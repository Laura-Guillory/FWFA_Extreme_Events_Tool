import xarray
import numpy
import pandas


def get_all_stations():
    with open('data/locations.txt', 'r') as file:
        stations = file.read().split('\n')
    return stations


def make_query(parameters):
    # Load data
    data = xarray.open_mfdataset([
        'data/minimum_temperature.nc',
        'data/maximum_temperature.nc',
        'data/precipitation.nc',
        'data/windspeed.nc'
    ], join='override')

    # Narrow down data to parameters
    # Station
    data = data.where(data.region == parameters['station'], drop=True)

    # Temperature
    arrays_to_combine = []
    if parameters['temperature']['condition'] == 'Lower Than':
        arrays_to_combine.append(
            data.minimum_temperature.where(data.minimum_temperature < parameters['temperature']['value'])
        )
    elif parameters['temperature']['condition'] == 'Higher Than':
        arrays_to_combine.append(data.maximum_temperature.where(
            data.maximum_temperature > parameters['temperature']['value']
        ))

    # Precipitation
    if parameters['precipitation']['condition'] == 'Lower Than':
        arrays_to_combine.append(data.precipitation.where(data.precipitation < parameters['precipitation']['value']))
    elif parameters['precipitation']['condition'] == 'Higher Than':
        arrays_to_combine.append(data.precipitation.where(data.precipitation > parameters['precipitation']['value']))

    # Wind
    if parameters['wind']['condition'] == 'Lower Than':
        arrays_to_combine.append(data.windspeed.where(data.windspeed < parameters['wind']['value']))
    elif parameters['wind']['condition'] == 'Higher Than':
        arrays_to_combine.append(data.windspeed.where(data.windspeed > parameters['wind']['value']))

    # Combine results
    combined_data = ~numpy.isnan(arrays_to_combine[0].values[0])
    for i in range(1, len(arrays_to_combine)):
        combined_data = numpy.logical_and(combined_data, ~numpy.isnan(arrays_to_combine[i].values[0]))

    # Count consecutive days and record instances
    results = []
    i_consecutive = 0
    for i_date in range(0, data.time.size):
        if not combined_data[i_date]:
            if i_consecutive >= parameters['consecutive_days']:
                start_date = data.time.values[i_date-i_consecutive]
                start_date = pandas.to_datetime(start_date)
                end_date = data.time.values[i_date-1]
                end_date = pandas.to_datetime(end_date)
                results.append((start_date, end_date))
            i_consecutive = 0
        else:
            i_consecutive += 1
    if i_consecutive >= parameters['consecutive_days']:
        start_date = data.time.values[data.time.size-i_consecutive]
        start_date = pandas.to_datetime(start_date)
        end_date = data.time.values[data.time.size-1]
        end_date = pandas.to_datetime(end_date)
        results.append((start_date, end_date))
    return results
