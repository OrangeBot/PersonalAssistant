import logging


# logging.basicConfig(level=logging.DEBUG)


def log_something():
    logging.debug('This message should go to the log file')
    logging.info('So should this')
    logging.warning('And this, too')
