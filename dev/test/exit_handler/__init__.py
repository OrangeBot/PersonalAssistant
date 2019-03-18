import threading
import time

from pyutils import run_bg


class ExitHandler(object):
    def __init__(self):
        self._lock = threading.RLock()
        self.active = False
        self._counter = 0

    def __call__(self, *args, **kwargs):
        print("Process 'started'")
        self.run()

    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     print("My handler, my amazing __exit__ handler works!!!")

    def __del__(self):
        print("My handler, my amazing __del__ handler works!!!")

    @property
    def active(self):
        with self._lock:
            return self._active

    @active.setter
    def active(self, active):
        with self._lock:
            self._active = active

    def run(self):
        self.active = True
        run_bg(self._run)

    def _run(self):
        while self.active:
            print("I'm running, counting seconds: {}".format(self._counter))
            time.sleep(1)
            self._counter += 1

    def shutdown(self):
        self.active = False

    def __enter__(self):
        print("Working with 'database' started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        print("Working with 'database' exited incredibly gracefully, and as a proof will count to ten")
        i = 0
        while i < 10:
            i += 1
            print(i)
            time.sleep(0.5)


if __name__ == '__main__':
    # e = ExitHandler()
    # e()
    # time.sleep(10)
    # e.shutdown()
    with ExitHandler() as e:
        print("Supposed database working")
        e()
        time.sleep(10)
        e.shutdown()
