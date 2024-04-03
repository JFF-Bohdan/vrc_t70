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

Each trunk can contain up to 10 DS18B20 sensors, connected
using [1-Wire](https://en.wikipedia.org/wiki/1-Wire) bus.

Controller can be connected to main device (for example PC or any other controller) using
[RS485](https://en.wikipedia.org/wiki/RS-485) bus. One RS485 network can contain multiple VRC-T70
devices, so real count of connected DS18B20 can be huge and fit your requirements.

### Protocol

VRC-T70 device communicates using open protocol, which documented in
[protocol description](./doc/protocol_en.md)


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

```
pip install -e git+https://github.com/JFF-Bohdan/vrc_t70@master#egg=vrc_t70
```

### Tools

#### General information

Tools can be used only after VRC-T70 package would be installed.

Example outputs in this document may be outdated. Command line examples should be
revelant and up to date.

Please find more details about available CLI tools in
[CLI tools description](./doc/cli_tools_en.md)
