#include<stdio.h>
#include "libserialport.h"


main()
{

printf("Started!\n");

struct sp_port **list;
int i, ret;

ret = sp_list_ports(&list);

if (ret == SP_OK) {
  printf("Success getting ports list!\n");
  for (i = 0; list[i]; i++) {
    printf("Found port: '%s'\n",sp_get_port_name(list[i]));
  }

} else {
  printf("No joy getting ports list!\n");
}
sp_free_port_list(list);

// Get pointer to port
char port_name[] = "/dev/ttyAMA0";
char *port_description;
int baudrate, num_bits, stop_bits;
enum sp_parity parity_code;
struct sp_port *my_port;
struct sp_port_config *my_port_config;

ret = sp_get_port_by_name(port_name, &my_port);
if (ret != SP_OK) {
  printf("Failed to get port: %s.  Exiting now.\n",port_name);
  return 0;
}

port_description = sp_get_port_description(my_port);
printf("Details of port: %s\n",port_description);

// Open port
ret = sp_open(my_port, SP_MODE_READ_WRITE);
if (ret == SP_OK) {
  printf("Successfully opened port!\n");
} else {
  printf("Failed to open port :(\n");
  sp_free_port(my_port);
  return 0;
}

// Initialize port config
ret = sp_new_config(&my_port_config);
if (ret != SP_OK) {
  printf("Failed to initialize port config.\n");
  sp_free_port(my_port);
  return 0;
}

// Get default config details
ret = sp_get_config(my_port, my_port_config);
if (ret != SP_OK) {
  printf("Failed to get port config.\n");
  sp_free_port(my_port);
  return 0;
}
ret = sp_get_config_baudrate(my_port_config, &baudrate);
if (ret == SP_OK) {
  printf("Default baudrate: %d\n",baudrate);
} else {
  printf("Failed to get baudrate.\n");
  sp_free_port(my_port);
  return 0;
}
ret = sp_get_config_bits(my_port_config, &num_bits);
if (ret == SP_OK) {
  printf("Default number of bits: %d\n",num_bits);
} else {
  printf("Failed to get number of bits.\n");
  sp_free_port(my_port);
  return 0;
}
ret = sp_get_config_stopbits(my_port_config, &stop_bits);
if (ret == SP_OK) {
  printf("Default number of stop bits: %d\n",stop_bits);
} else {
  printf("Failed to get number of stop bits.\n");
  sp_free_port(my_port);
  return 0;
}
ret = sp_get_config_parity(my_port_config, &parity_code);
if (ret == SP_OK) {
  printf("Default parity: %d\n",parity_code);
} else {
  printf("Failed to get default parity.\n");
  sp_free_port(my_port);
  return 0;
}


printf("Reached end!\n");

}
