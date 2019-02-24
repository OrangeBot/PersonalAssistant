# The answer is to create a condition object and use its wait() method with the optional timeout instead of time.sleep().
# If the thread needs to be woken prior to the timeout, call the notify() method of the condition object.

import threading
import time

cond = threading.Condition()


def custom_waiter():
    print("Let the wait being")
    if cond.wait(timeout=10):
        print("Condition true")
    else:
        print("Condition false")


if __name__ == "__main__":
    t = threading.Thread(target=custom_waiter)
    t.run()
    for i in range(10):
        print("i: ", i)
        time.sleep(1)