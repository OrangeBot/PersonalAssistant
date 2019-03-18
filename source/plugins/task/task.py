from proto.task_pb2 import TTask
from source.plugins.base import PluginItem, Plugin


class TaskItem(PluginItem, TTask):
    pass


class Task(Plugin, TaskItem):
    def setup_callbacks(self):
        # todo:
        pass

    def populate_schedule(self):
        # todo: add task reminders to schedule?
        pass

    # todo launch: create_task
    def create_task(self, uid=None):
        # if uid is None
        if uid is None:
            uid = self.pa.plugins['uid'].create_uid()
