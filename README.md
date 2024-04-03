# vrc_t70

![](https://travis-ci.org/JFF-Bohdan/vrc_t70.svg?branch=master)

Documentation, samples and tools for support of VRC-T70 controller.

This repository contains:

- General information about controller.
- Protocol Description.
- Python library which can be used for communication with a VRC-T70 controller;
- Tools and examples that would use a Python library to get current sensors data and
servicing functionality.

## General information

VRC-T70 is a controller able to communicate with up to 70
widely known [DS18B20](https://www.google.com.ua/search?q=ds18b20%20tech%20spec)
sensors, divided in 7 trunks.

Each trunk can contain up to 10 DS18B20sensors, connected
using [1-Wire](https://en.wikipedia.org/wiki/1-Wire) bus.

Controller can be connected to main device (for example PC or any other controller) using
[RS485](https://en.wikipedia.org/wiki/RS-485) bus. One RS485 network can contain multiple VRC-T70
devices, so real count of connected DS18B20 can be huge and fit your requirements.

### Protocol

VRC-T70 device communicates using open protocol, which documented in
[./doc/protocol/protocol_en.md](./doc/protocol_en.md)

## Package and tools

### General information

This repository contains `vrc_t70` library that can be used in your Python Program
to communicate with VRC-T70 device(s). Also, it contains some tools which can be useful
when using VRC-T70 controller and can be used as example of an application based on `vrc_t70` library.

Available tools:

- Tool for available ports listing.
- Tool for devices searching on a RS-485 bus.
- Tool for temperature information gathering.

### Installation

#### Latest PyPI stable release

```pip install vrc_t70```

#### Latest development release on GitHub

pip install -e git+https://github.com/JFF-Bohdan/vrc_t70@master#egg=vrc_t70

### Tools

#### General information

Tools can be used only after VRC-T70 package would be installed.

Example outputs in this document may be outdated. Command line examples are revelant and up to date.

#### List all available ports

You can find information about all available COM ports in your system
by executing:

```shell
vrc-t70 list-ports
```

Sample output:

```
$ vrc-t70 list-ports
2024-03-24 22:32:10.139 | INFO     | vrc_t70.cli_tools.list_ports:list_ports:15 - Looking for available COM ports ...
2024-03-24 22:32:10.148 | INFO     | vrc_t70.cli_tools.list_ports:list_ports:22 - Found 1 port(s)
2024-03-24 22:32:10.151 | INFO     | vrc_t70.cli_tools.list_ports:list_ports:43 - Available devices:
+---+------+-------------+------+-------+---------------+--------------+------------------------+
| # | Name | Device name | VID  | PID   | Serial number | Manufacturer | Description            |
+---+------+-------------+------+-------+---------------+--------------+------------------------+
| 0 | COM4 | COM4        | 1027 | 24577 | A50285BIA     | FTDI         | USB Serial Port (COM4) |
+---+------+-------------+------+-------+---------------+--------------+------------------------+
```

#### Find device address

You can scan RS-485 network for VRC-T70 devices using `find_devices` tool. It
will ping all devices with addresses from `0x01` up to `0xfe` and will log information
about all devices online.

Example command line (find devices with any address, can take ~1.5 minutes for execution):

`find_devices --uart com15 --delay 0.1`

Where:

* `--uart com15` - specifies uart name. In this case `COM15` in Windows;
* `--delay 0.1` - specifis delay of `0.1` second before sending ping request to
device with next address.

Example:

`find_devices --uart com15 --min 1 --max 10`

Where:
* `--min 1` - minimal device address to check;
* `--max 10` - maximal device address to check.

Sample output:

```
> find_devices --uart com15 --min 1 --max 10
2019-06-17 00:13:59,128 - temp reader - INFO - Searching...
        found device with address 0x01
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:04<00:00,  2.26rqs/s[{'devices': 1}]] 2019-06-17 00:14:03,298 - temp reader - INFO - :
+-----------------+----------------+
| Timestamp found | Device Address |
+-----------------+----------------+
| 0.06            | 1 [0x01]       |
+-----------------+----------------+
2019-06-17 00:14:03,302 - temp reader - INFO - Done. Total_devices_count = 0 (Spent time: 4.17)
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
> get_temperatures --uart com15 --address 1 --speed 115200
2019-06-17 00:16:04,080 - temp reader - DEBUG - app started
2019-06-17 00:16:04,095 - temp reader - INFO - initializing communication with device 1 [0x01]...
2019-06-17 00:16:04,096 - temp reader - INFO -  ping
2019-06-17 00:16:04,159 - temp reader - DEBUG -         initializing session id with 3a9011c5
2019-06-17 00:16:04,349 - temp reader - DEBUG -         session_id = 3a9011c5
2019-06-17 00:16:04,350 - temp reader - DEBUG - scanning for sensors on trunks...
2019-06-17 00:16:04,351 - temp reader - INFO - Rescanning devices on trunks
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00,  7.81trunsk/s] 2019-06-17 00:16:05,261 - temp reader - INFO - sensors per trunks:
+------------+---------------+
| Trunk Name | Sensors Count |
+------------+---------------+
| Trunk-2    | 1             |
+------------+---------------+

2019-06-17 00:16:05,262 - temp reader - INFO - bulk data processing commands
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:01<00:00,  5.27trunks/s] 2019-06-17 00:16:06,616 - temp reader - INFO - data for Trunk-2:
+-------+-------------+------------------+
| Index | Temperature | Address          |
+-------+-------------+------------------+
| 0     | 29.12       | 28ff0930901504a9 |
+-------+-------------+------------------+

2019-06-17 00:16:06,617 - temp reader - INFO - simple data processing commands
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 32.11trunk/s] 2019-06-17 00:16:06,840 - temp reader - INFO - data for Trunk-2:
+-------+-------------+------------------+
| Index | Temperature | Address          |
+-------+-------------+------------------+
| 0     | 29.12       | 28ff0930901504a9 |
+-------+-------------+------------------+

2019-06-17 00:16:06,841 - temp reader - INFO - retrieving sensors count
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 10.56trunks/s] 2019-06-17 00:16:07,508 - temp reader - INFO - sensors per trunks:
+------------+---------------+
| Trunk Name | Sensors Count |
+------------+---------------+
| Trunk-2    | 1             |
+------------+---------------+

2019-06-17 00:16:07,621 - temp reader - INFO - application finished
```
