call activate "Extreme Events Tool"
pyinstaller main.py --name ExtremeEvents --onedir -y -w ^
--add-data "C:\ProgramData\Anaconda3\envs\Extreme Events Tool\Lib\site-packages\dask\dask.yaml;./dask" ^
--add-data "C:\ProgramData\Anaconda3\envs\Extreme Events Tool\Lib\site-packages\distributed\distributed.yaml;./distributed" ^
--add-data "data/locations.txt;./data" ^
--add-data "data/windspeed.nc;./data" ^
--add-data "data/precipitation.nc;./data" ^
--add-data "data/minimum_temperature.nc;./data" ^
--add-data "data/maximum_temperature.nc;./data"
conda deactivate