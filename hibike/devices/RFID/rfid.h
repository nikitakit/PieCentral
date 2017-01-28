#include <SPI.h>
#include <MFRC522.h>
#include "hibike_device.h"
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  RFID,                               // Device Type
  1,                                 // Year
  UID_RANDOM,                        // ID
};
///////////////////////////////////////////////


#define RST_PIN	9
#define SS_PIN	10

#define NUM_PARAMS 1

// function prototypes
void setup();
void loop();
