# VRC-T70 data exchange protocol

This document contains description of data exchange protocol for communication with VRC-T70 controller.


## 1. General information

### 1.1. About protocol
#### 1.1.1 Communication protocol

Communication protocol is binary and half-duplex. VRC-T70 device responses with response packets to each request
packets from master device (PC or other controller). So VRC-T70 device is slave for master device (for example - PC).

When transmitting value with more than one byte, it must be transferred in
[Big-endian] (https://en.wikipedia.org/wiki/Endianness#Big-endian).

Example: when transferring `0xaabbccdd` it will be transmitted in four bytes in this sequence
`{0xaa, 0xbb, 0xcc, 0xdd}`

#### 1.1.2. Network

RS-485 network can contain more than one device. Each device can be addressed using unique address (1 byte).

#### 1.1.3. Data types

Controller supports these data types:

* float - 4 bytes float value;
* uint8 - 8 bits unsigned integer value;
* uint32 - 32 bits unsigned integer value.

### 1.2. Command packet

Command packet can be transferred from master device to VRC-T70 controller. Each command packet
contains these parts:

* `address` controller address (1 byte);
* `command_id` (1 byte);
* `sequence_id` (2 bytes);
* `data_length` (1 byte);
* `<data bytes>` (N bytes, optional);
* `crc` (1 byte).

Where:

* `address` - controller address in RS485 network;
* `command_id` - command id;
* `sequence_id` - 2 bytes number which must be returned by controller in response packet;
* `data_length` - length of data segment, if not data will be provided shall be 0x00;
* `<data bytes>` - optional data if necessary (optional);
* `crc` - cyclic redundancy check for error detections till transmission.

`sequence_id` - sequence id can be used in master device to perform asynchronous behaviour. If you
don't need this functionality you can specify 0x0000 as sequence id.

Crc specification:

* CRC-8 DVB S2
* Poly  : 0xD5
* Init  : 0x00
* Revert: false
* XorOut: 0x00
* Check : 0xBC ("123456789")

Info: you can use http://www.sunshine2k.de/coding/javascript/crc/crc_js.html where you can generate
CRC predefined characteristics or define own.

Packet example:

`{0x01 0x01 0x22 0x33 0x00 0x0a}` - PING packet to device with address 0x01, no payload (data),
sequence id = 0x2233

### 1.3. Response packet

Response packet can be received from controller as a response for request packet.

Each response packet contains these parts::

* `address` controller address (1 byte);
* `event_id` (1 byte);
* `sequence_id` (2 bytes);
* `processing_result` (1 byte)
* `data_length` (1 byte);
* `<data bytes>` (N bytes, optional);
* `crc` (1 byte).

Where:
* `address` - controller address in RS485 network;
* `event_id` - must be same as command id in request packet;
* `sequence_id` - 2 bytes number which must be same as in request packet;
* `processing_result` - error code for processing;
* `data_length` - length of data segment, if not data will be provided shall be 0x00;
* `<data bytes>` - optional data if necessary (optional);
* `crc` - cyclic redundancy check for error detections till transmission.

Example:

`{0x01 0x01 0x22 0x33 0x00 0x00 0x56}` - response for PING command from controler with address 0x01,
no payload (data), processing result 0x00 (successful processing), sequence id = 0x2233

### 1.4. Processing result codes

Each request, processed by controller will achieve one of possible processing result codes:

* 0x00 - NO_ERROR - no any errors when processing request;
* 0x01 - UNKNOWN_COMMAND - unknown command;
* 0x02 - ACCESS_DENIED	access denied;
* 0x03 - INCORRECT_VALUE - incorrect value in command parameters;
* 0x04 - DS18B20_ERROR - error when reading data from DS18B20 sensor;
* 0x05 - DS18B20_BUSY - DS18B20 sensor is busy.

### 1.5. Session control

For synchronization support and session control between master device (PC or other controller)
session control was added.

It's allows to be ensured that DS18B20 indexes and addresses in arrays is same on master
controller and VRC-T70 controller.

Algorithm description. When master device want ensure that session is OK, it can request for session
id and modify behaviour depends on value returned:

* master device request for current session id `2.7. Get Session ID (0x07)`
* if session id equals zero it means that VRC-T70 controller restarted;
* if session id on master device and VRC-T70 controller is not equal it means that there is problem with session control;
* when session is not OK, new session id (not equal to zero must be specified for controller) using `Set Session ID (0x06)`
and sensors rescan shall be performed using `Rescan sensors on trunk (0x09)` for each trunk.

### 1.6. Trunks and sensors indexes and scanning logic

When VRC-T70 device starts it knows that it have 7 trunks (with indexes from 1 up to 7) with no
any known devices.

When master controller requests for sensors rescan operation on specified trunk number VRC-T70
performs sensors scan and collects information about up to 10 devices for trunk. Each sensor address
will be stored in array (which can hold max. 10 adresses) and can be accessed by index (from 0 to 9).

After trunk was scanned VRC-T70 can be requested for temperature for specific sensor by specifying
trunk number (from 1 to 7) and sensor index in array (from 0 to 9). Also, master device can request
for sensors count on specific trunk and sensor addresses on specific trunk.

## 2. Requests.

### 2.1. Ping (`0x01`)

command_id = `0x01`

PING request - can be used to check that VRC-T70 controller is connected and online.

**Data**: `none`

**Response data**: `none`

Packet example:

`0x07 0x01 0x22 0x33 0x00 0x14`

### 2.2. Get temperature value by trunk and sensor index (`0x02`)

command_id = `0x02`
Can be used to get temperature for sensor with specified index (0...9) on specified trunk (1..7)

**Possible errors**:

* `INCORRECT_VALUE` - trunk number and/or sensor index is invalid.

**Data**:

Offset | Size | Description
-- | -- | --
0x00 | 1 | trunk number (1..7)
0x01 | 1 | sensor index (0..9)


**Response data**:

Offset | Size | Description
-- | -- | -- 
0x00 | 1 | trunk number (1..7)
0x01 | 1 | sensor index (0..9)
0x02 | 1 | is device connected (1 - connection available, 0 - no connection)
0x03 | 4 | temperature (float, big endian)


### 2.3. Get temperature values for trunk (`0x03`)

command_id = `0x03`

Can be used to get temperature values for all sensord on trunk (1..7)

**Possible errors**:

* `INCORRECT_VALUE` - trunk number and/or sensor index is invalid.

**Data**:

Offset | Size | Description
0x00 | 1 | trunk number (1..7)

**Response data**:

Offset | Size | Description
-- | -- | --
0x00 | 1 | trunk number (1..7)
0x01 | 1 | is sensor connected (0x01 - connection available, 0x00 - no connection)
0x02 | 4 | temperature at sensor (4 bytes float)
... | ... | ...

`is sensor connected` and `temperature at sensor` will be repeated for each sensor at trunk.

Info: in case when 10 sensors available at trunk, response packet size can be calculated as:
* `address` (1 byte)
* `event_id` (1 byte)
* `sequence_id` (2 bytes)
* `processing_result` (1 byte)
* `data_length` (1 byte)
* `trunk_number` (1 byte)
* 10 x 5 bytes - data for all sensors (1 byte for connection flag and 4 bytes for temperature)
* `crc` (1 byte)

So max. size will be **58** bytes.

### 2.4. Get sensor unique number (`0x04`)

command_id = `0x04`

Can be uses to get sensor unique id (8 bytes) by trunk number (1..7) and sensor index (0..9)

**Possible errors**:
* `INCORRECT_VALUE` - trunk number and/or sensor index is invalid.

**Data**:

Offset | Size | Description
0x00 | 1 | trunk number (1..7)
0x01 | 1 | sensor index (0..9)

**Response data**:

Offset | Size| Description
0x00 | 1 | trunk number (1..7)
0x01 | 1 | sensor index (0..9)
0x02 | 8 | sensor unique identifier

Request example:

`0x07 0x04 0x22 0x33 0x02 0x01 0x00 0xC3`

### 2.5. Get sensor unique numbers by trunk (`0x05`)
command_id = `0x05`

Can be used to get unique addresses of all sensors at trunk (1..7)

**Possible errors**:
* `INCORRECT_VALUE` - trunk number is invalid.

**Data**:

Offset | Size | Description
0x00 | 1 | trunk number (1..7)

**Response data**:

Offset | Size | Description
0x00 | 1 | Номер магистрали (1..7)
0x01 | 8 | sensor unique number N
0x09 | 1 | is error detected when communicating with sensor (0x00 - no errors detected, 0x01 - have error)
...	| ... |...

Info: in case when 10 sensors available at trunk, response packet size can be calculated as:
* `address` (1 byte)
* `event_id` (1 byte)
* `sequence_id` (2 bytes)
* `processing_result` (1 byte)
* `data_length` (1 byte)
* `trunk_number` (1 byte)
* 10 x 9 bytes - data for all sensors (8 bytes for sensor unique address and 1 byte for error flag)
* `crc` (1 byte)

So max. size will be **98** bytes.

### 2.6. Set Session ID (`0x06`)

command_id = `0x06`

Can be used to set session id

**Data**:

Offset | Size | Description
0x00 | 4 | new session id

**Response data**:

Offset | Size | Description
0x00 | 4 | new session id

### 2.7. Get Session ID (`0x07`)

command_id = `0x07`

Can be used to get current session id

**Data**: `none`

**Response data**:

Offset | Size | Description
0x00 | 4 | session id

### 2.8. Set New Device Address (`0x08`)

command_id = `0x08`

Can be used to set new controller address. Controller address will be stored on EEPROM.

Info: when updating firmware address will be 0x01

**Data**:

Offset | Size| Description
0x00 | 1 | New controller address

**Response data**:

Offset | Size| Description
0x00 | 1 | new controller address

Warning! Controller will make response with **old** address. It means that address was successfully
updated. Next response possible only by using new address.

## 2.9. Rescan Trunk (`0x09`)

command_id = `0x09`

Scan trunk for sensors. When this command received controller will perform scanning for sensors
available at specified trunk and will store first 10 addresses in sensors array for trunk.

**Data**:

Offset | Size | Description
0x00 | 1 | trunk number (1..7)

**Possible errors**:
* `INCORRECT_VALUE` - trunk number is invalid.

**Response data**:

Offset | Size | Description
0x00 | 1| trunk number (1..7)
0x01 | 1 | sensors count at trunk (0..10)

Warning! Sensors order can be different for different calls of this command. For example one or more
sensors can be dicsonnected and/or added.

### 2.10. Get sensors count on trunk (`0x0A`)

command_id = `0x0A`

Can be used to get sensors count at trunk. This command will not require for re-scan, it just
returns length of array of sensors on trunk.

**Data**:

Offset | Size | Description
0x00 | 1 | trunk number (1..7)

**Possible errors**:
* `INCORRECT_VALUE` - trunk number is invalid.

**Response data**:

Offset | Size | Description
0x00 | 1 | trunk number (1..7)
0x01 | 1 | sensors count at trunk (0..10)


