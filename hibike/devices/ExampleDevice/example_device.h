#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  EXAMPLE_DEVICE,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

#define NUM_PARAMS 6 //change to however many params are needed


// function prototypes
void setup();
void loop();

uint8_t device_data_update(int param, uint8_t* data_update_buf, size_t buf_len);
uint32_t device_write(uint8_t param, uint8_t* data, size_t len);

#endif /* EX_DEVICE_H */