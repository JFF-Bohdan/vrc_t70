# vrc_t70

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
