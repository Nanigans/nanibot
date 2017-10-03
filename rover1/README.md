# Description
This is the project root of the first Nanigans rover project.  All application code is contained below this directory.
## Code organization
### components
This is the top level directory for all device-indepenent software components that work together to help the rover perform various tasks, such as:
* motor control
* navigation
* image processing
### missions
This directory contains main executable programs that accomplish specific tasks or missions.  Only one mission program should be executed at a time.  The launched mission program will launch all subprocesses and threads it requires to accomplish its task. 

E.g., Running simple motor driver test with do_simple_scripted_route.py
1. rover1/missions $ "workon rover1" (activate virtual environment where all necessary packages are installed)
2. power on moter controller (cycle kill switch if it was already on)
3. rover1/missions $ "sudo python do_simple_scripted_route.py" (execute mission program)
### peripherals
This directory contains low level code that abstracts away the particulars of various peripheral devices connected to the CPU
# Requirements
The following environment and dependencies are assumed by the application code:

Main CPU: Raspberry Pi 2
* Raspbian OS
* Python 2
  * virtualenv
  * virtualenvwrapper
  * Numpy
  * Pandas
  * SciPy
  * pigpio (see further explanation below)
  * smbus
  * Adafruit_BNO055 (BNO055)
* Adafruit_Python_BNO055 library and python interface
  * https://github.com/adafruit/Adafruit_Python_BNO055.git  
* pigpio library and interfaces
  * http://abyz.co.uk/rpi/pigpio/index.html

Motor Driver: Dimension Engineering Sabertooth 2x12

IMU Breakout Board: Adafruit BNO055 9-DOF Absolute Orientation IMU Fusion Breakout
