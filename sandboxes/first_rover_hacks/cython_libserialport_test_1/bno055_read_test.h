#include "libserialport.h"

#define DO_BLOCKING_READ_WRITE 1
#define READ_WRITE_TIMEOUT_SEC 5

#define GPIO_IMU_RST 18
#define GPIO_LEVEL_HIGH 1
#define GPIO_LEVEL_LOW 0

// Linear acceleration data registers
#define BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR  0X28
#define BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR  0X29
#define BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR  0X2A
#define BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR  0X2B
#define BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR  0X2C
#define BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR  0X2D

typedef struct {
  short int x;
  short int y;
  short int z;
} Point3D;

int main(void);

int run_serial_read_test(int num_trials);

int get_serial_adapter(struct sp_port **my_port, struct sp_port_config *my_port_config);

int serial_send(struct sp_port *my_port, const void *command, size_t write_bytes_count, void *response);

int read_sensor_vector(struct sp_port *my_port, char address, Point3D *result);

int read_linear_acceleration_vector(struct sp_port *my_port, Point3D *result);

