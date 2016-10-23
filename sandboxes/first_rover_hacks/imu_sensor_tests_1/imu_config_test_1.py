"""
This script was used to test basic I/O configuration and performance of the Adafruit BNO055
Lessons learned:
- If the data register for the magnetometer is read more frequently than the configured Data Output Rate (see Table 3-10 in BNO055 data sheet), the data values will remain unchanged until the next internal update.  Note: the linear acceleration data register (in fusion mode) updates more frequently than the magnetometer-only data register.
- The data register for the magnetometer does not persist identical values if sampled faster than the configured bandwidth (see Table 3-9 in BNO055 data sheet).  This was test in NDOF mode (fusion), AMG mode (non-fusion), and GYROONLY mode (non-fusion) - note: the test was limited by the effective max sampling rate in the python serial implementation.  There are no configuration options in the data sheet for Data Output Rate for the accelerometer or gyroscope.  There are, however, configurable bandwidth options.  This is discussed with some clarity here: https://forum.pjrc.com/threads/29541-BNO055-Gyro-Update-Rate
- The basic python serial implementation in the included BNO055 python module seems to be limited to sampling measurements at an average interval of 10-40 ms.  Time per sample appeared to be about twice as long in non-fusion modes than in NDOF Fusion mode.
- It seems that the configuration of sensor options in BNO055 can only be changed when the chip is put back into CONFIG MODE (see Table 3-5 in BNO055 data sheet)
- Among dozens of times running the script, the following runtime exception was raised (while calling the begin() method on an instance of BNO055) about 1 out of 10 occassions: RuntimeError: Register read error: 0xee06

BNO055 data sheet: https://cdn-shop.adafruit.com/datasheets/BST_BNO055_DS000_12.pdf
"""

from Adafruit_BNO055 import BNO055
import time

NUM_MEASUREMENTS = 40

def start_bno(mode=None):
  if mode is None:
    if not bno.begin():
      raise RuntimeError('Failed to initialize BNO055!')
  else:
    print 'starting in mode: ',mode
    if not bno.begin(mode=mode):
      raise RuntimeError('Failed to initialize BNO055!')

def get_binary_word_str(word, bit_width=8):
  return ''.join([str(word >> i & 0X1) for i in range(bit_width-1,-1,-1)])

def print_measurements(lin_accel,mag,gyro,accel):
  print '({0:.3f}, {1:.3f}, {2:.3f})\t({3:.3f}, {4:.3f}, {5:.3f})\t({6:.3f}, {7:.3f}, {8:.3f})\t({9:.3f}, {10:.3f}, {11:.3f})'.format(
    lin_accel[0],
    lin_accel[1],
    lin_accel[2],
    mag[0],
    mag[1],
    mag[2],
    gyro[0],
    gyro[1],
    gyro[2],
    accel[0],
    accel[1],
    accel[2])

def update_gyro_config(bno,page=0,bandwidth_code=0B111,range_code=0B000,verbose=False):

  # - Switch to config mode
  bno._config_mode()

  # Select page 1 for gyro configuration
  bno._write_byte(BNO055.BNO055_PAGE_ID_ADDR, page)
  time.sleep(0.05)

  gyro_config_address = 0XA
  config_value = ((bandwidth_code << 3) | range_code) & 0X3F

  if verbose:
    prior_value = bno._read_byte(gyro_config_address)
    time.sleep(0.05)
    print 'setting gyro config: {0} - {1!s}'.format(config_value,get_binary_word_str(config_value))
  
  # Update gyro settings
  bno._write_byte(gyro_config_address,config_value)
  time.sleep(0.05)
  
  if verbose:
    confirmation = bno._read_byte(gyro_config_address)
    print 'confirmation - from: {0} to: {1}'.format(prior_value & 0X3F,confirmation & 0X3F)
    print 'page ID: {}'.format(bno._read_byte(BNO055.BNO055_PAGE_ID_ADDR))

  # Select page 0 since done with gyro configuration
  bno._write_byte(BNO055.BNO055_PAGE_ID_ADDR, 0)
   
  # - Back into operation mode
  bno._operation_mode()
  
  time.sleep(0.65)

if __name__ == '__main__':

  print 'About to start BNO'

  start_time = time.time()

  # Create and configure the BNO sensor connection.
  # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
  bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
  #bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18, serial_timeout_sec=None)

  done_creating_bno_time = time.time()

  # -- Reset bno and set to desired mode --
  mode = BNO055.OPERATION_MODE_AMG
  #mode = BNO055.OPERATION_MODE_GYRONLY
  start_bno(mode)
  #start_bno()
  print 'Done starting BNO'

  done_starting_bno_time = time.time()

  # 12 Hz Gyro BW
  update_gyro_config(bno,page=1,bandwidth_code=0B101,range_code=0B000,verbose=True)

  print 'Linear Acceleration\tMagnetometer\t\tGyroscope\t\tAccerlation'
  lin_accel = (0,0,0)
  mag = (0,0,0)
  gyro = (0,0,0)
  accel = (0,0,0)
  for i in range(NUM_MEASUREMENTS):

      lin_accel = bno.read_linear_acceleration()
      mag = bno.read_magnetometer()
      gyro = bno.read_gyroscope()
      #accel = bno.read_accelerometer()

      print_measurements(lin_accel,mag,gyro,accel)

  done_with_measurements_time = time.time()

  print '\ntime to create bno: {0}\ntime to start bno: {1}\ntime per measurement ({2}): {3}'.format(
      done_creating_bno_time - start_time,
      done_starting_bno_time - done_creating_bno_time,
      NUM_MEASUREMENTS,
      (done_with_measurements_time - done_starting_bno_time)/NUM_MEASUREMENTS)

