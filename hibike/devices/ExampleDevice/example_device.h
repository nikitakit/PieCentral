#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

// You must replace EXAMPLE_DEVICE with the device id of the device you are writing firmware for
// The device id's are defined in hibike/lib/hibike/devices.h
// The device if should correspond to a device id in hibike/hibikeDevices.json

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  EXAMPLE_DEVICE,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

#define NUM_PARAMS 6 //change to however many params are needed

// this is an optional device specific enum to make implementation easier
typedef enum {
  VALUE_0 = 0,
  VALUE_1 = 1,
  VALUE_2 = 2,
  VALUE_3 = 3,
  VALUE_4 = 4,
  VALUE_5 = 5
} param;

// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */
