import argparse
import configparser
import os

from loguru import logger


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="configuration file path"
    )
    args = parser.parse_args()
    config = configparser.RawConfigParser()

    if not os.path.exists(args.config):
        logger.error("can't find file: {}".format(args.config))
        return None

    try:
        config.read(args.config)
    except BaseException as e:
        logger.exception("can't read config: {}".format(e))
        return None

    return config
