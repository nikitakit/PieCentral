#include "line_follower.h"

uint16_t data[NUM_PINS];

void setup() {
  hibike_setup();

  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    pinMode(pins[i], INPUT_PULLUP);
  }

}


void loop() {
  hibike_loop();
}


uint32_t device_update(uint8_t param, uint32_t value) {
  return ~((uint32_t) 0);
}


uint32_t device_status(uint8_t param) {
  return ~((uint32_t) 0);
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t device_data_update(uint16_t params, uint8_t* data_update_buf, size_t buf_len) {
  if (buf_len < sizeof(uint16_t) * NUM_PINS) {
    return 0;
  }

  uint8_t *data = (uint8_t *) data_update_buf;
  // Read sensor
  int i=0;
  for (int count = 0; params > 0; params = params>>1) {
      if (params & 1){
        data[i] = 1 - analogRead(pins[i]);
        i++;
      }
      count++;
  }
  return sizeof(uint8_t) * i;



// uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
//   if (buf_len < sizeof(uint16_t) * NUM_PINS) {
//     return 0;
//   }

//   // Read sensor
//   for (int i = 0; i < NUM_PINS; i++) {
//       data[i] = analogRead(pins[i]);  
//   }
  
//   // Append data to packet buffer
//   uint8_t offset = 0;
//   for (int i = 0; i < NUM_PINS; i++) {
//     append_buf(data_update_buf, &offset, (uint8_t *)&data[i], sizeof(uint16_t));
//   }

//   return offset;
// }
