import logging
from util.enum import Enum


class LogLevel(Enum):
    Debug = 'debug'
    Info = 'info'
    Warning = 'warning'
    Error = 'error'
    Critical = 'critical'


def get_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(levelname)s][%(filename)s:%(lineno)d] %(message)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger
