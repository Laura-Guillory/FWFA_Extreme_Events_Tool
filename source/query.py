import xarray
import numpy
import pandas
import sys
import os
import threading


class ThreadedQuery(threading.Thread):
    def __init__(self, queue, parameters):
        threading.Thread.__init__(self)
        self.queue = queue
        self.parameters = parameters

    # What this program actually does. Takes parameters specified by the user and searches data to find instances that
    # fit those parameters. Expects parameters in the following structure:
    # parameters: {}
    #   temperature: {}
    #       condition: {} (Must be 'Any', 'Higher Than', or 'Lower Than')
    #       value: float
    #   precipitation: {}
    #       condition: {} (Must be 'Any', 'Higher Than', or 'Lower Than')
    #       value: float
    #   wind: {}
    #       condition: {} (Must be 'Any', 'Higher Than', or 'Lower Than')
    #       value: float
    #   months: [] (True or False)
    # station: int
    # consecutive_days: int
    #
    # Should return results in the following structure:
    # results: []
    #   (start_date: Pandas Timeframe, end_date: Pandas Timeframe) <- tuple
    def run(self):
        try:
            # Load data
            data = xarray.open_mfdataset([
                resource_path('data/minimum_temperature.nc'),
                resource_path('data/maximum_temperature.nc'),
                resource_path('data/precipitation.nc'),
                resource_path('data/windspeed.nc')
            ], join='override')

            # Narrow down data to parameters
            # Station
            data = data.where(data.region == self.parameters['station'], drop=True)

            # Months
            filter_months = not all(self.parameters['months'])
            month_mask = None
            if filter_months:
                months_in_filter = []
                for i, month in enumerate(self.parameters['months']):
                    if month:
                        months_in_filter.append(i+1)
                data.load()
                month_mask = ~numpy.in1d(data['time.month'], months_in_filter)
                data['precipitation'][:, month_mask] = numpy.nan
                data['windspeed'][:, month_mask] = numpy.nan
                data['minimum_temperature'][:, month_mask] = numpy.nan
                data['maximum_temperature'][:, month_mask] = numpy.nan

            # Temperature
            arrays_to_combine = []
            if self.parameters['temperature']['condition'] == 'Lower Than':
                arrays_to_combine.append(
                    data.minimum_temperature.where(data.minimum_temperature < self.parameters['temperature']['value'])
                )
            elif self.parameters['temperature']['condition'] == 'Higher Than':
                arrays_to_combine.append(data.maximum_temperature.where(
                    data.maximum_temperature > self.parameters['temperature']['value']
                ))

            # Precipitation
            # Is accumulation instead of every day. Calculate rolling accumulation for the given duration
            data['precipitation'] = data.precipitation.rolling(
                time=self.parameters['consecutive_days'], min_periods=1
            ).sum()
            precipitation_bool = None
            if self.parameters['precipitation']['condition'] == 'Lower Than':
                precipitation_bool = ~numpy.isnan(
                    data.precipitation.where(data.precipitation < self.parameters['precipitation']['value'])[0].values
                )
            elif self.parameters['precipitation']['condition'] == 'Higher Than':
                precipitation_bool = ~numpy.isnan(
                    data.precipitation.where(data.precipitation > self.parameters['precipitation']['value'])[0].values
                )

            # Wind
            if self.parameters['wind']['condition'] == 'Lower Than':
                arrays_to_combine.append(data.windspeed.where(data.windspeed < self.parameters['wind']['value']))
            elif self.parameters['wind']['condition'] == 'Higher Than':
                arrays_to_combine.append(data.windspeed.where(data.windspeed > self.parameters['wind']['value']))

            # Combine results
            combined_data = None
            if len(arrays_to_combine) > 0:
                combined_data = ~numpy.isnan(arrays_to_combine[0].values[0])
                for i in range(1, len(arrays_to_combine)):
                    combined_data = numpy.logical_and(combined_data, ~numpy.isnan(arrays_to_combine[i].values[0]))

            # Get the rest of the data required and close files
            time_dimension = data.time.size
            data.close()

            # Count consecutive days and record instances
            results = []
            i_consecutive = 0
            query_precipitation = False if self.parameters['precipitation']['condition'] == 'Any' else True
            query_wind = False if self.parameters['wind']['condition'] == 'Any' else True
            query_temperature = False if self.parameters['temperature']['condition'] == 'Any' else True

            # These could be combined to reduce repeated code, but separating them eliminates thousands of unnecessary
            # checks, speeding things up. Readability is compromised in favour of performance.
            # If only temperature and wind
            if not query_precipitation:
                for i_date in range(0, data.time.size):
                    if combined_data[i_date]:
                        i_consecutive += 1
                    elif i_consecutive >= self.parameters['consecutive_days']:
                        start_date = data.time.values[i_date - i_consecutive]
                        start_date = pandas.to_datetime(start_date)
                        end_date = data.time.values[i_date - 1]
                        end_date = pandas.to_datetime(end_date)
                        results.append((start_date, end_date))
                        i_consecutive = 0
                    else:
                        i_consecutive = 0
                if i_consecutive >= self.parameters['consecutive_days']:
                    start_date = data.time.values[data.time.size - i_consecutive]
                    start_date = pandas.to_datetime(start_date)
                    end_date = data.time.values[data.time.size - 1]
                    end_date = pandas.to_datetime(end_date)
                    results.append((start_date, end_date))
            # If only precipitation
            elif not query_wind and not query_temperature:
                i_date = 0
                while i_date < data.time.size:
                    if precipitation_bool[i_date]:
                        start_i = i_date - self.parameters['consecutive_days'] + 1
                        if start_i < 0:
                            start_i = 0
                        if not filter_months or not(month_mask[start_i] or month_mask[i_date]):
                            start_date = pandas.to_datetime(data.time.values[start_i])
                            end_date = pandas.to_datetime(data.time.values[i_date])
                            results.append((start_date, end_date))
                            i_date = i_date + self.parameters['consecutive_days']
                    i_date += 1
            # If combination of precipitation and other conditions
            elif query_precipitation and (query_wind or query_temperature):
                for i_date in range(0, time_dimension):
                    if combined_data[i_date]:
                        i_consecutive += 1
                        if i_consecutive >= self.parameters['consecutive_days']:
                            # Check precipitation requirement - if not met, move window along one space
                            if not precipitation_bool[i_date]:
                                i_consecutive -= 1
                                continue
                            start_date = pandas.to_datetime(data.time.values[i_date - i_consecutive] + 1)
                            end_date = pandas.to_datetime(data.time.values[i_date])
                            results.append((start_date, end_date))
                            i_consecutive = 0
                    else:
                        i_consecutive = 0
            else:
                self.queue.put((Exception, None))
                return
        except MemoryError:
            self.queue.put((MemoryError, None))
            return
        except:
            self.queue.put((Exception, None))
            return
        self.queue.put((None, results))


# For populating the station dropdown in the GUI
def get_all_stations():
    with open(resource_path('data/locations.txt'), 'r') as file:
        stations = file.read().split('\n')
    return stations


# Helps the program find where files are when packaged into an application by PyInstaller
# Works for dev environment as well
# Returns the absolute path
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)