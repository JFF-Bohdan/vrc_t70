# Common bytes
# VRC-T70 Controlled address is 0x08
# Sequence id 0x2233

PING_REQUEST = bytes([0x08, 0x01, 0x22, 0x33, 0x00, 0x27])
PING_RESPONSE = bytes([0x08, 0x01, 0x22, 0x33, 0x00, 0x00, 0xf0])
PING_RESPONSE_WITH_ERROR_CODE = bytes([0x08, 0x01, 0x22, 0x33, 0xdd, 0x00, 0x2b])

GET_SESSION_ID_REQUEST = bytes([0x08, 0x07, 0x22, 0x33, 0x00, 0x6c])
# Session id 0xdeadbeef
GET_SESSION_ID_RESPONSE = bytes([0x08, 0x07, 0x22, 0x33, 0x00, 0x04, 0xde, 0xad, 0xbe, 0xef, 0x0b])

# Session id is 0xdeadbeef
SET_SESSION_ID_REQUEST = bytes([0x08, 0x06, 0x22, 0x33, 0x04, 0xde, 0xad, 0xbe, 0xef, 0x99])
# Session id 0xdeadbeef
SET_SESSION_ID_RESPONSE = bytes([0x08, 0x06, 0x22, 0x33, 0x00, 0x04, 0xde, 0xad, 0xbe, 0xef, 0x3c])

# Trunk number 4
RESCAN_SENSORS_ON_TRUNK_REQUEST = bytes([0x08, 0x09, 0x22, 0x33, 0x01, 0x04, 0x9e])
# Trunk number 4, sensors count is 3
RESCAN_SENSORS_ON_TRUNK_RESPONSE = bytes([0x08, 0x09, 0x22, 0x33, 0x00, 0x02, 0x04, 0x03, 0x1a])

# Trunk number 4
GET_SENSORS_COUNT_ON_TRUNK_REQUEST = bytes([0x08, 0x0a, 0x22, 0x33, 0x01, 0x04, 0x91])
# Trunk number 4, sensors count is 3
GET_SENSORS_COUNT_ON_TRUNK_RESPONSE = bytes([0x08, 0x0a, 0x22, 0x33, 0x00, 0x02, 0x04, 0x03, 0x73])

# Trunk number 4, sensor index 5
GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_REQUEST = bytes([0x08, 0x02, 0x22, 0x33, 0x02, 0x04, 0x05, 0x2d])
# Trunk number 4, sensor index 5, temperature 19.98
GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_RESPONSE = bytes(
    [
        0x08,
        0x02,
        0x22, 0x33,
        0x00,
        0x07,
        0x04,
        0x05,
        0x01,
        0x55, 0xd5, 0x9f, 0x41,  # 19.97916603088379 C
        0xdd
    ]
)
# Trunk number 4, sensor index 5, temperature is not provided because of error
GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_RESPONSE_V2 = bytes(
    [
        0x08,
        0x02,
        0x22, 0x33,
        0x00,
        0x07,
        0x04,
        0x05,
        0x00,
        0x55, 0xd5, 0x9f, 0x41,  # 19.97916603088379 C
        0x6b
    ]
)

# Trunk number 4, sensor index 5
GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_REQUEST = bytes([0x08, 0x04, 0x22, 0x33, 0x02, 0x04, 0x05, 0xd7])
# Trunk number 4, sensor index 5, sensor address 0x28ff2c7d901501c1
GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE = bytes(
    [
        0x08,
        0x04,
        0x22, 0x33,
        0x00,
        0x0a,
        0x04,
        0x05,
        0x28, 0xff, 0x2c, 0x7d, 0x90, 0x15, 0x01, 0xc1,
        0x0e
    ]
)

# Trunk number 4
GET_TEMPERATURES_ON_TRUNK_REQUEST = bytes([0x08, 0x03, 0x22, 0x33, 0x01, 0x04, 0xbc])
# Trunk number 4, 1 sensor with temperature 20.94 C
GET_TEMPERATURES_ON_TRUNK_RESPONSE_1_SENSOR = bytes(
    [
        0x08,
        0x03,
        0x22, 0x33,
        0x00,
        0x06,
        0x04,
        0x01,
        0x00, 0x80, 0xa7, 0x41,  # 20.94C

        0x57
    ]
)
# Trunk number 4, 4 sensors with temperatures:
#   - 19.9792 C
#   - 20.94 C
#   - 18.44C
#   - None (not connected anymore)
#   - 19.62 C
GET_TEMPERATURES_ON_TRUNK_RESPONSE_5_SENSORS = bytes(
    [
        0x08,
        0x03,
        0x22, 0x33,
        0x00,
        0x1a,
        0x04,

        0x01,
        0x55, 0xd5, 0x9f, 0x41,  # 19.9792 C

        0x01,
        0x00, 0x80, 0xa7, 0x41,  # 20.94C

        0x01,
        0x00, 0x80, 0x93, 0x41,  # 18.44C

        0x00,
        0xff, 0xff, 0xff, 0xff,  # None

        0x01,
        0x00, 0x00, 0x9d, 0x41,  # 19.62C

        0xe4
    ]
)


# Trunk number 4
GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_REQUEST = bytes([0x08, 0x05, 0x22, 0x33, 0x01, 0x04, 0xa2])
# Trunk number 4, 1 sensor with address 0x28ff2c7d901501c1
GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_1_SENSOR = bytes(
    [
        0x08,
        0x05,
        0x22, 0x33,
        0x00,
        0x0a,
        0x04,

        0x28, 0xff, 0x2c, 0x7d, 0x90, 0x15, 0x01, 0xc1,
        0x00,
        0x1b
    ]
)
# Trunk number 4, 4 sensors with addresses:
# - 0x28ff2c7d901501c1 (no error)
# - 0x28fffd7f90150155 (no error)
# - 0x28ff6f31901504ab (no error)
# - 0x28ff0930901504a9 (has error)
GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_4_SENSORS = bytes(
    [
        0x08,
        0x05,
        0x22, 0x33,
        0x00,
        0x25,
        0x04,

        0x28, 0xff, 0x2c, 0x7d, 0x90, 0x15, 0x01, 0xc1,
        0x00,

        0x28, 0xff, 0xfd, 0x7f, 0x90, 0x15, 0x01, 0x55,
        0x00,

        0x28, 0xff, 0x6f, 0x31, 0x90, 0x15, 0x04, 0xab,
        0x00,

        0x28, 0xff, 0x09, 0x30, 0x90, 0x15, 0x04, 0xa9,
        0x01,

        0xd4
    ]
)
# Trunk number 4, 10 sensors with addresses:
# - 0x54000001f15c5728 (no error)
# - 0xf8031674dc8aff28 (has error)
# - 0x66041674b616ff28 (no error)
# - 0xf5031674e23eff28 (has error)
# - 0x9f0416805499ff28 (no error)
# - 0x87031674b483ff28 (no error)
# - 0x2818b4490c00007c (has error)
# - 0x28cc19490c0000bb (has error)
# - 0x2819ef480c000021 (has error)
# - 0x28c6de49f6b63c55 (no error)

GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_10_SENSORS = bytes(
    [
        0x08,
        0x05,
        0x22, 0x33,
        0x00,
        0x5b,
        0x04,

        0x54, 0x00, 0x00, 0x01, 0xf1, 0x5c, 0x57, 0x28,
        0x00,
        0xf8, 0x03, 0x16, 0x74, 0xdc, 0x8a, 0xff, 0x28,
        0x01,
        0x66, 0x04, 0x16, 0x74, 0xb6, 0x16, 0xff, 0x28,
        0x00,
        0xf5, 0x03, 0x16, 0x74, 0xe2, 0x3e, 0xff, 0x28,
        0x01,
        0x9f, 0x04, 0x16, 0x80, 0x54, 0x99, 0xff, 0x28,
        0x00,
        0x87, 0x03, 0x16, 0x74, 0xb4, 0x83, 0xff, 0x28,
        0x00,
        0x28, 0x18, 0xb4, 0x49, 0x0c, 0x00, 0x00, 0x7c,
        0x01,
        0x28, 0xcc, 0x19, 0x49, 0x0c, 0x00, 0x00, 0xbb,
        0x01,
        0x28, 0x19, 0xef, 0x48, 0x0c, 0x00, 0x00, 0x21,
        0x01,
        0x28, 0xc6, 0xde, 0x49, 0xf6, 0xb6, 0x3c, 0x55,
        0x00,
        0x81
    ]
)

# New controller address is 42
SET_CONTROLLER_NEW_ADDRESS_REQUEST = bytes([0x08, 0x08, 0x22, 0x33, 0x01, 0x2a, 0x24])

# New controller address is 42
SET_CONTROLLER_NEW_ADDRESS_RESPONSE = bytes([0x08, 0x08, 0x22, 0x33, 0x00, 0x01, 0x2a, 0xdb])