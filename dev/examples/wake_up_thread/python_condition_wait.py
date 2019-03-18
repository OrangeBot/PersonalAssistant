#!/usr/bin/env python
import logging
import threading

formatter = "%(asctime)s - %(name)s (%(threadName)-10s) - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger(__name__)
import time


def thread_one(start_event):
    with start_event:
        logger.info("started, waiting for 2 seconds")
        time.sleep(1)
        start_event.wait(2)
        # will be suspended until start_event is true
        logger.info("just woke up after")


def thread_two(start_event):
    with start_event:
        logger.info("started")
        # will process something...
        logger.info("Waiting for 5 seconds")
        time.sleep(5)
        logger.info("finished processing")
        logger.info("will wake up thread_one")
        start_event.notify()


if __name__ == '__main__':
    start_event = threading.Condition()
    t_one = threading.Thread(target=thread_one, args=[start_event]).start()
    t_two = threading.Thread(target=thread_two, args=[start_event]).start()
