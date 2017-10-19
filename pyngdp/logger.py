import logging


def build_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel('INFO')

    return logger
