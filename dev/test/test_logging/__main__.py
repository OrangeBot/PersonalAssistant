import logging

from dev.test.test_logging.lib import log_something

if __name__ == '__main__':
    logging.info("But does this work also?")
    log_something()
    logging.info("But does this work also? ______2")
