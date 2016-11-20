cdef extern from "bno055_read_test.h":

    ctypedef struct Point3D:
        pass

    int run_serial_read_test(int num_trials)
