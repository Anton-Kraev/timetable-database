import logging


def get_logger(logger_name: str) -> logging.Logger:
    """Function for getting logger
    :param logger_name: logger name"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=f"{logger_name}.log", mode='w+')
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
