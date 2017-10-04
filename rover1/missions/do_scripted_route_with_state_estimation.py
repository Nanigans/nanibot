"""
MIT License

Copyright (c) 2017 Nanigans

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

BNO055.py Absolute Orientation Sensor Python Library is copyright (c) 2015 Adafruit 
Industries and released under a MIT License.  See more details at:
  https://github.com/adafruit/Adafruit_Python_BNO055/blob/master/LICENSE


This mission drives the rover along a scripted route, periodically makes state estimates of the rover position, and logs data for offline analysis.

It makes a lot of assumptions about the hardware configuration of the rover.

Under normal, full battery conditions the rover requires freedom of motion in a rectangular box stretching from the front of the rover to 10 feet ahead of it and 3 feet to either side of its starting position.

usage:
sudo python do_scripted_route_with_state_estimation.py
"""

if __name__ == '__main__' and __package__ is None:
  from os import sys, path
  sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import time
import threading
import sys
import csv
import json

from Adafruit_BNO055 import BNO055
import peripherals.sabertooth.sabertooth_adapter as sabertooth_adapter
import peripherals.bno055_imu.inertial_sensor_bno055 as imu
import components.logging.data_recorder as data_recorder
import components.tracking.state_estimation as state_estimation
import components.driving.motor_control as motor_control

CALIBRATION_FILE='../peripherals/bno055_imu/calibration/calibration.json'
DATA_LOG_FILE='../log/data_dump_scripted_route_with_state_estimation.log'

DO_CALIBRATION = False
SINGLE_THREADED = True
WARMUP_SLEEP_SEC = 3.0
MAIN_LOOP_INTERVAL_SEC = 0.1
MAX_PROGRAM_DURATION_SEC = 10.0
DEFAULT_MOTOR_SPEED = 10
BNO_UPDATE_FREQUENCY_HZ = 100.0
INCREASE_SPEED_INTERVAL_SEC = 3.0
MAX_SPEED_INCREASES = 10.0

# BNO sensor axes remap values.  These are the parameters to the BNO.set_axis_remap
# function.  Don't change these without consulting section 3.4 of the datasheet.
# The default axes mapping below assumes the Adafruit BNO055 breakout is flat on
# a table with the row of SDA, SCL, GND, VIN, etc pins facing away from you.
BNO_AXIS_REMAP = { 'x': BNO055.AXIS_REMAP_X,
                   'y': BNO055.AXIS_REMAP_Z,
                   'z': BNO055.AXIS_REMAP_Y,
                   'x_sign': BNO055.AXIS_REMAP_POSITIVE,
                   'y_sign': BNO055.AXIS_REMAP_POSITIVE,
                   'z_sign': BNO055.AXIS_REMAP_NEGATIVE }

if __name__ == '__main__':

  try:
   
    # DEBUG
    print "reached main method"

    start_time_tag = strftime("%Y%m%d_%H%M%S",time.gmtime())
    start_time = time.time()

    # Load calibration from disk.
    with open(CALIBRATION_FILE, 'r') as cal_file:
      cal_data = json.load(cal_file)

    motorControllerAdapter = sabertooth_adapter.SabertoothPacketizedAdapterGPIO() 
    motorController = motor_control.MotorController(motorControllerAdapter)
    imuSensor = imu.InertialSensorBNO055(
      calibration_data=cal_data,
      axis_remap=BNO_AXIS_REMAP)
    stateEstimator = state_estimation.StateEstimator(sensor=imuSensor)
    
    dataRecorder = data_recorder.DataRecorder(DATA_LOG_FILE+'_'+start_time_tag)

    last_speed_increase = start_time
    num_speed_increases = 0
    driving = False

    while True:
      current_time = time.time()
      program_duration = current_time - start_time
      if program_duration > WARMUP_SLEEP_SEC and not driving:
        driving = True
        print "starting to drive.  Look out!"
        # Start driving forward at preset power
        motorController.goForward(DEFAULT_MOTOR_SPEED)
        motorController.goStraight()
      if program_duration > MAX_PROGRAM_DURATION_SEC:
        print "Shutting down.  Program duration {dur} (sec) exceeds max duration of {max_dur} (sec)".format(dur=program_duration,max_dur=MAX_PROGRAM_DURATION_SEC)
        break


      if (current_time - last_speed_increase >= INCREASE_SPEED_INTERVAL_SEC) and (num_speed_increases < MAX_SPEED_INCREASES):
        # Increase speed 5%
        motorController.adjustFwdBwdSetting(5)
        num_speed_increases += 1
        print "--- increasing speed, since it's been {} seconds ---".format(current_time - last_speed_increase)
        last_speed_increase = current_time

      state_estimates = stateEstimator.getCurrentState()
      print "Acceleration: ({accel_x},{accel_y},{accel_z}) - Position: ({x},{y},{z}) - program time: {t} (sec)".format(
        accel_x=state_estimates['acceleration'][0],
        accel_y=state_estimates['acceleration'][1],
        accel_z=state_estimates['acceleration'][2],
        x=state_estimates['position'][0],
        y=state_estimates['position'][1],
        z=state_estimates['position'][2],
        t=state_estimates['t'] - start_time)

      dataRecorder.captureData(
        {'time':state_estimates['t'] - start_time,
         'position_x':state_estimates['position'][0],
         'position_y':state_estimates['position'][1],
         'position_z':state_estimates['position'][2],
         'velocity_x':state_estimates['velocity'][0],
         'velocity_y':state_estimates['velocity'][1],
         'velocity_z':state_estimates['velocity'][2],
         'acceleration_x':state_estimates['acceleration'][0],
         'acceleration_y':state_estimates['acceleration'][1],
         'acceleration_z':state_estimates['acceleration'][2],
        })

      time.sleep(MAIN_LOOP_INTERVAL_SEC)
  finally:
    motorControllerAdapter.stop()
    time.sleep(2)

try:
  dataRecorder.saveDataRecord()
except:
  record_data = dataRecorder.getDataRecord()
  print ','.join(record_data['columns'])
  for row_data in record_data['data_rows']:
    print '[{data}],'.format(data=','.join(row_data))
