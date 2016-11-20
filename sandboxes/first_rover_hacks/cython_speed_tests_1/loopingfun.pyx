def loop_n_times_v1(n):
  count = 0
  for i in range(n):
    count += 1

  return count

def loop_n_times_v2(int n):
  cdef int count, i
  count = 0
  for i in range(n):
    count += 1
  return count
