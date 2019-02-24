#!/usr/bin/env python
import threading
import time
import logging
formatter = "%(asctime)s - %(name)s (%(threadName)-10s) - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger(__name__)
def thread_one(start_event):
    logger.info("started")
    start_event.wait()
    # will be suspended until start_event is true
    logger.info("just woke up")
def thread_two(start_event):
    logger.info("started")
    # will process something...
    logger.info("processing something")
    time.sleep(2)
    logger.info("finished processing")
    logger.info("will wake up thread_one")
    start_event.set()
if __name__ == '__main__':
    start_event = threading.Event()
    t_one = threading.Thread(target=thread_one, args=[start_event]).start()
    t_two = threading.Thread(target=thread_two, args=[start_event]).start()