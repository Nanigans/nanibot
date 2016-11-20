#include <stdio.h>
#include <pigpio.h>
#include <time.h>
#include "libserialport.h"

#define GPIO_IMU_RST 18
#define GPIO_LEVEL_HIGH 1
#define GPIO_LEVEL_LOW 0


int main() {

  printf("Started!\n");

  // Initialize GPIO
  if (gpioInitialise() < 0) {
    printf("pigpio initialization failed\n");
  } else {
    printf("pigpio initialization succeeded\n");
  }
  //gpioTerminate();

  // Setup GPIO pin 18 and send rest signal
  #define GPIO_IMU_RST 18
  #define GPIO_LEVEL_HIGH 1
  #define GPIO_LEVEL_LOW 0
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
