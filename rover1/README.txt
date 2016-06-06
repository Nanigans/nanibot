This is the project root of the first Nanigans rover project.  All application code is contained below this directory.

The following environment and dependencies are assumed by the application code:

Main CPU: Raspberry Pi 2
- Raspbian OS
- Python 2
-- virtualenv
-- virtualenvwrapper
-- Numpy
-- Pandas
-- SciPy
-- pigpio (see further explanation below)
-- smbus
-- Adafruit_BNO055 (BNO055)
- Adafruit_Python_BNO055 library and python interface
-- https://github.com/adafruit/Adafruit_Python_BNO055.git  
- pigpio library and interfaces
-- http://abyz.co.uk/rpi/pigpio/index.html

Motor Driver: Dimension Engineering Sabertooth 2x12

IMU Breakout Board: Adafruit BNO055 9-DOF Absolute Orientation IMU Fusion Breakout
