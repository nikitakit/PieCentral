#include "potentiometer.h"
#include <Servo.h>



uint8_t pins[NUM_PINS] = {IN_0, IN_1, IN_2};

void setup() {
  hibike_setup();

  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    pinMode(pins[i], INPUT);
  }

}


void loop() {
  hibike_loop();
}

// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  return ~((uint32_t) 0);
}

uint32_t device_write(uint8_t param, uint8_t* data, size_t len){
  return 0;
}

// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t device_data_update(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  // Read sensor, which is in uint16
  if (MAX_PAYLOAD_SIZE - buf_len < sizeof(float) || param>2 || param<0) {
    return 0;
  }
  float *data = (float *)data_update_buf;
  data[0] = ((float)analogRead(pins[param]))/1023;
  return sizeof(float);
}
