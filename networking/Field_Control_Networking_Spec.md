# Field Control Networking Specificiation

## Contents

1. Overview
2. Setting up the Clients and Network
3. Connecting to the Field Control Network
4. Establishing Communication Links
5. Sending Messages

## 1. Overview

A robot interacts with two networks:  the Student network and the Field Control (FC) network.  The former is the network over which students communicate with their robot via provided mini-routers.  The latter--the focus of this spec--is the network over which students' robots interact with FC over the course of a match.

Clients (field control, driver stations, and robots) are assigned static IPs and communicate over TCP connections.

FC sends out messages to initiate robot-to-driver-station pairing and robot mode changes.  FC listens to heartbeat messages from robots.

## 2. Setting Up the Clients and Network

### Clients

The FC network will have up to eight clients, as follows:

- One FC client.  This is the FC computer running the match.  A PiE computer+monitor. 
- Four driver station clients.  This acts as the student-robot interface (via Dawn and Runtime), and as the robot-field control interface (see "Establishing Communication Links").  A wifi-enabled laptop or  computer+monitor.
- Up to four robot clients.  A wifi-enabled Beagle Bone Black (via wifi dongle).  One per student robot.

### Assigning IP Addresses

Every client will have a statically assigned IP address.  This is feasible due to the small number of total clients (1 per robot ( less than 30 in total), 4 driver stations, and one field control center).

Consider the following example static IP scheme ("P" = subnet prefix):

- FCl:  P.255
- Driver Stations:  P.254-251
- Robots:  P.TeamNumber

## 3. Connecting to the Field Control Network

### Configuration

A robot can connect to at most one network at a time, which must be either the Student network or the FC network.  The Student network is to be listed as higher priority than the FC Network.  This can be set each robot's network config file.

In order to participate in a match, teams temporarily relinquish their routers.

### Rationale 

This results in two desirable guarantees:

1. When not in a match, students will always be able to connect with their robots over the Student network even if the robot is within range of the FC network.
2. When in a match, robots will only have the option of connecting to the FC network (due to router confiscation). 

Note that this may result in robots not in a match to still be connected to the FC network.  However, this is totally fine since the FC client will not be listening to robots not currently tied to a driver station (see "Sending Messages").

## 4. Establishing Communication Links

Within each match, the FC network will create/maintain eight TCP connections:

- A connection between the FC client and each Driver Station client.  These can persist across matches, and so need to be opened only once per network initialization.
- A connection beween a Driver Station client and its corresponding Robot client. These must be opened/closed at the start/end of each match (i.e. once the Robot client joins/leaves the FC network and is paired/unpaired with a Driver Station client).

If a FC-to-Driver-Station connection is dropped, FC is responsible for reestablishing the connection.  If a Driver-Station-to-Robot connection is dropped, the Driver Station notifies FC; FC then re-sends the pairing message to said Driver Station (see "Sending Messages").

## 5. Sending Messages

The FC client sends messages to initiate robot-to-driver-station pairing, and to indicate what mode (autonomous, tele-op, etc) the robot is in.   Driver station clients listen accordingly, and pass the message to robots.

Robot clients send only a heartbeat, which contains a status value that the FC client can use to verify the robot is both connected an in the expected mode.

In further detail:

### From FC

**Robot-to-Driver-Station Pairing.**  Prior to this message, a robot, while connected to the network, is not yet associated with a driver station.  Containing the static IP of the Robot client with which to pair, the FC client sends this to the Driver Station client, which then opens a connection and begins communication with said robot.

If more than one robot responds to the pairing message (i.e. IP address collision), or if no robot responds, FC is notified by the Driver Station.  The match will not proceed until this is externally resolved (e.g. reprogramming the suspected robot(s)'s Beaglebones).

**Mode Changing.**  This message contains an integer indicating whether the robot should be in Autonomous (1), Tele-Op (2), Disabled (3), or E-Stopped (4) mode.  Sent from FC to Driver Station, then Driver Station to Robot.

### To FC

**Heartbeat.** Upon pairing, the robot begins sending a "heartbeat"--a message containing a single integer between 0 and 4 (inclusive) indicating its mode. If no mode change message has been received yet, it replies Connected (0) by default. Sent from Robot to Driver Station, then Driver Station to FC.
