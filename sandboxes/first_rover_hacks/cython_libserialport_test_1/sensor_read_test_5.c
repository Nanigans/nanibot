#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/time.h>
#include <errno.h>
#include <signal.h>
#include "libserialport.h"
#include "bno055_read_test.h"

#define MAX_LOOP_COUNT 100000000
#define WAKEUP_INTERVAL_SEC 0

int wakeup_count = 0, wakeup_set = 0, read_started = 0, read_completed = 0, wakeup_wrap = 0;

void wakeup_handler(int signum) {
  if (wakeup_set) {
    wakeup_wrap = 1;
  }
  wakeup_set = 1;
}

void finalize_wakeup_attempt() {
  wakeup_set = 0;
  wakeup_count++;
  read_started = 0;
  read_completed = 1; 
}

int main() {
  int ret, num_samples = 1000, sample_interval_usec = 10000, max_read_retries = 10;
  ret = run_serial_read_test_2(num_samples, sample_interval_usec, max_read_retries);
  return ret;
}

int initialize_sensor_itimer(int wakeup_interval_usec) {

  int ret;

  // - Block all signals other than SIGALRM
  sigset_t mask;
  sigfillset(&mask);
  sigdelset(&mask,SIGALRM);
  sigdelset(&mask,SIGINT);
  sigprocmask(SIG_SETMASK, &mask, NULL);

  // - Configure and set interupt timer
  struct itimerval timer;
  struct timeval tv;

  tv.tv_sec = WAKEUP_INTERVAL_SEC;
  tv.tv_usec = wakeup_interval_usec;
  timer.it_interval = tv;
  timer.it_value = tv;

  struct sigaction new_action, old_action;
  memset(&new_action, 0, sizeof(new_action));
  memset(&old_action, 0, sizeof(old_action));
  new_action.sa_handler = wakeup_handler;
  ret = sigaction(SIGALRM, &new_action, &old_action);

  if (ret < 0) {
    printf("Error setting up sigaction.\n");
    return 0;
  }

  ret = setitimer(ITIMER_REAL,&timer,NULL);
  if (ret < 0) {
    printf("Error setting interupt timer.  Error: %d\n",errno);
    return 0;
  }

  return 1;
}

int run_serial_read_test(int num_samples) {
  int ret;
  ret = run_serial_read_test_2(num_samples, 10000, 10);
  return ret;
}

int run_serial_read_test_2(int num_samples, int sample_interval_usec, int max_read_retries) {

  // Reset global variables (This proved necessary when repeatedly calling this function from iPython)
  wakeup_count = 0; 
  wakeup_set = 0; 
  read_started = 0; 
  read_completed = 0; 
  wakeup_wrap = 0;

  // - Compute operational constants
  float max_time_sec = 10 * num_samples * sample_interval_usec * 1.0e-6; // Extra factor of 10, so we don't get cutoff prematurely

  // - Get serial port adapter and config object
  int ret;
  struct sp_port *serial_adapter;
  struct sp_port_config *serial_config;

  ret = sp_new_config(&serial_config);
  ret = get_serial_adapter(&serial_adapter, serial_config);
  if (ret != 1) {
    printf("Failed to get serial adapter :(\n");
    sp_free_port(serial_adapter);
  }

  Point3D measurement_vector;
  //Point3D measurement_vector = (Point3D){ .x=(float)0, .y=(float)0, .z=(float)0 };

  ret = read_linear_acceleration_vector(serial_adapter, &measurement_vector);
  if (ret == 1) {
    printf("Successfully read linear acceleration.\n");
    printf("Example Measurement - x: %d - y: %d - z: %d\n",measurement_vector.x,measurement_vector.y,measurement_vector.z); 
  } else {
    printf("Failed to read linear acceleration.\n");
  }

  // - Initialize interupt timer for sensor readings
  if (!initialize_sensor_itimer(sample_interval_usec)) {
    return 0;
  }


  // Relevant global variables: int wakeup_set, read_started, read_completed
  int loop_count = 0, success_count = 0, comm_fail_count = 0, wrap_count = 0, max_comm_fail_count = 0;
  struct timespec start_timespec, current_timespec, heartbeat_timespec;
  double duration, heartbeat_duration;
  ret = clock_gettime(CLOCK_REALTIME,&start_timespec);
  ret = clock_gettime(CLOCK_REALTIME,&heartbeat_timespec);

  while (1) {
    
    loop_count++;
    ret = clock_gettime(CLOCK_REALTIME,&current_timespec);
    duration = ((double)current_timespec.tv_sec+1.0e-9*(current_timespec.tv_nsec)) - ((double)start_timespec.tv_sec + 1.0e-9*(start_timespec.tv_nsec));
    heartbeat_duration = ((double)current_timespec.tv_sec+1.0e-9*(current_timespec.tv_nsec)) - ((double)heartbeat_timespec.tv_sec + 1.0e-9*(heartbeat_timespec.tv_nsec));
  
    // Show heartbeat message so I know test is still running 
    if (heartbeat_duration >= 10) {
      ret = clock_gettime(CLOCK_REALTIME,&heartbeat_timespec);
      printf("Heart beat!  Cumulative time (sec): %f\n",duration);
    }

    // Upper bound the max test duration (time) 
    if (duration >= max_time_sec) {
      printf("Max program duration expired\n");
      break;
    }

    // Upper bound the max test duration (loops) 
    if (loop_count >= MAX_LOOP_COUNT) {
      printf("Max program loop count exhausted\n");
      break;
    }

    // End the test after the desired number of read attempts (number of scheduled wakeups, actually)
    if (wakeup_count >= num_samples) {
      printf("Max read attemps exhasted\n");
      break;
    }

    // Come in here if a scheduled wakeup occurred and has not been marked complete (by success or failure)
    if (wakeup_set) {
      
      // If the last wakeup did not conclude by the time of the next scheduled wakeup, let me know
      if (wakeup_wrap == 1) {
        //printf("Timer wrap around for turn %d\n",wakeup_count);
        wakeup_wrap = 0;
        wrap_count++;
        finalize_wakeup_attempt();
        // In the case of wakeup wrap, keep wakeup_set true, but count the failed attempt
        wakeup_set = 1;
      }      
 
      // Check if there was a failed read attempt since last scheduled wakeup
      if (read_started && !read_completed) {
        comm_fail_count++;
        
        // Giveup on this wakeup after max_read_retries read attempts
        if (comm_fail_count > max_read_retries) {
          finalize_wakeup_attempt(); 
          comm_fail_count = 0;
          max_comm_fail_count++;
          //printf("Failed serial communication on all %d retries for turn %d\n",max_read_retries,wakeup_count);
         
          continue;
        }
      }
      
      // Indicate that we have started trying to read from the sensor for the current scheduled wakeup
      read_started = 1;
      read_completed = 0;
      
      ret = read_linear_acceleration_vector(serial_adapter, &measurement_vector);
      if (ret == 1) {
        success_count++;
      } else {
        continue;
        //printf("Failed to read linear acceleration in turn %d.\n",wakeup_count);
      }

      finalize_wakeup_attempt(); 
      if (comm_fail_count > 15) {
        printf("Wake up!  Cumulative time (sec): %f.  Succeeded after %d retries\n",duration,comm_fail_count);
      } /* else {
        printf("Wake up!  Cumulative time (sec): %f\n",duration);
      } */
      comm_fail_count = 0;

      continue;
    }
  }

  // int loop_count = 0, success_count = 0, comm_fail_count = 0, wrap_count = 0, max_comm_fail_count = 0;
  printf("Program duration (sec): %f\n",duration);
  printf("Read attempts: %d\n",wakeup_count);
  printf("Sensor sample interval (ms): %0.1f\n",(double)sample_interval_usec/(double)1000);
  printf("Successful reads: %d\n",success_count);
  printf("Max comm failure occurrences: %d\n",max_comm_fail_count);
  printf("Wakeup wrap count: %d\n",wrap_count);
  printf("Read success rate: %0.3f\n",(double)success_count/(double)wakeup_count);

  // - Clean up program
  sp_free_port(serial_adapter);
  printf(" ---- End of test...Freed Serial Port ---- \n");
  return 0;

}


int get_serial_adapter(struct sp_port **my_port, struct sp_port_config *my_port_config) {

  int ret;

  // Get pointer to port
  char port_name[] = "/dev/ttyAMA0";

  ret = sp_get_port_by_name(port_name, my_port);
  if (ret != SP_OK) {
    printf("Failed to get port: %s.  Exiting now.\n",port_name);
    return 0;
  }

  // Open port
  ret = sp_open((*my_port), SP_MODE_READ_WRITE);
  if (ret == SP_OK) {
    printf("Successfully opened port!\n");
  } else {
    printf("Failed to open port :(\n");
    sp_free_port(*my_port);
    return 0;
  }

  // Initialize port config
  ret = sp_new_config(&my_port_config);
  if (ret != SP_OK) {
    printf("Failed to initialize port config.\n");
    sp_free_port(*my_port);
    return 0;
  } else {printf("Successfully initialized port config.\n");}

  return 1;
}

int serial_send(struct sp_port *my_port, const void *command, size_t write_bytes_count, void *response) {

  int ret, read_count=8; 

  if (DO_BLOCKING_READ_WRITE) {
    unsigned int timeout = READ_WRITE_TIMEOUT_SEC*1000;
    
    ret = sp_blocking_write(my_port, command, write_bytes_count, timeout);
    if (ret <= 0) {
      printf("Failed to write serial bytes.\n");
      return 0;
    }
    ret = sp_blocking_read(my_port, response, (size_t)read_count, timeout);
 
  } else {

    int fd;
    ret = sp_get_port_handle(my_port,&fd);
    if (ret != SP_OK) {
      printf("Failed to get port handle for nonblocking read/write.\n");
    }
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(fd,&fds);
    
    struct timespec ts;
    ts.tv_sec = READ_WRITE_TIMEOUT_SEC;
    ts.tv_nsec = 0;
    
    ret = pselect(fd+1, NULL, &fds, NULL, &ts, NULL);
    if (ret < 0 && errno != EINTR) {
      printf("Error in pselect for write: %d\tport handle: %d\n",errno,fd);
      return 0;
    } else if (ret == 0) {
      printf("Timeout while waiting to write.\n");
      return 0;
    }
    ret = sp_nonblocking_write(my_port, command, write_bytes_count);

    FD_ZERO(&fds);
    FD_SET(fd,&fds);
    ts.tv_sec = READ_WRITE_TIMEOUT_SEC;
    ts.tv_nsec = 0;
     
    ret = pselect(fd+1, &fds, NULL, NULL, &ts, NULL);
    if (ret < 0 && errno != EINTR) {
      printf("Error in pselect for read.\n");
      return 0;
    } else if (ret == 0) {
      printf("Timeout while waiting to read.\n");
      return 0;
    }
    ret = sp_nonblocking_read(my_port, response, (size_t)read_count);
  
  }

  if (ret < read_count) {
    //printf("Successful write to serial, but failed on serial read.\n");
    return 0;
  } else {
    return ret;
  }

}

int read_linear_acceleration_vector(struct sp_port *my_port, Point3D *result) {
  int ret;
  ret = read_sensor_vector(my_port, BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR, result);

  return ret; 
}

// TODO: encapsulate robust serial processing, including retries and timeouts
int read_sensor_vector(struct sp_port *my_port, char address, Point3D *result) {

  int i, ret, expected_data_size, expected_response_size;
  expected_data_size = 6; // x, y, z data at 2 bytes per datum
  expected_response_size = expected_data_size + 2; // 2 extra bytes in packet, as per data sheet
  
  // Initialize intermediate serial response buffer
  char response[expected_response_size];
  short int temp_result[3];

  // Construct standard UART read packet (described in BNO055 data sheet: https://cdn-shop.adafruit.com/datasheets/BST_BNO055_DS000_12.pdf)
  char command[] = {0xAA, 0x01, address & 0xFF, expected_data_size & 0xFF};

  
  // First, flush the input buffer
  ret = sp_flush(my_port,SP_BUF_INPUT); 

  // Second, send data read command to BNO055
  ret = serial_send(my_port, command, sizeof(command), response);
  if (ret != expected_response_size) {
    //printf("Linear acceleration read returned wrong size response.  Expected %d, Got %d.\n",expected_response_size,ret);
    return 0;
  }


  // Verify register read success
  if (response[0] != 0xBB) {
    //printf("Register read error.\n");
    return 0;
  }

  
  // - Unpack serial response into result array
  // - First two bytes are metadata, unpack remaining N bytes of data
  for (i = 0; i<(expected_data_size/2); i++) {
    temp_result[i] = ((response[i*2+3] << 8) | response[i*2+2]) & 0xFFFF;
    if (temp_result[i] > 32767) {
      temp_result[i] = temp_result[i] - 65536;
    }
  }

  // Set fields of result
  result->x = temp_result[0];
  result->y = temp_result[1];
  result->z = temp_result[2];

  return 1;

}


