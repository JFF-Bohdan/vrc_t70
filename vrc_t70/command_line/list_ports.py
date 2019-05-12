import sys

from loguru import logger

import serial.tools.list_ports


def main():
    logger.remove()

    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} {message}",
        level="INFO",
        backtrace=True,
        diagnose=True
    )

    ports = serial.tools.list_ports.comports()
    logger.info("found {} port(s)".format(len(ports)))
    ports = sorted(ports, key=(lambda x: x.device))
    for port in ports:
        logger.info("\t'{}' ('{}')".format(port.device, port.description))

    return 0


if __name__ == "__main__":
    res = main()
    exit(0)
