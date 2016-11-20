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

}
