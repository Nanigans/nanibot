#include <stdio.h>
#include <pigpio.h>
#include <time.h>
#include "libserialport.h"
#include "bno055_reset.h"

// gcc -o reset_bno.exe reset_bno.c -iquote/home/pi/libserialport -I/home/pi/libserialport -lrt -lpigpio

int reset_bno055() {

  // Initialize GPIO
  if (gpioInitialise() < 0) {
    printf("pigpio initialization failed\n");
  } else {
    printf("pigpio initialization succeeded\n");
  }

  // Setup GPIO pin 18 and send rest signal
  if (gpioSetMode(GPIO_IMU_RST, PI_OUTPUT) < 0) {
    printf("GPIO 18 setup failed\n");
    gpioTerminate();
  } else {
    printf("GPIO 18 setup succeeded\n");
  }

  if (gpioWrite(GPIO_IMU_RST, GPIO_LEVEL_HIGH) < 0) {
    printf("GPIO RST write high failed\n");
    gpioTerminate();
  } else {
    printf("GPIO RST write high succeeded\n");
  }
  // Sleep 650 ms to allow BNO055 to fully reset
  time_sleep(0.65);
  
  // - Clean up program
  gpioTerminate();
  printf("Reached end!\n");
  return 0;

}

int main() { 
  int ret;
  ret = reset_bno055();
  return ret;
}
