cimport cbno055_read_test

def run_serial_read_test(int num_trials):
  cdef int ret  
  ret = cbno055_read_test.run_serial_read_test(num_trials)
