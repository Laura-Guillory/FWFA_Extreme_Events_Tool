call activate "Extreme Events Tool"
pyinstaller main.py --name ExtremeEvents --onefile -y -w ^
--add-data "C:\ProgramData\Anaconda3\envs\Extreme Events Tool\Lib\site-packages\dask\dask.yaml;./dask" ^
--add-data "C:\ProgramData\Anaconda3\envs\Extreme Events Tool\Lib\site-packages\distributed\distributed.yaml;./distributed" ^
--add-data "D:\Documents\My_Actual_Files\USQ_Work\FWFA\HEEAT\venv\Lib\site-packages\xarray-999-py3.8.egg\xarray\static;./xarray/static" ^
--add-data "data/locations.txt;./data" ^
--add-data "data/windspeed.nc;./data" ^
--add-data "data/precipitation.nc;./data" ^
--add-data "data/minimum_temperature.nc;./data" ^
--add-data "data/maximum_temperature.nc;./data"
conda deactivate