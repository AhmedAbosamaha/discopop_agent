#include <sys/types.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/syssgi.h>
#include <sys/immu.h>
#include <errno.h>
#include <stdio.h>

typedef unsigned long address_t;



void timer_init() 
{
  
  int fd;
  char *virt_addr;
  address_t phys_addr, page_offset, pagemask, pagebase_addr;
  
  pagemask = getpagesize() - 1;
  errno = 0;
  phys_addr = syssgi(SGI_QUERY_CYCLECNTR, &cycleval);
  if (errno != 0) {
    perror("SGI_QUERY_CYCLECNTR");
    exit(1);
  }
  resolution = 1.0e-12*cycleval; 
  base_counter = *iotimer_addr;
}

void wtime_(double *time) 
{
  static int initialized = 0;
  volatile iotimer_t counter_value;
  if (!initialized) { 
    timer_init();
    initialized = 1;
  }
  counter_value = *iotimer_addr - base_counter;
  *time = (double)counter_value * resolution;
}


void wtime(double *time) 
{
  static int initialized = 0;
  volatile iotimer_t counter_value;
  if (!initialized) { 
    timer_init();
    initialized = 1;
  }
  counter_value = *iotimer_addr - base_counter;
  *time = (double)counter_value * resolution;
}


