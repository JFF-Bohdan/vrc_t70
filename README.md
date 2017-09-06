# vrc_t70

![](https://travis-ci.org/JFF-Bohdan/vrc_t70)
	
Documentation, samples and tools for VRC-T70 controller.

## General information

### Protocol
TBD


## Tools

### General information

This repository contains some tools which can be useful when using VRC-T70 controller. Available tools:

* tool for devices searching;
* tool for temperature information gathering.

### Find device address

You can scan RS-485 network for VRC-T70 devices using `find_device.py` script. It will ping all devices with addresses from `0x01` up to `0xfe` and will log information about all devices online.

Example command line:

`python find_device.py --uart com15 --delay 0.1`

Where:

* `--uart com15` - specifies uart name. In this case `COM15` in Windows;
* `--delay 0.1` - specifis delay of 0.1 second before sending ping request to device with next address.

Example:

`python find_device.py --uart com15 --min 1 --max 10`

Where:
* `--min 1` - minimal device address to check;
* `--max 10` - maximal device address to check.s

Sample output:

```
Searching...
        found device with address 0x01
Done. Total_devices_count = 1
```

in this case script found one device with address `0x01.`


### Get temperatures of all sensors linked to the device

You can get information about all temperatures on all connected sensors on all trunks using `get_temperatures`. Command line example:

`python get_temperatures.py --uart com15 --address 1 --speed 115200`

Where:

* `--uart com15` - specifies uart name. In this case `COM15` in Windows;
* `--address 1` - specifies device address - 0x01;
* `--speed 115200` - specifies uart speed, 115200 if default device speed, so you can skip this parameter.


Sample output:

```
initializing communication with device 1 [0x01]...
        ping
        initializing session id with 8c4cf4a3
        session_id = 8c4cf4a3
scanning for sensors...

--==Bulk data processing commands==--
Trunk #1 [0 device(s)]:
Trunk #2 [1 device(s)]:
        [0]:    23.12 C [ number: 28fffd7f90150155 ]
Trunk #3 [0 device(s)]:
Trunk #4 [0 device(s)]:
Trunk #5 [0 device(s)]:
Trunk #6 [0 device(s)]:
Trunk #7 [0 device(s)]:

--==Simple data processing commands==--
Trunk #1 [0 device(s)]:
Trunk #2 [1 device(s)]:
        [0]:    23.12 C [ number: 28fffd7f90150155 ]
Trunk #3 [0 device(s)]:
Trunk #4 [0 device(s)]:
Trunk #5 [0 device(s)]:
Trunk #6 [0 device(s)]:
Trunk #7 [0 device(s)]:
```