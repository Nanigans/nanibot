cdef extern from "bno055_read_test.h":

    ctypedef struct Point3D:
        pass

    int run_serial_read_test(int num_trials)
    
    int run_serial_read_test_2(int num_trials, int sample_interval_usec, int max_read_retries)
