# vrc_t70

![](https://travis-ci.org/JFF-Bohdan/vrc_t70.svg?branch=master)	

Documentation, samples and tools for VRC-T70 controller.

This repository contains:

* General information about controller;
* Protocol;
* Python library which can be used for communication with controller;
* Tools and examples that uses Python library to to get current sensors data and 
servicing functionality.

**RU:** документация, примеры и утилиты для работы с контроллером VRC-T70.
Русская версия документации может быть найдена в [./doc/README_ru.md](./doc/README_ru.md)

## General information

VRC-T70 controller able to communicate with up to 70
widely known [DS18B20](https://www.google.com.ua/search?q=ds18b20%20tech%20spec)
sensors, divided for 7 trunks.

Each trunk can contain up to 10 sensors, connected using [1-Wire](https://en.wikipedia.org/wiki/1-Wire) bus. 

Controller can be connected to master device (for example computer or other controller) using
[RS485](https://en.wikipedia.org/wiki/RS-485) bus. One RS485 network can contain many VRC-T70 
devices, so real count of connected DS18B20 can be huge and fit your requirements.

### Protocol

VRC-T70 device communicates using open protocol, which documented in
[./doc/protocol/protocol_en.md](./doc/protocol/protocol_en.md)

## Packgage and tools

### General information

This repository contains `vrc_t70` package that can be used in your Python Program to communicate with VRC-T70 device. Also, it contains some tools which can be useful when using VRC-T70 controller. 

Available tools:

* tool for devices searching on RS-485 bus;
* tool for temperature information gathering.


### Installation

#### Latest PyPI stable release

```pip install tqdm```


#### Latest development release on GitHub

pip install -e git+https://github.com/JFF-Bohdan/vrc_t70@master#egg=vrc_t70

### Tools

#### General information

Tools can be used after package installation only

#### Find device address

You can scan RS-485 network for VRC-T70 devices using `find_device` tool. It
will ping all devices with addresses from `0x01` up to `0xfe` and will log information 
about all devices online.

Example command line:

`find_device --uart com15 --delay 0.1`

Where:

* `--uart com15` - specifies uart name. In this case `COM15` in Windows;
* `--delay 0.1` - specifis delay of `0.1` second before sending ping request to 
device with next address.

Example:

`find_device --uart com15 --min 1 --max 10`

Where:
* `--min 1` - minimal device address to check;
* `--max 10` - maximal device address to check.

Sample output:

```
Searching...
        found device with address 0x01
Done. Total_devices_count = 1
```

in this case script found one device with address `0x01.`


#### Get temperatures of all sensors linked to the device

You can get information about all temperatures on all connected sensors on all trunks 
using `get_temperatures`. Command line example:

`get_temperatures --uart com15 --address 1 --speed 115200`

Where:

* `--uart com15` - specifies uart name. In this case `COM15` in Windows;
* `--address 1` - specifies device address - `0x01`;
* `--speed 115200` - specifies uart speed, `115200` if default device speed, so you can 
skip this parameter.


Sample output:

```
initializing communication with device 1 [0x01]...
        ping
        initializing session id with efbab484
        session_id = efbab484
scanning for sensors...

--==Bulk data processing commands==--
Trunk #1 [0 device(s)]:
Trunk #2 [1 device(s)]:
        [0]:    24.31 C [ number: 28fffd7f90150155 ]
Trunk #3 [0 device(s)]:
Trunk #4 [0 device(s)]:
Trunk #5 [0 device(s)]:
Trunk #6 [0 device(s)]:
Trunk #7 [0 device(s)]:

--==Simple data processing commands==--
Trunk #1 [0 device(s)]:
Trunk #2 [1 device(s)]:
        [0]:    24.31 C [ number: 28fffd7f90150155 ]
Trunk #3 [0 device(s)]:
Trunk #4 [0 device(s)]:
Trunk #5 [0 device(s)]:
Trunk #6 [0 device(s)]:
Trunk #7 [0 device(s)]:

Retrieving sensors count:
        trunk #1 - 0
        trunk #2 - 1
        trunk #3 - 0
        trunk #4 - 0
        trunk #5 - 0
        trunk #6 - 0
        trunk #7 - 0
```