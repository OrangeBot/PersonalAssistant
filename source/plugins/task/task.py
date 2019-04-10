from proto.task_pb2 import TTask
from source.plugins.base import PluginItem, Plugin


class TaskItem(PluginItem, TTask):
    def __init__(self, uid=None, text=None, name=None):
        super(TaskItem, self).__init__(uid=uid, text=text, name=name)

    @property
    def uid(self):
        return self._proto.Uid

    @uid.setter
    def uid(self, uid):
        self._proto.Uid = uid

    @property
    def text(self):
        return self._proto.Text

    @text.setter
    def text(self, text):
        self._proto.Text = text

    @property
    def name(self):
        return self._proto.Name

    @name.setter
    def name(self, name):
        self._proto.Name = name


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
