from loopingfun import loop_n_times_v1, loop_n_times_v2
import time

num_loops = 10000

# - Test 0: pure python
start_test_0 = time.time()
count = 0
for i in range(num_loops):
  count += 1
check_value_0 = count
end_test_0 = time.time()
print 'test 0 - count:{count} - time (ms):{time_delta}'.format(count=check_value_0,time_delta=(end_test_0-start_test_0)*1000.0)

# - Test 1: cythonized naive python
start_test_1 = time.time()
check_value_1 = loop_n_times_v1(num_loops)
end_test_1 = time.time()
print 'test 1 - count:{count} - time (ms):{time_delta}'.format(count=check_value_1,time_delta=(end_test_1-start_test_1)*1000.0)

# - Test 2: optimized cython
start_test_2 = time.time()
check_value_2 = loop_n_times_v2(num_loops)
end_test_2 = time.time()
print 'test 2 - count:{count} - time (ms):{time_delta}'.format(count=check_value_2,time_delta=(end_test_2-start_test_2)*1000.0)

