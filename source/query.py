import xarray
import numpy
import pandas
import sys
import os
import threading
import datetime


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
    # station: int
    # consecutive_days: int
    #
    # Should return results in the following structure:
    # results: []
    #   (start_date: Pandas Timeframe, end_date: Pandas Timeframe) <- tuple
    def run(self):
        start = datetime.datetime.now()
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
            if self.parameters['precipitation']['condition'] == 'Lower Than':
                precipitation_bool = data.precipitation.where(
                    data.precipitation < self.parameters['precipitation']['value']
                )
            elif self.parameters['precipitation']['condition'] == 'Higher Than':
                precipitation_bool = data.precipitation.where(
                    data.precipitation > self.parameters['precipitation']['value']
                )

            # Wind
            if self.parameters['wind']['condition'] == 'Lower Than':
                arrays_to_combine.append(data.windspeed.where(data.windspeed < self.parameters['wind']['value']))
            elif self.parameters['wind']['condition'] == 'Higher Than':
                arrays_to_combine.append(data.windspeed.where(data.windspeed > self.parameters['wind']['value']))

            # Combine results
            # TODO: FIX PRECIPITATION ONLY CALCULATION
            combined_data = ~numpy.isnan(arrays_to_combine[0].values[0])
            for i in range(1, len(arrays_to_combine)):
                combined_data = numpy.logical_and(combined_data, ~numpy.isnan(arrays_to_combine[i].values[0]))

            # Get the rest of the data required and close files
            time_dimension = data.time.size
            data.close()

            # Count consecutive days and record instances
            results = []
            i_consecutive = 0
            for i_date in range(0, time_dimension):
                print(combined_data[i_date])
                if combined_data[i_date]:
                    if not precipitation_bool[i_date + self.parameters['consecutive_days']]:
                        i_consecutive = 0
                        continue
                    i_consecutive += 1
                    if i_consecutive >= self.parameters['consecutive_days']:
                        start_date = pandas.to_datetime(data.time.values[i_date - i_consecutive])
                        end_date = pandas.to_datetime(data.time.values[i_date - 1])
                        results.append((start_date, end_date))
                        i_consecutive = 0
                else:
                    i_consecutive = 0
        except MemoryError:
            self.queue.put((MemoryError, None))
            return
        except:
            self.queue.put((Exception, None))
            return
        print(datetime.datetime.now() - start)
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
