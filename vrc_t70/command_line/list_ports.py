import serial.tools.list_ports

from .shared import init_logger


def main():
    logger = init_logger()

    ports = serial.tools.list_ports.comports()
    logger.info("found {} port(s)".format(len(ports)))
    ports = sorted(ports, key=(lambda x: x.device))
    for port in ports:
        logger.info("\t'{}' ('{}')".format(port.device, port.description))

    return 0


if __name__ == "__main__":
    res = main()
    exit(0)
