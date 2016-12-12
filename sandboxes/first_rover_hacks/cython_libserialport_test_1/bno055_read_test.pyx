cimport cbno055_read_test

def run_serial_read_test(int num_trials):
  cdef int ret  
  ret = cbno055_read_test.run_serial_read_test(num_trials)

def run_serial_read_test_2(int num_trials, int sample_interval_usec, int max_read_retries):
  cdef int ret  
  ret = cbno055_read_test.run_serial_read_test_2(num_trials, sample_interval_usec, max_read_retries)
