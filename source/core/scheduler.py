# -*- coding: utf-8 -*-
# # try to emulate necessary scheduler behavior

import random
import time

import sortedcontainers
from pyutils import WARN, to_utc_seconds


class CallbackTask(object):
    def __init__(self, callback, target_time=None, task_id=None, is_recurring=True):
        self.callback = callback
        self.target_time = to_utc_seconds(target_time or time.time())
        self.id = task_id or Scheduler.generate_task_id(self)
        self.is_recurring = is_recurring

    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)


class Scheduler(object):
    _task_ids = set()

    def __init__(self):
        self._schedule = sortedcontainers.SortedDict()  # time -> (task, id)
        self._tasks = dict()  # id -> (task, timestamp)

    def add_task(self, callback, target_time=None, task_id=None, is_recurring=True):
        task = CallbackTask(callback, target_time=target_time, task_id=task_id, is_recurring=is_recurring)
        while task.target_time in self._schedule:
            WARN("Timestamp already in schedule. Incrementing by a microsecond")
            task.target_time += 1e-6
        self._schedule[task.target_time] = task
        self._tasks[task.id] = task
        return task

    def get_next_task(self):
        # type: () -> CallbackTask
        _, task = self._schedule.peekitem(0)
        return task

    def remove_task(self, task_id=None):
        if task_id is None:
            _, task = self._schedule.popitem(0)
            self._tasks.pop(task.id)  # remove first task from schedule and tasks
        else:
            task = self._tasks.pop(task_id)
            self._schedule.pop(task.target_time)
        return task

    pop = remove_task

    @classmethod
    def generate_task_id(cls, task):
        while True:
            task_id = 'task_' + str(random.randint(1, 1e9)).zfill(9)
            if task_id not in cls._task_ids:
                cls._task_ids.add(task_id)
                return task_id

    def __repr__(self):
        # todo for debug purposes.
        return repr(self._schedule)

    def get_time_to_next_event(self):
        """
        :return: time in seconds until next event.
        """
        return self.get_next_task().target_time - time.time()
