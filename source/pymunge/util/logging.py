import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(levelname)s][%(filename)s:%(lineno)d] %(message)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger
