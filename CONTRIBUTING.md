# How to Contribute

## Requirements

* Python 3
* Anaconda
* Install the packages listed in requirements.txt

This repository does not contain the netCDF files that drive this tool. Please contact the developer to obtain a
download and place the data in the `data` directory.

## Running the program (development)

To start the program, run `main.py`. All code is in the `source` directory, and all data is in the `data` directory.

## Building from source

PyInstaller is used to package this tool into an executable. To build, run `build.bat` (Windows only). If you are 
running Linux you should be able to create your own shell script or run the build command on the command line. Be aware 
that PyInstaller is not a cross-compiler - to make a Windows program you must build on a Windows machine; to make a
Linux program you build in Linux, etc.

The executable ExtremeEvents.exe will appear in the `dist` directory. It has a significant startup delay due to the 
250MB+ of data that needs to be unpacked on startup.

If you experience errors while building, and you didn't change any code, submit the error as an issue on the 
[GitHub Repository](https://github.com/Laura-Guillory/FWFA_Extreme_Events_Tool).

If you experience errors, and you changed the code, try reviewing PyInstaller documentation such as the 
[manual](https://pyinstaller.readthedocs.io/en/stable/usage.html) or the 
[When Things Go Wrong guided troubleshooter](https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html)