#include <TimerOne.h> //Needed to make this file compile because hibike compiler bugs.

#include "ui.h"
#include "motor.h"
#include "pid.h"
#include "encoder.h"
//Code here that helps deal with the human-readable UI.
//Will contain code that will do the following:

//Let the user set State: Disabled, Enabled (open loop), Enabled (PID velocity), Enabled (PID position).
//Let the user set the setpoint.
//Let the user set the current limit stuff?
//Let the user enable/disable printing of various outputs (Position, current, etc)

//This code will be called by void loop in Integrated.  It will NOT use timers or interrupts.


void manual_ui()
{


  if (heartbeat > heartbeatLimit) {
    disable();
    Serial.println("We ded");
  }
  if (continualPrint) {
    Serial.print("PWM: ");
    Serial.print(pwmPID,5);
    Serial.print("  |  Encoder Pos: ");
    Serial.print(pos);
    Serial.print("  |  Encoder Vel: ");
    Serial.println(vel);
  }
  while (Serial.available()) {
    char c = Serial.read();  //gets one byte from serial buffer
    if ( (c == 10) || (c == 13)) //if c is \n or \r
    {
      //do nothing.
    }
    else if (c == 's') 
    {
      pwmInput = Serial.parseFloat();
      Serial.print("New Speed: ");
      Serial.println(pwmInput);
    }
    else if (c == 'c') {
      Serial.println("Clearing Fault");
      clearFault();
    }
    else if (c == 'p') {
      Serial.read();
      char val = Serial.read();
      if (val == 'p') {
        driveMode = 2;
        enablePos();
        Serial.println("Turning on PID Position mode");
      } 
      else if (val == 'v') {
        driveMode = 1;
        enableVel();
        Serial.println("Turning on PID Position mode");
      }
    }
    else if (c == 'm') {
      Serial.println("Turning on manual mode");
      disablePID();
      driveMode = 0;
    }
    else if (c == 'e') {
      Serial.println("Enabled");
      enable();
    }
    else if (c == 'd') {
      Serial.println("Disabled");
      disable();
    }
    else if (c == 'r') {
      Serial.print("Encoder Pos: ");
      Serial.println(encoder());
      Serial.print("Encoder Vel: ");
      Serial.println(vel);
      Serial.print("Current: ");
      Serial.println(readCurrent());
    }
    else if (c == 't') {
      continualPrint = !continualPrint;
      Serial.println("Toggling readout prints");
    }
    else if (c == 'w') {
      Serial.read();
      char val1 = Serial.read();
      char val2 = Serial.read();
      
      if (val1 == 'c') {
        current_threshold = Serial.parseFloat();
        Serial.print("New current threshold: ");
        Serial.println(current_threshold);
      }
      else if (val1 == 'p') {
        if (val2 == 'p'){
          PIDPosKP = Serial.parseFloat();
          Serial.print("New PID position KP value: ");
          Serial.println(PIDPosKP);
        }
        else if (val2 == 'i'){
          PIDPosKI = Serial.parseFloat();
          Serial.print("New PID position KI value: ");
          Serial.println(PIDPosKI);
        }
        else if (val2 == 'd'){
          PIDPosKD = Serial.parseFloat();
          Serial.print("New PID position KD value: ");
          Serial.println(PIDPosKD);
        }
        else {
          PIDPos = Serial.parseFloat();
          Serial.print("New PID position: ");
          Serial.println(PIDPos);
        }
        updatePosPID();

    }
    else if (val1 == 'v') {
      if (val2 == 'p') {
        PIDVelKP = Serial.parseFloat();
        Serial.print("New PID velocity KP value: ");
        Serial.println(PIDVelKP);
      }
      else if (val2 == 'i') {
        PIDVelKI = Serial.parseFloat();
        Serial.print("New PID velocity KI value: ");
        Serial.println(PIDVelKI);
      }
      else if (val2 == 'd') {
        PIDVelKD = Serial.parseFloat();
        Serial.print("New PID velocity KD value: ");
        Serial.println(PIDVelKD);
      } 
      else {
        PIDVel = Serial.parseFloat();
        Serial.print("New PID velocity: ");
        Serial.println(PIDVel);
      }
      updateVelPID();
    }
    
    else {
      Serial.println("Cannot write to that");
    }
  }
  else if (c == 'b') {
    Serial.println("Heartbeat");
    heartbeat = 0;
  }
  else if (c == 'h') {
    hibike = true;
    heartbeatLimit = 500;
    Serial.println("Going to hibike mode");
  }
  else if (c == 'z') {
    hibike = false;
    heartbeatLimit = 30000;
    Serial.println("Turning off hibike");
  }
  else if (c == '?') {
    Serial.println("Manual Controls: \ns <x> - sets pwm to x \nc     - clears faults \np <x> - turns on PID mode, velocity if x = v, position if x = p \nm     - turns on manual input mode \ne     - enables motor \nd     - disables motor \nr     - displays 1 print of all readable values \nt     - toggles continual printing of pos and vel \nb     - send heartbeat \nh     - switch hibike mode \nz     - switch human controls \nw <x> <y> - writes the value y to the variable x");
  }
  else {
    Serial.println("Bad input");
  }
}
delay(10);
}

