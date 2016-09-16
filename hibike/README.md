# hibike 2.0!
Hibike is a lightweight communications protocol designed for the passing of sensor data for the 
PiE Robotics Kit, a.k.a Frank or "Kit Minimum" to some.

#### This branch contains documentation and implementation for the 2016-2017 version of the hibike protocol, which should feature iterative improvements over last year's protocol

#### These suggestions should make their way into protocol documentation first, then implemented in code. The basic read/write functions need to be implemented in Python, and everything needs to be implemented in Arduino, before merging this branch back to develop.

## Suggested Protocol Changes (Please make suggestions)

1. The checksum should be changed to something more robust
    - Janet suggested using UDP's checksum
2. COBS encoding should be implemented cleaner
    - It should be documented and part of the protocol itself, not a wrapper around it
    - There should not be a redundant length field
    - Only the first 2 bytes of a packet should not be cobs encoded
        - 0 byte and packet length
3. Data Update and Device Update/Status should be unified
    - Huge advantage: The BBB polling, writing, and subscribing can have identical responses from SD, and runtime can treat them the same
    - Protocol can abstract a device as only key value pairs
        - Current implementaion has key value pairs and one custom "data update" struct per device
        - Custom "data update struct" is nice because it is the exact size we need
        - Only Key Value pairs means 32 bits per digital IO pin...
        - Does ease of abstraction and implementaion justify larger packet length?
        - Is packet length significant anyways?
            - 32 bits at 115200 baud is .2 milliseconds?
            - Someone should test actual throughput
                - Especially how fast BBB can actually receive data
                - Even when doing blocking reads byte by byte in python?
                - While runtime and student code are running?
                - With 20+ devices?
        - Should the size of values be unique to reduce packet length?
            - Harder to implement
            - Both devices need to know the size of each value
                - But they needed to know the types anyways so maybe this is ok
    - SubRequest can specify which keys it wants to receive
        - Each DataUpdate will have to also encode this information to be stateless
        - What if we subscribe to more than the max payload size?
            - Just respond with as many as you can fit?
            - Error Packet?
        - A uint16_t bitmask could work? 16 keys is plenty for a device
4. Unused packets should be removed from the protocol
    - DescriptionRequest and Response are redundant
        - maintaing one config file is better for production
    - Do we have a use for the error packet yet?
        - Maybe when SD receives write requests for a read only key?
        - Maybe when a checksum fails/unexpected 0 byte is seen?
            - Can there be infinite loops of back and forth error packets?
            - Maybe only SD can send errors, and they'll only be used for logging statistics
5. Hot-Plugging behaviour should be optimized and well-defined
    - Current status quo (rebooting BBB to add devices) is unacceptable
    - Reenmerate devices every x seconds and also when runtime requests it
        - Or runtime can just request it every x seconds
    - Hibike can notify runtime when a device disconnects/connects
    - Student code accessing disconnected devices should raise a well-defined exception in *student code*
    - If a SD disconnects, will BBB find out until it tries reenumerating it?
        - If so, should BBB even bother reenumerating SDs it hasn't detected as disconnected?



## Section 0: A Quick Introduction

We make a few starting assumptions concerning the endpoints of communication: the device controlling 
a sensor is a Smart Device (SD), and a Beaglebone Black (BBB) is used as the central control board 
of each robot and thus is in charge of communicating with each Smart Device. These two communicate 
with each other via serial: the Beaglebone running pySerial and the Smart Device by using the 
built-in serial library. As each Smart Device communicates with the Beaglebone on its own separate 
port, we conveniently have no need to worry about any race conditions or other problems arising from 
concurrency.

Refer to Section 5 for an outline of the general behavior of the Hibike protocol.


## Section 1: General Message Structure
All messages have the relatively simple structure of Message ID, Payload, and Checksum as
depicted below. A more complete description of each field is given below the diagram.

    +------------+------------------+---------------------+------------+
    | Message ID |  Payload Length  |       Payload       |  Checksum  |
    |  (8 bits)  |      (8 bits)    |   (length varies)   |  (8 bits)  |
    +------------+------------------+---------------------+------------+

Message ID - an 8-bit ID specifying the type of message being sent or received. More information
             about each message type is specified in the following sections.

Payload Length - an 8-bit unsigned integer specifying the number of bytes in the payload

Payload    - Varies wildly depending on the type of message being sent. This will, of course, be
             described in more detail in Section 4.

Checksum   - An 8-bit checksum placed at the very end of every message. Really, any checksum scheme
             appending 8-bits to the end of the message will do, but an exceedingly simple one
             recommended exactly for its simplicity is making the checksum the XOR of every other
             byte in the message.

## Section 2: UID Format
Each Smart Device will be assigned an 88-bit UID with the following data.

    +-------------------+--------------+-----------------------------+
    |     Device Type   |     Year     |             ID              |
    |      (16 bits)    |   (8 bits)   |          (64 bits)          |
    +-------------------+--------------+-----------------------------+

Device Type - 16-bit ID specifying the type device the Smart Device controller is attached to.
              Device types are enumerated in Section 4

Year        - 8-bit ID corresponding to the competition year that the Smart Device was manufactured
              for. The 2015-2016 season will correspond to 0x00

ID          - Randomly generated 64-bit number that will uniquely identify each Smart Device within
              a specific device type and year. With 64-bit IDs, the probability of a hash collision 
              with 1000 of 1 type of device per year is roughly 0.05%

## Section 3: Enumerations

Message ID Enumeration:

    +---------+--------------------------+
    |   ID    |       Message Type       |
    +------------------------------------+
    |  0x00   |   Subscription Request   |
    +------------------------------------+
    |  0x01   |   Subscription Response  |
    +------------------------------------+
    |  0x02   |        Data Update       |
    +------------------------------------+
    |  0x03   |       Device Update      |
    +------------------------------------+
    |  0x04   |       Device Status      |
    +------------------------------------+
    |  0x05   |      Device Response     |
    +------------------------------------+
    |  0x06   |          Ping            |
    +------------------------------------+
    |  0x08   |    Description Request   |
    +------------------------------------+
    |  0x09   |   Description Response   |
    +------------------------------------+
    |  0xFF   |           Error          |
    +------------------------------------+

Device Type Enumeration:

    +---------+----------------+
    |   ID    |    Sensor      |
    +--------------------------+
    |  0x00   | LimitSwitch    |
    +--------------------------+
    |  0x01   | LineFollower   |
    +--------------------------+
    |  0x02   | Potentiometer  |
    +--------------------------+
    |  0x03   | Encoder        |
    +--------------------------+
    |  0x04   | BatteryBuzzer  |
    +--------------------------+
    |  0x05   | TeamFlag       |
    +--------------------------+
    |  0x06   | Grizzly        |
    +--------------------------+
    |  0x07   | ServoControl   |
    +--------------------------+
    |  0x08   | LinearActuator |
    +--------------------------+
    |  0x09   | ColorSensor    |
    +--------------------------+
    |  0x10   | DistanceSensor |
    +--------------------------+
    |  0x11   | MetalDetector  |
    +--------------------------+
    |  0xFFFF | ExampleDevice  |
    +---------+----------------+
     
Note: These assignments are totally random as of now. We need to figure
      out exactly what devices we are supporting.
Note: As of now, Grizzlies are not supported by Hibike (pyGrizzly should 
      be used instead) But they should be in the near future, to preserve 
      the idea of treating every peripheral as a SmartDevice.

Error ID Enumeration:

    +---------+---------------+
    | Status  |    Meaning    |
    +-------------------------+
    |   0xFB  |    Invalid    |
    |         | Message Type  |
    +-------------------------+
    |   0xFC  |   Malformed   |
    |         |    Message    |
    +-------------------------+
    |   0xFD  |  Invalid UID  |
    +-------------------------+
    |   0xFE  | Checksum Error|
    +-------------------------+
    |   0xFF  | Generic Error |
    +-------------------------+
Note: These assignments are also fairly random and may not all even be
      needed.

## Section 4: Message Descriptions
1. Sub Request: BBB requests data to be returned at a given interval. 
                The SD will respond with a Sub Response packet.
    Payload format:

        +---------------+
        |     Delay     |
        |   (16 bits)   |
        +---------------+

    Direction:
    BBB --> SD

2. Sub Response: SD sends (essentially) an ACK packet with the UID and 
                 delay state
    Payload format:

        +--------------------------+--------------------+
        |          UID             |       Delay        |
        |       (88 bits)          |     (16 bits)      |
        +--------------------------+--------------------+

    Direction:
    BBB <-- SD

3. Data Update: SD sends its state values based on the given delay 
                (refresh rate). BBB does not send an ACK packet back.
    Payload format:

        +------------------------+
        |        Reading         |
        |       (variable)       |
        +------------------------+

    Direction:
    BBB <-- SD

4. Device Update: BBB writes a value to the SD state. SD responds with
                  a Device Response packet.
    Payload format:

        +---------------+--------------------+
        |     Param     |       Value        |
        |    (8 bits)   |     (32 bits)      |
        +---------------+--------------------+

    Direction:
    BBB --> SD

5. Device Status: BBB polls a value from the SD state. SD responds with
                  a Device Response packet.
    Payload format:

        +---------------+
        |     Param     |
        |    (8 bits)   |
        +---------------+

    Direction:
    BBB --> SD

6. Device Response: SD returns the (possibly updated) value of the 
                    param changed/polled earlier.
    Payload format:

        +---------------+--------------------+
        |     Param     |       Value        |
        |    (8 bits)   |      (32 bits)     |
        +---------------+--------------------+

    Direction:
    BBB <-- SD

7. Ping: BBB pings SD for enumeration purposes.
         The SD will respond with a Sub Response packet.
    Payload format:

        +---------------+
        |     Empty     |
        |    (0 bits)   |
        +---------------+

    Direction:
    BBB --> SD

8. DescriptionRequest: BBB requests a descriptor string from the SD.
                       The SD will respond with a sequence of DescriptionResponse packets.
    Payload format:

        +---------------+
        |     Empty     |
        |    (0 bits)   |
        +---------------+

    Direction:
    BBB --> SD
9. DescriptionResponse: SD returns a sequence of packets containing indexes and substrings.
                        The final packet's substring is terminated with a 0 byte.
                        The BBB assembles the substrings into a full device descriptor.

    Payload format:

        +---------------+-----------------------+
        |     Index     |  Descriptor Substring |
        |    (8 bits)   |       (Variable)      |
        +---------------+-----------------------+

    Direction:
    SD --> BBB

10. Error Packet: Not planned as of yet. May only be useful for
                 debugging. See "Behavior" section for a higher-level
                 description of how error-handling will work.
    Payload format:

        +----------------+
        |   Error Code   |
        |    (8 bits)    |
        +----------------+

    Direction:
    BBB ??? SD

## Section 5: General Behavior
Setup

  1. The BBB must be able to determine what sensors are connected
     on startup. This means Hibike supports any combination of devices
     but not hot-plugging.
  2. The BBB will send Subscription Request Packets to every detectable 
     serial port with a delay value of 0, and determines the type of 
     sensor based on the Subscription Response payload sent back
  3. The BBB must then allocate bandwidth (refresh rate) based on the 
     type and number of each device connected
  4. Each supported device will have an associated data file that
     lists its reading length, parameters enumerations, etc...

Sensor Communication (Reading values)

  1. After setup the BBB sends the approrpiate Subscription Request 
     Packet is sent to each device.
  2. The SD will then return values at regular intervals specified by
     the Subscription Request (delay field)
  3. Hibike also allows for the BBB to poll certain fields from the
     state of a SD, using a Device Status Packet.
  4. The SD will respond by returning a Device Response Packet with 
     the value of the field specified.

Actuator Communication (Writing values)

  1. For devices that will have configurable states (like the 
     Grizzly), the BBB can write data to a specfied parameter of the
     SD with a Device Update Packet
  2. The SD will then return a Sensor Response Packet with the newly
     written value of the specified param in the payload.

Error handling

  1. Still kind of up in the air, but in general, only the BBB will
     have error handling behavior
  2. Every packet sent from the BBB will have a timout for recieving
     the appopriate ACK packet back. If the packet does not come
     within the time limit, or the recieved packet is invalid, the 
     BBB will try to resend the packet.
  3. If a SD recieves an invalid packet, it will simply not respond.
     This can change if need be.
