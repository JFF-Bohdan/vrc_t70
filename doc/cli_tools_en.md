# CLI tools for VRC-T70 controller

This package contains several CLI tools to show how to work with VRC-T70
controllers.


## List all available ports

You can find information about all available COM ports in your system
by executing:

```shell
vrc-t70 list-ports
```

Sample output:

```
$ vrc-t70 list-ports
2024-04-03 21:27:19.836 | INFO     | vrc_t70.cli_tools.list_ports:list_ports:16 - Looking for available COM ports ...
2024-04-03 21:27:19.849 | INFO     | vrc_t70.cli_tools.list_ports:list_ports:23 - Found 1 port(s)
2024-04-03 21:27:19.849 | INFO     | vrc_t70.cli_tools.list_ports:list_ports:44 - Available devices:
+---+------+-------------+------+-------+---------------+--------------+------------------------+
| # | Name | Device name | VID  | PID   | Serial number | Manufacturer | Description            |
+---+------+-------------+------+-------+---------------+--------------+------------------------+
| 0 | COM4 | COM4        | 1027 | 24577 | A50285BIA     | FTDI         | USB Serial Port (COM4) |
+---+------+-------------+------+-------+---------------+--------------+------------------------+
```

## Find connected controllers

You can scan RS-485 network for VRC-T70 controllers using `find_devices` tool.
It's able to ping controllers with addresses from minimal (`0x01`) up
to maximum (`0xfe`) and will print information about all devices available.

Example command line (find devices with any address, can take ~1.5 minutes for execution):

```
vrc-t70 find-controllers --port com4 -m 1 -x 254
```

Where:

- `--port com4` - specifies UART name. In this case `COM4` in Windows;
- `-m 1` - minimal controller address
- `-x 254` - max controller address

Example:

`find_devices --uart com15 --min 1 --max 10`

Where:
* `--min 1` - minimal device address to check;
* `--max 10` - maximal device address to check.

Sample output:

```
$ vrc-t70 find-controllers --port com4 -m 1 -x 254

<skipped>

2024-04-03 21:29:12.590 | INFO     | vrc_t70.cli_tools.find_controllers:find_controllers:166 - Scan finished in 1 minute, 24 seconds and 860 milliseconds
2024-04-03 21:29:12.590 | INFO     | vrc_t70.cli_tools.find_controllers:find_controllers:171 - Found devices with addresses:
+-------------------+---------------+
| Address (decimal) | Address (hex) |
+-------------------+---------------+
| 1                 | 0x01          |
+-------------------+---------------+
2024-04-03 21:29:12.590 | INFO     | vrc_t70.cli_tools.find_controllers:find_controllers:178 - Closing UART
```

in this case script found one device with address `0x01.`

## Demo application to show

This application shows how to use available classes which can be used
to communicate with VRC-T70 device.

Example command line:

```
$ vrc-t70 demo-app-1 --port com4 --address 1
```

Example output:

```
$ vrc-t70 demo-app-1 --port com4 --address 1

<skipped>

2024-04-03 21:39:58.762 | INFO     | vrc_t70.cli_tools.demo_app:print_scan_results:191 - Scan results:
+-------+--------------+------------------+-------------+
| Trunk | Sensor index | Sensor address   | Temperature |
+-------+--------------+------------------+-------------+
| 1     | N/A          | N/A              | N/A         |
| 2     | 0            | 28ff0930901504a9 | 17.88       |
| 3     | 0            | 28fffd7f90150155 | 20.38       |
| 4     | 0            | 28ff6f31901504ab | 20.12       |
| 5     | 0            | 28ff2c7d901501c1 | 22.50       |
| 6     | N/A          | N/A              | N/A         |
| 7     | N/A          | N/A              | N/A         |
+-------+--------------+------------------+-------------+
2024-04-03 21:39:58.768 | INFO     | vrc_t70.cli_tools.demo_app:demo_app:245 - Batched scan is finished in 3 seconds and 203 milliseconds
2024-04-03 21:39:58.770 | INFO     | vrc_t70.cli_tools.demo_app:demo_app:246 - Device info: VrcT70DeviceInfo(address=1, session_id=3405691582, trunks={1: TrunkInfo(sensors_count=0, sensors_addresses={}, sensors_temperatures={}), 2: TrunkInfo(sensors_count=1, sensors_addresses={0: 2954089984758711465}, sensors_temperatures={0: 17.875}), 3: TrunkInfo(sensors_count=1, sensors_addresses={0: 2954358604898304341}, sensors_temperatures={0: 20.41666603088379}), 4: TrunkInfo(sensors_count=1, sensors_addresses={0: 2954202139239711915}, sensors_temperatures={0: 20.125}), 5: TrunkInfo(sensors_count=1, sensors_addresses={0: 2954128798378164673}, sensors_temperatures={0: 22.5}), 6: TrunkInfo(sensors_count=0, sensors_addresses={}, sensors_temperatures={}), 7: TrunkInfo(sensors_count=0, sensors_addresses={}, sensors_temperatures={})})
2024-04-03 21:39:58.772 | INFO     | vrc_t70.cli_tools.demo_app:print_scan_results:159 - Scan finished for controller 0x01 with session id 0xcafebabe in 3 seconds and 203 milliseconds
2024-04-03 21:39:58.774 | INFO     | vrc_t70.cli_tools.demo_app:print_scan_results:191 - Scan results:
+-------+--------------+------------------+-------------+
| Trunk | Sensor index | Sensor address   | Temperature |
+-------+--------------+------------------+-------------+
| 1     | N/A          | N/A              | N/A         |
| 2     | 0            | 28ff0930901504a9 | 17.88       |
| 3     | 0            | 28fffd7f90150155 | 20.42       |
| 4     | 0            | 28ff6f31901504ab | 20.12       |
| 5     | 0            | 28ff2c7d901501c1 | 22.50       |
| 6     | N/A          | N/A              | N/A         |
| 7     | N/A          | N/A              | N/A         |
+-------+--------------+------------------+-------------+
2024-04-03 21:39:58.778 | INFO     | vrc_t70.cli_tools.demo_app:demo_app:251 - Closing UART
```
