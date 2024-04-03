# VRC-T70 data exchange protocol

This document contains description of data exchange protocol for communication with VRC-T70 controller.

## 1. General information

### 1.1. About protocol

#### 1.1.1 Communication protocol

Communication protocol is binary and half-duplex. VRC-T70 device responds with response packets
to each request packet from main device (PC or other controller). So VRC-T70 device acts as a
node for main device.

When transmitting value with more than one byte, it must be transferred in
[Big-endian] (https://en.wikipedia.org/wiki/Endianness#Big-endian).

Example: when transferring `0xaabbccdd` it will be transmitted in four bytes in this sequence
`[0xaa, 0xbb, 0xcc, 0xdd]`

#### 1.1.2. Network

[RS-485](https://en.wikipedia.org/wiki/RS-485) network can contain multiple devices.
Each device can be addressed using unique address (1 byte).

#### 1.1.3. Data types

Controller supports such data types:

- `float` - 4 bytes float value.
- `uint_8` - 8 bits unsigned integer value.
- `uint_16` - 16 bits unsigned integer value.
(TODO: check if we need it)
- `uint_32` - 32 bits unsigned integer value.

### 1.2. Request packet

TODO: make it a table

Request packet can be transferred from main device to VRC-T70 controller. Each request packet
contains these parts:

- `address` controller address (1 byte);
- `request_id` (1 byte);
- `sequence_id` (2 bytes);
- `data_length` (1 byte);
- `<data bytes>` (N bytes, optional);
- `crc` (1 byte).

Where:

- `address` - controller address in RS485 network;
- `request_id` - request id;
- `sequence_id` - 2 bytes number which must be returned by controller in a response packet;
- `data_length` - length of data segment, if not data will be provided should be `0x00`;
- `<data bytes>` - data bytes (optional);
- `crc` - cyclic redundancy check for error detections in transmission.

`sequence_id` - sequence id can be used in main device to perform asynchronous behaviour. If you
don't need this functionality you can specify `0x0000` as sequence id.

Crc specification:

- CRC-8 DVB S2
- Poly  : 0xD5
- Init  : 0x00
- Revert: false
- XorOut: 0x00
- Check : 0xBC ("123456789")

Info: you can use http://www.sunshine2k.de/coding/javascript/crc/crc_js.html where you can generate
CRC predefined characteristics or define own.

Packet example:

`[0x01, 0x01, 0x22, 0x33, 0x00, 0x0a]` - PING packet (request id `0x01`)
to a device with address `0x01`, without payload and with sequence id `0x2233` and crc `0x0a`

### 1.3. Response packet

Response packet can be received from controller as a response for a request packet.

Each response packet contains these parts:

Offset   | Name                | Size | Data type | Description
--       |  --                 | --   | --        | --
0x00     | `address`           | 1    | uint_8    | VRC-T70 controller address
0x01     | `event_id`          | 1    | uint_8    | Event id, must be same as request id in a request packet
0x02     | `sequence_id`       | 2    | uint_16   | Sequence id, must be same as in a request packet
0x04     | `processing_result` | 1    | uint_8    | Error code for request processing.
0x05     | `payload_length`    | 1    | uint_8    | Length of data payload. If no data should be `0x00`.
0x06     | `payload`           | N    | array     | Array of bytes which represent payload
0x07 + N | `crc`               | 1    | uint_8    | CRC of a packet (cyclic redundancy check) for error detections till transmission.


Example:

`[0x01, 0x01, 0x22, 0x33, 0x00, 0x00, 0x56]` - response for PING request (request id `0x01`)
from a controler with address `0x01`, without payload (data),
processing result `0x00` (successful processing), sequence id = `0x2233` and crc `0x56`

### 1.4. Processing result codes

Each request, processed by controller will achieve one of possible processing result codes:

- `0x00` - `NO_ERROR` - no any errors when processing request;
- `0x01` - `UNKNOWN_REQUEST` - unknown request;
- `0x02` - `ACCESS_DENIED`	access denied;
- `0x03` - `INCORRECT_VALUE` - incorrect value in request parameters;
- `0x04` - `DS18B20_ERROR` - error when reading data from DS18B20 sensor;
- `0x05` - `DS18B20_BUSY` - DS18B20 sensor is busy.

### 1.5. Session control

For synchronization support and session control between main device (PC or other controller)
session control is supported.

It's allows to be sure that DS18B20 indexes and addresses in arrays are same on main
device and VRC-T70 controller.

#### Algorithm description.

When main device wants to ensure that session is OK, it can request for
session id and modify behaviour depends on value received.

Algorithm:

- Main device requests for current session id `Get session id (0x07)`.
- If session id equals to zero (`0x00`) it means that VRC-T70 controller has
been restarted and there is no session configured.
- If session id on main device and VRC-T70 controller are not equal it means
that there is problem with session control and session needs to be restarted.
- When session is not OK, new session id (not equal to zero) must be specified on
a controller by using `Set session id (0x06)` and sensors rescan
should be performed using `Rescan sensors on trunk (0x09)` for each trunk.

### 1.6. Trunks and sensors indexes and scanning logic

When VRC-T70 device starts it knows that it has 7 trunks (with indexes from 1 up to 7)
with no any known device.

When main device requests for sensors rescan operation on a specified trunk number VRC-T70
performs scan operation and collects information about for up to 10 sensors per trunk. Each
sensor address will be stored in an array (which can hold up to 10 adresses) and sensors data
can  be accessed by an index (from 0 to 9).

Each sensor on each trunk will be requested for temperature by controller every 100 ms.

After trunk would be scanned for sensors information VRC-T70 can be requested for
temperature on specific sensor by specifying trunk number (from 1 to 7) and sensor index
in array (from 0 to 9). Also, main device can request for sensors count on a specific
trunk and sensors unique addresses on a specific trunk.

Bulk operations are also supported, controller can be requested for
temperatures and/or unique addresses on all sensors on any trunk.

So, possible indexes will be:

- possible trunk index from 1 up to 7.
- possible sensor index from 0 to 9.


Example main device logic after start can be like:

- Ensure that VRC-T70 is available on RS 485 bus (can use `PING`
request to achieve this). Please take a note, that it's possible to
have multiple VRC-T70 devices on a same RS-485 bus.
- Initialize session id controller (use `Set session id` request).
- Initialize re-scan of sensors on all necessary trunks (for example from 1 up to 7).
(use `Rescan sensors on trunk` request).
- Read sensors unique addresses (one by one using `Get sensor unique address` or bulk by
using `Get sensor unique addresses on trunk`).
- Perform repeated reading of session id (use `Get session id`) and temperatures on
sensors (one by one using `Get temperature on sensor` or using bulk
reading `Get temperature values on trunk`)

## 2. Requests.

### 2.1. Ping (`0x01`)

Request id = `0x01`

PING request - can be used to check that VRC-T70 controller is connected and online.

**Data**: `none`

**Response data**: `none`

Request packet example:

`0x07 0x01 0x22 0x33 0x00 0x14`

(PING request to device with address `0x07` with sequence id `0x2233`, no payload)

TODO: add example of response

### 2.2. Get temperature on a sensor (`0x02`)

Request id = `0x02`
Can be used to get temperature for sensor with specified index (0...9) on a
specified trunk (1..7)

**Possible errors**:

- `INCORRECT_VALUE` - trunk number and/or sensor index is invalid.

**Data**:

Offset | Size | Description
   --  |  --  | --
0x00   |  1   | Trunk number (1..7)
0x01   |  1   | Sensor index (0..9)

**Response data**:

Offset | Size | Description
   --  |  --  | --
0x00   |   1  | Trunk number (1..7)
0x01   |   1  | Sensor index (0..9)
0x02   |   1  | Is sensor connected (1 - connection available, 0 - no connection)
0x03   |   4  | Temperature (float, big endian)

### 2.3. Get temperature values on a trunk (`0x03`)

Request id = `0x03`

Can be used to get temperature values for all sensors on a trunk (1..7)

**Possible errors**:

- `INCORRECT_VALUE` - trunk number and/or sensor index is invalid.

**Data**:

Offset | Size | Description
  --   |  --  | --
0x00   |   1  | Trunk number (1..7)

**Response data**:

Offset | Size | Description
  --   |  --  | --
0x00   |   1  | Trunk number (1..7)
0x01   |   1  | Is sensor connected (0x01 - connection available, 0x00 - no connection)
0x02   |   4  | Temperature at sensor (4 bytes float)
...    |  ... | ...

`is sensor connected` and `temperature at sensor` will be repeated for each
sensor at a trunk.

Info: in case when 10 sensors available at trunk, response packet size can be calculated as:

- `address` (1 byte)
- `event_id` (1 byte)
- `sequence_id` (2 bytes)
- `processing_result` (1 byte)
- `data_length` (1 byte)
- `trunk_number` (1 byte)
- 10 x 5 bytes - data for all sensors (1 byte for connection flag and 4 bytes for temperature)
- `crc` (1 byte)

So max. size would be `58` bytes.

### 2.4. Get sensor unique addresses (`0x04`)

Request id = `0x04`

Can be uses to get a sensor unique addresses (8 bytes) by trunk number
(1..7) and sensor index (0..9)

**Possible errors**:

- `INCORRECT_VALUE` - trunk number and/or sensor index is invalid.

**Data**:

Offset | Size | Description
  --   |  --  | --
0x00   |   1  | Trunk number (1..7)
0x01   |   1  | Sensor index (0..9)

**Response data**:

Offset | Size | Description
--     |  --  | --
0x00   |  1   | Trunk number (1..7)
0x01   |  1   | Sensor index (0..9)
0x02   |  8   | Sensor unique address

Request example:

`0x07 0x04 0x22 0x33 0x02 0x01 0x00 0xC3`

### 2.5. Get sensor unique addresses on trunk (`0x05`)

Request id = `0x05`

Can be used to get unique addresses of all sensors at trunk (1..7)

**Possible errors**:

- `INCORRECT_VALUE` - trunk number is invalid.

**Data**:

Offset | Size | Description
  --   |  --  | --
0x00   |   1  | Trunk number (1..7)

**Response data**:

Offset | Size | Description
  --   |  --  | --
0x00   |  1   | Trunk number (1..7)
0x01   |  8   | Sensor unique addresses N
0x09   |  1   | Is error detected when communicating with sensor (0x00 - no errors detected, 0x01 - have error)
...	   | ...  | ...

Info: in case when 10 sensors available at trunk, response packet size can be calculated as:
- `address` (1 byte)
- `event_id` (1 byte)
- `sequence_id` (2 bytes)
- `processing_result` (1 byte)
- `data_length` (1 byte)
- `trunk_number` (1 byte)
- 10 x 9 bytes - data for all sensors (8 bytes for sensor unique address and 1 byte for error flag)
- `crc` (1 byte)

So max. size will be `98` bytes.

### 2.6. Set Session Id (`0x06`)

Request id = `0x06`

Can be used to set session id

**Data**:

Offset | Size | Description
  --   | --   | --
0x00   |  4   | New session id

**Response data**:

Offset | Size | Description
  --   |  --  | --
0x00   |  4   | New session id

### 2.7. Get session id (`0x07`)

Request id = `0x07`

Can be used to get current session id

**Data**: `none`

**Response data**:

Offset | Size | Description
--     |  --  | --
0x00   |   4  | Session id

### 2.8. Set new device address (`0x08`)

Request id = `0x08`

Can be used to set new controller address. Controller address will be stored
on EEPROM an as a result, address information will survive device restart
and/or power loss.

Info: after updating firmware address will be `0x01`

**Data**:

Offset | Size| Description
--     | --  | --
0x00   |  1  | New controller address

**Response data**:

Offset | Size| Description
   --  |  -- | --
0x00   |  1  | New controller address

Warning! Controller will make response with **old** address. It means that
address was successfully updated. Next request/response cycle would be possible
only by using new address.

## 2.9. Rescan sensors on a trunk (`0x09`)

Request id = `0x09`

Can be used to scan trunk for sensors. When this request is received
controller will perform scanning for sensors available at specified trunk
and will store first 10 addresses in sensors array for a trunk.

**Data**:

Offset | Size | Description
--     |  --  | --
0x00   |  1   | Trunk number (1..7)

**Possible errors**:

- `INCORRECT_VALUE` - trunk number is invalid.

**Response data**:

Offset | Size | Description
--     | --   | --
0x00   | 1    | Trunk number (1..7)
0x01   | 1    | Sensors count at trunk (0..10)

Warning! Sensors order can be different for different calls of this request.
For example one or more sensors can be disconnected and/or added.

### 2.10. Get sensors count on a trunk (`0x0A`)

Request id = `0x0A`

Can be used to get sensors count at a trunk. This request will not perform
re-scan, it just returns length of array with sensors on trunk.

**Data**:

Offset | Size | Description
  --   |  --  | --
0x00   | 1    | Trunk number (1..7)

**Possible errors**:

- `INCORRECT_VALUE` - trunk number is invalid.

**Response data**:

Offset | Size | Description
--     | --   | --
0x00   | 1    | Trunk number (1..7)
0x01   | 1    | Sensors count on trunk (0..10)
