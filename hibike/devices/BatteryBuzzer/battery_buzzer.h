#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
#include "pitches.h"
#include "disp_8.h" //implement
#include "safety.h" //implement
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  BATTERY_BUZZER,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
///
typedef enum {
  CELL_SAFE,
  CELL_LOW_VOLTAGE,
  CELL_UNBALANCED,
  CELL_DISCONNECTED
} cell_state;

// function prototypes
void setup();
void loop();

uint32_t device_write(uint8_t param, uint8_t* data, size_t len);
uint8_t device_data_update(uint8_t param, uint8_t* data_update_buf, size_t buf_len);

void calibrationSetup(bool beep);
void readTimerStart();
void updateSafety();
void updateCellStates();

cell_state new_state(float voltage, float nextCellVoltage, bool disconnected, cell_state lastState);
float abs_diff(float a, float b);

#endif /* EX_DEVICE_H */
