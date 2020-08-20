# How to use

## Requirements

* Windows

## Running the program

To run the program, locate _ExtremeEvents.exe in the program files and double click. You may find it helpful to create 
a shortcut (right click _ExtremeEvents.exe -> Create Shortcut; then move the shortcut to your desktop)

## Using the program

The FWFA Extreme Events tool reviews historical records and report instances of extreme weather events. It allows the 
user to set desired thresholds for temperature, precipitation, and windspeed, and receive a report on the dates that
these conditions have occurred in the past.

The options available are explained below.

### Select Location

Here the user selects the location where they would like to examine historical records. The dropdown menu offers a 
choice of 555 stations around Australia.

### Select Conditions

Here the user selects the desired thresholds for each climate variable (temperature, precipitation, and windspeed). The 
user can set thresholds for just one of the climate variables, two, or all three. 

For each climate variable, the user can choose between "Higher Than", "Lower Than", or "Any". 

* Higher Than - the program will search for results where the climate variable was higher than the value in the box to 
the right
* Lower Than - the program will search for results where the climate variable was lower than the value in the box to 
the right
* Any - this climate variable will be ignored and will not impact results

Selecting "Any" for all three climate variables is equivalent to not setting any threshold at all, and is not allowed. 
The user must select "Higher Than" or "Lower Than" for at least one climate variable to do a valid search.

Below are some examples of search parameters; it is encouraged to try them out.

--Example 1--

Temperature:    Higher Than     40 °C 
Precipitation:  Any             
Windspeed:      Any

In this example, the program will search for instances where the temperature over 40 °C. It will not matter whether it 
rained or what the windspeed was that day.

--Example 2--

Temperature:    Lower Than      5 °C 
Precipitation:  Higher Than     5 mm
Windspeed:      Higher Than     5m/s

In this example, the program will search for instances where the temperature was under 5 °C, it was rainy and windy. 
Searches like this can be useful when examining windchill.

### Select Duration

Here the user selects the minimum number of consecutive days necessary for the event to be included in the results. The
default is 1. In general extreme events that last longer are more severe; for example, an extremely hot day can be 
manageable, but a heatwave lasting several weeks is a serious event.

### Getting results

To search using the thresholds that you have selected, click "Query". After a loading time, your results should appear 
in the panel to the right.

Results will consist of the first and last date where the event occurred, with one entry per event.

Consecutive days that fit the search criteria will be considered to be one "event" spanning multiple days, even if the 
user specified a duration of one day. This is intended to simplify results. 

If there are no results, try widening your search criteria or checking that the thresholds you have set are
appropriate for the region that you have specified.

## Data sources

This program requires accurate data for daily windspeed, precipitation, minimum temperature and maximum temperature,
which is packaged with the application in netCDF format.

Precipitation and temperature data is sourced from 
[LongPaddock's SILO database](https://www.longpaddock.qld.gov.au/silo/), which uses mathematical interpolation 
techniques to infill gaps in time series.

Wind data is sourced from 
[NOAA-CIRES-DOE Twentieth Century Reanalysis](https://psl.noaa.gov/data/gridded/data.20thC_ReanV3.monolevel.html). Wind
data was obtained as eastward and northward components, which was used to calculate the overall windspeed that is used
in this program. 

The date range for the data used in this program is 1 January 1889 to 31 December 2015.