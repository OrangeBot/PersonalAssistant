# -*- coding: utf-8 -*-
import logging
# import argparse
import os
import threading

from pyutils import run_bg
from typing import Iterable

from proto.config_pb2 import TPersonalAssistantConfig
from scheduler import Scheduler
from source.lib.common import load_config
from source.plugins import Uid, Task, Folder, Todoist, Plugin, CLI

LOG = logging.getLogger()


class PersonalAssistantSession(object):
    def __init__(self, pa):
        """
        :param pa:
        :type pa: source.core.PersonalAssistant
        """
        self.pa = pa


PluginMap = {'uid': Uid,
             'task': Task,
             'folder': Folder,
             'todoist': Todoist,
             'cli': CLI,
             'base_plugin': Plugin}


class PersonalAssistant(object):
    def __init__(self, config_dir, app_data_dir):
        self._lock = threading.RLock()
        self._active = False

        # load config # todo: move to launch?
        self._config_dir = config_dir
        config_path = os.path.join(self.config_dir, 'core.config')
        self.config = load_config(config_path, TPersonalAssistantConfig)
        self._app_data_dir = app_data_dir

        # configurable # todo: move to launch?
        plugins = [p.Name.lower() for p in self.config.Plugins if p.IsActive]
        self._plugins = {p: PluginMap[p](self) for p in plugins}

        self.scheduler = Scheduler()

        self._callback_ringbell = threading.Condition()  # todo: consider moving ringbell into scheduler

    def notify_schedule_callback(self):
        self._callback_ringbell.notify()

    # ----------------------------------------------------
    # running machinery
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
        with self:  # this is actually incredible!
            while self.active:
                with self._callback_ringbell:
                    # determine next task timestamp
                    timeout = self.scheduler.get_time_to_next_event()
                    # wait for task or callback
                    self._callback_ringbell.wait(timeout=timeout)
                    # do what is needed (run target task)
                    task = self.scheduler.get_next_task()
                    result = task()
                    if task.is_recurring:
                        assert result is not None, "Recurring task should return timestamp of next occurence."  # todo: check that result is a valid timestamp
                        self.scheduler.add_task(callback=task.callback, )
                        # todo: add task_id to corresponding plugin?
                    self.scheduler.remove_task(task.id)
                    # todo: add recurrent flag for task. if task is recurrent

    def shutdown(self):
        self.active = False

    # ----------------------------------------------------
    # properties
    @property
    def plugins(self):
        # type: () -> Iterable[Plugin]
        """
        :return:
        :return type:
        """
        return self._plugins.values()

    def get_plugin(self, plugin_name):
        return self._plugins[plugin_name]

    @property
    def app_data_dir(self):
        return self._app_data_dir

    @property
    def config_dir(self):
        return self._config_dir

    @property
    def uid(self):
        # type: () -> Uid
        return self['uid']

    # ----------------------------------------------------
    # __getattr__, __getitem__ etc
    def __getitem__(self, item):
        return self.get_plugin(item)

    # launch machinery
    def __enter__(self):
        for plugin in self.plugins:  # todo: implement load order feature.
            plugin.launch()
        return self

    def __exit__(self):
        for plugin in self.plugins:
            plugin.shutdown()

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#
#     from secrets import lib_root
#
#     parser.add_argument("--config-dir", default=os.path.join(lib_root, "config"))
#     parser.add_argument("--app-data-dir", default=os.path.join(lib_root, "app_data"))
#     parser.add_argument("--debug", action="store_true")
#     args = parser.parse_args()
#
#     if args.debug:
#         logging.basicConfig(level=logging.DEBUG)
#
#     pa = PersonalAssistant(config_dir=args.config_dir, app_data_dir=args.app_data_dir)
#     pa.run()
