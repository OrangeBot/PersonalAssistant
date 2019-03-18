# # try to emulate necessary scheduler behavior

import numbers
import random
import time

import dateutil
import six
import sortedcontainers
from pyutils import Namespace, WARN


def is_utc_seconds(t):
    return isinstance(t, numbers.Number) and 315522000.0 < t < 2524597200.0  # 1 Jan 1980 - 1 Jan 2050


def to_utc_seconds(t):
    # todo: if it's a string - parse or convert to float
    if isinstance(t, six.string_types):
        try:
            t = float(t)
        except ValueError:
            t = dateutil.parser.parse(t).timestamp()
    if is_utc_seconds(t):
        return t
    if is_utc_seconds(t / 1000):
        return t / 1000
    if is_utc_seconds(t / 1e6):
        return t / 1e6
    raise ValueError("{} is not recognized time format".format(t))


class Scheduler(object):
    def __init__(self):
        self._schedule = sortedcontainers.SortedDict()  # time -> (task, id)
        self._tasks = dict()  # id -> (task, timestamp)

    def add_task(self, task, timestamp=None, task_id=None):
        task_id = task_id or self.getnerate_task_id(task)
        timestamp = to_utc_seconds(timestamp or time.time())
        while timestamp in self._schedule:
            WARN("Timestamp already in schedule. Incrementing by a microsecond")
            timestamp += 1e-6
        self._schedule[timestamp] = Namespace(task=task, task_id=task_id)
        self._tasks[task_id] = Namespace(task=task, timestamp=timestamp)
        return Namespace(task_id=task_id, timestamp=timestamp)

    def get_next_task(self):
        return self._schedule.peekitem(0)

    def remove_task(self, task_id=None):
        if task_id is None:
            item = self._schedule.popitem(0)
            self._tasks.pop(item[1].task_id)  # remove first task from schedule and tasks
            return item
        else:
            return self._schedule.pop(self._tasks.pop(task_id))  # remove

    pop = remove_task

    def getnerate_task_id(self, task):
        while True:
            task_id = str(random.randint(1, 1e9)).zfill(9)
            if task_id not in self._tasks:
                return task_id

    def __repr__(self):
        # todo for debug purposes.
        return repr(self._schedule)
