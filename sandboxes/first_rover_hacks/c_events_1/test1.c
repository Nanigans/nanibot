#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <signal.h>

#define MAX_TIME_SEC 20
#define MAX_LOOP_COUNT 100
#define WAKEUP_INTERVAL 2

int wakeup_set = 0;

void wakeup_handler(int signum) {
  wakeup_set = 1;
}

int main(void) {

  struct itimerval timer;
  struct timeval tv;

  tv.tv_sec = (time_t)WAKEUP_INTERVAL;
  timer.it_interval = tv;
  timer.it_value = tv;

  int ret, loop_count = 0, duration = 0;

  struct sigaction new_action, old_action;
  memset(&new_action, 0, sizeof(new_action));
  memset(&old_action, 0, sizeof(old_action));
  new_action.sa_handler = wakeup_handler;
  //sigemptyset(&new_action.sa_mask);
  //new_action.sa_flags = 0;
  ret = sigaction(SIGALRM, &new_action, &old_action);

  if (ret < 0) {
    printf("Error setting up sigaction.\n");
    return 0;
  }

  ret = setitimer(ITIMER_REAL,&timer,NULL);
  if (ret < 0) {
    printf("Error setting interupt timer.\n");
    return 0;
  }

  time_t start_time = time(NULL), current_time;


  while (duration < MAX_TIME_SEC && loop_count < MAX_LOOP_COUNT) {
    loop_count++;

    current_time = time(NULL);
    duration = (int)current_time - (int)start_time;

    if (wakeup_set) {
      printf("Wake up!  Cumulative time (sec): %d\n",duration);
      wakeup_set = 0;
      continue;
    }

    sleep(1);
  }

  printf("Number of loops completed: %d\n",loop_count);

  return 0;
}
