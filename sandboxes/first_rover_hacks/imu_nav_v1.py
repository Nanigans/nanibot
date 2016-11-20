try:
  import pandas as pd
except:
  pass
import csv 
import json
import logging
import sys
import time
import threading
import gopigo
from Adafruit_BNO055 import BNO055

SINGLE_THREADED = True
WARMUP_SLEEP_SEC = 2.0
MAIN_LOOP_INTERVAL_SEC = 0.1
MAX_PROGRAM_DURATION_SEC = 5.0
DEFAULT_MOTOR_SPEED = 100
BNO_UPDATE_FREQUENCY_HZ = 100.0
INCREASE_SPEED_INTERVAL_SEC = 1.0
MAX_SPEED_INCREASES = 10.0

DO_CALIBRATION = False
CALIBRATION_FILE='calibration.json'

DATA_FILE = 'sensor_data.csv'


# Create and configure the BNO sensor connection.
# Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)

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

# Global state to keep track of the latest readings from the BNO055 sensor.
# This will be accessed from multiple threads so care needs to be taken to
# protect access with a lock (or else inconsistent/partial results might be read).
# A condition object is used both as a lock for safe access across threads, and
# to notify threads that the BNO state has changed.
bno_data = {}
bno_changed = threading.Condition()

# Background thread to read BNO sensor data.  Will be created right before
# the first request is served (see start_bno_thread below).
bno_thread = None

def read_bno():
    """Function to read the BNO sensor and update the bno_data object with the
    latest BNO orientation, etc. state.  Must be run in its own thread because
    it will never return!
    """
    while True:
        # Grab new BNO sensor readings.
        #temp = bno.read_temp()
        linX, linY, linZ = bno.read_linear_acceleration()
        heading, roll, pitch = bno.read_euler()
        x, y, z, w = bno.read_quaternion()
        sys, gyro, accel, mag = bno.get_calibration_status()
        status, self_test, error = bno.get_system_status(run_self_test=False)
        if error != 0:
            print 'Error! Value: {0}'.format(error)
        # Capture the lock on the bno_changed condition so the bno_data shared
        # state can be updated.
        with bno_changed:
            bno_data['time'] = time.time()
            bno_data['euler'] = (heading, roll, pitch)
            bno_data['temp'] = temp
            bno_data['linear'] = (linX, linY, linZ)
            bno_data['quaternion'] = (x, y, z, w)
            bno_data['calibration'] = (sys, gyro, accel, mag)
            # Notify any waiting threads that the BNO state has been updated.
            bno_changed.notifyAll()
        # Sleep until the next reading.
        time.sleep(1.0/BNO_UPDATE_FREQUENCY_HZ)

def read_bno_single_threaded():
    """Function to read the BNO sensor and update the bno_data object with the
    latest BNO orientation, etc. state.  Must be run in its own thread because
    it will never return!
    """
    # Grab new BNO sensor readings.
    linX, linY, linZ = bno.read_linear_acceleration()
    status, self_test, error = bno.get_system_status(run_self_test=False)
    if error != 0:
      print 'Error! Value: {0}'.format(error)
    # Capture the lock on the bno_changed condition so the bno_data shared
    # state can be updated.
    with bno_changed:
      bno_data['time'] = time.time()
      bno_data['linear'] = (linX, linY, linZ)
      # Notify any waiting threads that the BNO state has been updated.
      bno_changed.notifyAll()

def start_bno_thread():
    # Start the BNO thread right before the first request is served.  This is
    # necessary because in debug mode flask will start multiple main threads so
    # this is the only spot to put code that can only run once after starting.
    # See this SO question for more context:
    #   http://stackoverflow.com/questions/24617795/starting-thread-while-running-flask-with-debug
    global bno_thread
    # Initialize BNO055 sensor.
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055!')
    bno.set_axis_remap(**BNO_AXIS_REMAP)
    # Kick off BNO055 reading thread.
    bno_thread = threading.Thread(target=read_bno)
    bno_thread.daemon = True  # Don't let the BNO reading thread block exiting.
    bno_thread.start()

def start_bno_single_threaded():
  if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055!')
  bno.set_axis_remap(**BNO_AXIS_REMAP)

def load_calibration():
    # Load calibration from disk.
    with open(CALIBRATION_FILE, 'r') as cal_file:
        data = json.load(cal_file)
    # Grab the lock on BNO sensor access to serial access to the sensor.
    with bno_changed:
        bno.set_calibration(data)
    return 'OK'

class DataRecorder:

  def __init__(self,output_file_name):
    self._outputFileName = output_file_name
    self._dataRecord = {}

  def captureData(self,data,record_name='default'):
    try:
      if record_name not in self._dataRecord:
        self._dataRecord[record_name] = pd.DataFrame(columns=data.keys())
      self._dataRecord[record_name] = self._dataRecord[record_name].append(data,ignore_index=True)
    except:
      if record_name not in self._dataRecord:
        self._dataRecord[record_name] = {'columns':data.keys(),'data_rows':[]}
      self._dataRecord[record_name]['data_rows'].append(['{v:0.5f}'.format(v=v) for v in data.values()])

  def getDataRecord(self,record_name='default'):
    return self._dataRecord[record_name]

  def saveDataRecord(self,record_name='default'):
    self._dataRecord[record_name].to_csv(self._outputFileName,index=False)

class MotorController:

  #MAX_UPDATE_TIME_DIFF = 0.25
  #TIME_BETWEEN_SERVO_SETTING_UPDATES = 1.0
  #JOYSTICK_DEAD_ZONE = 0.1
  #MOTION_COMMAND_TIMEOUT = 2.0 # If no commands for the motors are recieved in this time then
                               # the motors (drive and servo) are set to zero speed

    
  #-----------------------------------------------------------------------------------------------
  def __init__(self,default_motor_speed=50):
    gopigo.set_speed(default_motor_speed)
    gopigo.stop()
    #gopigo.fwd()

    self.lastServoSettingsSendTime = 0.0
    self.lastUpdateTime = 0.0
    self.lastMotionCommandTime = time.time()

  def drive(self):
    gopigo.fwd()

  def stop(self):
    gopigo.stop()


class StateEstimator:

  def __init__(self,single_threaded=True):

    # Enable verbose debug logging if -v is passed as a parameter.
    if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
      logging.basicConfig(level=logging.DEBUG)

    self._single_threaded = single_threaded

    self._last_update_time = time.time()
    self._last_acceleration = (0,0,0)
    self._last_velocity = (0,0,0)
    self._last_position = (0,0,0)

  def _updateStateEstimates(self):

    if self._single_threaded:
      read_bno_single_threaded()
      t = bno_data['time']
      x, y, z = bno_data['linear']
    else:
      # Capture the bno_changed condition lock and then wait for it to notify
      # a new reading is available.
      with bno_changed:
        bno_changed.wait()
        # A new reading is available!  Grab the reading value and then give
        # up the lock.
        t = bno_data['time']
        x, y, z = bno_data['linear']
        #heading, roll, pitch = bno_data['euler']
        #temp = bno_data['temp']
        #x, y, z, w = bno_data['quaternion']
        #sys, gyro, accel, mag = bno_data['calibration']

    # - Compute new state
    dT = t - self._last_update_time
    velocities = (self._last_velocity[0] + dT * x, self._last_velocity[1] + dT * y, self._last_velocity[2] + dT * z)
    positions = (self._last_position[0] + 0.5 * dT * (velocities[0] + self._last_velocity[0]), 
                 self._last_position[1] + 0.5 * dT * (velocities[1] + self._last_velocity[1]),
                 self._last_position[2] + 0.5 * dT * (velocities[2] + self._last_velocity[2]))
    
    # - Update state estimates
    self._last_update_time = t
    self._last_acceleration = (x,y,z)
    self._last_velocity = velocities
    self._last_position = positions

  def getCurrentState(self):
    self._updateStateEstimates()

    return {
      'position':self._last_position,
      'velocity':self._last_velocity,
      'acceleration':self._last_acceleration,
      't':self._last_update_time}

if __name__ == '__main__':

  try:
    if SINGLE_THREADED:
      start_bno_single_threaded()
    else:
      start_bno_thread()
    if DO_CALIBRATION:
      load_calibration()

    stateEstimator = StateEstimator(single_threaded=SINGLE_THREADED)
    motorController = MotorController(DEFAULT_MOTOR_SPEED)

    dataRecorder = DataRecorder(DATA_FILE)

    start_time = time.time()
    last_speed_increase = start_time
    num_speed_increases = 0
    driving = False
 
    while True:
      current_time = time.time()
      program_duration = current_time - start_time
      if program_duration > WARMUP_SLEEP_SEC and not driving:
        driving = True
        motorController.drive()        
      if program_duration > MAX_PROGRAM_DURATION_SEC:
        print "Shutting down.  Program duration {dur} (sec) exceeds max duration of {max_dur} (sec)".format(dur=program_duration,max_dur=MAX_PROGRAM_DURATION_SEC)
        break

      if (current_time - last_speed_increase > INCREASE_SPEED_INTERVAL_SEC) and (num_speed_increases < MAX_SPEED_INCREASES):
        gopigo.increase_speed()
        num_speed_increases += 1
        last_speed_increase = current_time
        print '--- increasing speed ---'

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
    gopigo.stop()
    time.sleep(2)

try:
  dataRecorder.saveDataRecord()
except:
  record_data = dataRecorder.getDataRecord()
  print ','.join(record_data['columns'])
  for row_data in record_data['data_rows']:
    print '[{data}],'.format(data=','.join(row_data))

