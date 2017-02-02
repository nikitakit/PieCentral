#include "battery_buzzer.h"

// each device is responsible for keeping track of it's own params

buzzer = 10;

last_print_time = 0; //for the loop counter...


triple_calibration = true; //decide whether to use triple calibration or the simpler single calibration.

float vref_guess = 2.56;  //initial guess, based on datasheet.
calib[] = {2.56,2.56,2.56}; //initial guess, based on datasheet.


//got to keep these globals here to keep the compiler happy.
v_cell1;  // param 1
v_cell2;  // param 2
v_cell3;  // param 3
v_batt;   // param 4
dv_cell2; // param 5
dv_cell3; // param 6

bool print = false // keep until all Serial methods get deleted


// normal arduino setup function, you must call hibike_setup() here
void setup() {
  
  if(prints){
    //send working signal
  }
  pinMode(buzzer,OUTPUT);

  setup_display();
  setup_sensing();

  hibike_setup();
}


// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them

void loop() {
  // do whatever you want here
  // note that hibike will only process one packet per call to hibike_loop()
  // so exessive delays here will affect hibike.
  handle_8_segment();
  handle_calibration();

  if(millis() - last_print_time>250){
    measure_cells();
    handle_safety();
  }
  hibike_loop();
}


// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in little-endian bytes
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  //trigger calibration

}


// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data_update_buf to contain the parameter value.
//    param           -   Parameter index
//    data_update_buf -   buffer to return data in, little-endian
//    buf_len         -   Maximum length of the buffer
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_data_update(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  if(param == 0){
    if (MAX_PAYLOAD_SIZE - buf_len > sizeof(uint8_t)) {
      data_update_buf[0] = unsafe_status;
      return sizeof(uint8_t);
    }
  }
  if (MAX_PAYLOAD_SIZE - buf_len < sizeof(float) || param<0 || param >= 7){
    return 0
  }
  float_buf = (float *) data_update_buf;
  if(param == 1){
    float_buf[0] = v_cell1
  }
  else if(){

  }
  else if(){

  }
  else if(){

  }
  else if(){

  }
  else if(){

  }

  data_update_buf[0] = (uint8_t*) float_buf;
  return sizeof(float);
}
