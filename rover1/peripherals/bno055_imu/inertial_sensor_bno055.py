from Adafruit_BNO055 import BNO055
import time

class InertialSensorBNO055:

  _sensor = None

  def __init__(self,calibration_data=None,axis_remap=None):

    # Create and configure the BNO sensor connection.
    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
    self._sensor = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)

    if not self._sensor.begin():
      raise RuntimeError('Failed to initialize BNO055!')
    if axis_remap is not None:
      self._sensor.set_axis_remap(**axis_remap)
    if calibration_data is not None:
      self._sensor.set_calibration(calibration_data)

  def get_measurement(self):
    # Grab new BNO sensor readings.
    linX, linY, linZ = self._sensor.read_linear_acceleration()
    status, self_test, error = self._sensor.get_system_status(run_self_test=False)
    if error != 0:
      raise RuntimeError('Sensor error in BNO055')
    
    result = {}
    result['validity_time'] = time.time()
    result['acceleration_x'] = linX
    result['acceleration_y'] = linY
    result['acceleration_z'] = linZ
    
    return result

