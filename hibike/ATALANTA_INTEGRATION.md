# Hibike Runtime Integration

All hibike smart devices are abstracted as a mapping of parameters to values.
Runtime can read from, write to, or subscribe to these parameters.
Paramaters are always strings, but the type of each value is unique.
A config file will describe the type of the value for each paramater, and the parameters for each smart device type.
A parameter can be read only, write only, or read/write.

## Example Smart Devices:

LimitSwitch

- switch0: bool read only
- switch1: bool read only
- switch2: bool read only
- switch2: bool read only

Servo

- servo0_torqued: bool read/write
- servo0_pos: int read/write

MetalDetector

- callibrate: bool write only
- reading: int read only



## StateManager -> Hibike

`[SM_COMMANDS.READY]`

- tells hibike it's ready for instructions

`[SM_COMMANDS.ENUMERATE_ALL]`

- tells hibike to reenumerate all smart devices

`[SM_COMMANDS.SUBSCRIBE_DEVICE, uid, delay, [param1, param2, ...]]`

- tells hibike to subscribe to specific paramaters of a smart device

`[SM_COMMANDS.WRITE_PARAM, uid, param, value]`

- tells hibike to write to a specific parameter of a smart device

`[SM_COMMANDS.READ_PARAM, uid, param, value]`

- tells hibike to read (poll) a specific parameter of a smart device




## Hibike -> StateManager

`[SM_COMMANDS.DEVICE_SUBSCRIBED, uid, delay, [param1, param2, ...]]`

- sent when the BBB either enumerates or subscribes to a smart device

`[SM_COMMANDS.DEVICE_DISCONNECTED, uid]`

- sent when a smart device disconnects

`[SM_COMMANDS.DEVICE_VALUE, uid, param, value]`

- sent when the BBB receives a value from a smart device

`[SM_COMMANDS.INVALID_UID, uid]`

- sent when hibike receives a command from stateManager with a smart device that isn't connected

`[SM_COMMANDS.INVALID_PARAM, uid, param]`

- sent when hibike receives a command for a valid uid with a nonexistent param

`[SM_COMMANDS.PARAM_READ_ONLY, uid, param]`

- sent when stateManager tries to write to a read only param

`[SM_COMMANDS.PARAM_WRITE_ONLY, uid, param]`

- sent when stateManager tries to poll or subscribe to a write only param