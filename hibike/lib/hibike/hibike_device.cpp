#include "hibike_device.h"

message_t hibikeBuff;
uint64_t prevTime, currTime, heartbeatTime,sentHeartbeat, respHeartBeat;
uint16_t params, old_params;
uint32_t value;
uint16_t subDelay,hb_freq;
led_state heartbeat_state;
bool led_enabled;

void hibike_setup() {
  Serial.begin(115200);
  prevTime = millis();
  subDelay = 0;
  hb_freq = 0;

  // Setup Error LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  heartbeat_state = RESTING;
  led_enabled = false;

}

void hibike_loop() {
  currTime = millis();
  // Check for Hibike packets
  if (Serial.available() > 1) {
    if (read_message(&hibikeBuff) == -1) {
      toggleLED();
    } else {
      int offset;
      switch (hibikeBuff.messageID) {

        case SUBSCRIPTION_REQUEST:
          // change subDelay and send SUB_RESP
          subDelay = *((uint16_t*) &hibikeBuff.payload[2]);
          params = *((uint16_t*) &hibikeBuff.payload[0]);
          send_subscription_response(params, subDelay, &UID);
          break;

        case SUBSCRIPTION_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;

        case DEVICE_WRITE:
          //loop over params
          old_params = params;
          offset = 2;
          params = *((uint16_t*)&hibikeBuff.payload[0]);
          for (uint16_t count = 0; (params >> count) > 0; count++) {
            if (params & (1<<count)){
              int status = device_write(count, &hibikeBuff.payload[offset], hibikeBuff.payload_length-offset);
              if(status){
                offset += status;}
              else{
                params = params & ~(1<<count);}
              }
          }

          //write values
          *((uint16_t*)&hibikeBuff.payload[0]) = params;
          send_data_update(*((uint16_t*) &hibikeBuff.payload[0]));
          params = old_params;
          break;

        case DEVICE_READ:

          send_data_update(*((uint16_t*) &hibikeBuff.payload[0]));
          break;

        case DEVICE_DATA:
          // Unsupported packet
          toggleLED();
          break;

        case HEART_BEAT_REQUEST:
          //send heart beat response
          send_heart_beat_response(1);
          break;

        case HEART_BEAT_RESPONSE:
          respHeartBeat = currTime
          // Unsupported packet at this time
          break;

        case PING:
          send_subscription_response(params, subDelay, &UID);
          break;

        default:
          // Uh oh...
          toggleLED();
      }
    }
  }

  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    send_data_update(params);
  }

  if ((hb_freq > 0) && (currTime - sentHeartbeat)>=hb_freq){
    else{
      send_heart_beat_request(1);
      sentHeartbeat = currTime;
    }
  }

  // // Hearbeat
  // switch (heartbeat_state) {
  //   case RESTING:
  //     if (currTime - heartbeatTime >= 1700) {
  //       heartbeatTime = currTime;
  //       digitalWrite(LED_PIN, HIGH);
  //       led_enabled = true;
  //       heartbeat_state = FIRST_BEAT;
  //     }
  //     break;

  //   case FIRST_BEAT:
  //     if (currTime - heartbeatTime >= 100) {
  //       heartbeatTime = currTime;
  //       digitalWrite(LED_PIN, LOW);
  //       led_enabled = false;
  //       heartbeat_state = BREAK;
  //     }
  //     break;

  //   case BREAK:
  //     if (currTime - heartbeatTime >= 100) {
  //       heartbeatTime = currTime;
  //       digitalWrite(LED_PIN, HIGH);
  //       led_enabled = true;
  //       heartbeat_state = SECOND_BEAT;
  //     }
  //     break;

  //   case SECOND_BEAT:
  //     if (currTime - heartbeatTime >= 100) {
  //       heartbeatTime = currTime;
  //       digitalWrite(LED_PIN, LOW);
  //       led_enabled = false;
  //       heartbeat_state = RESTING;
  //     }
  //     break;
  // }

}

void toggleLED() {
  if (led_enabled) {
    digitalWrite(LED_PIN, LOW);
    led_enabled = false;
  } else {
    digitalWrite(LED_PIN, HIGH);
    led_enabled = true;
  }
}

uint64_t getLastHeartbeatResponse(){
  return respHeartBeat;
}

uint64_t getLastHeartbeatRequest(){
  return sentHeartbeat;
}

void setHeartBeatFreq(uint16_t freq){
  hb_freq = freq;
}