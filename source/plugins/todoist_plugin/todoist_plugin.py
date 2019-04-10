# -*- coding: utf-8 -*-
import logging
import os

from pyutils import get_password, run_bg, is_python_3

from source.plugins.base import PluginItem, Plugin, PluginItemDescription
from source.plugins.todoist_plugin.todoist_api_wrapper import TodoistApiWrapper
from source.plugins.todoist_plugin.todoist_webhooks import get_todoist_webhook_handler
# import todoist
from .proto.config_pb2 import TTodoistConfig
from .proto.todoist_pb2 import TTodoistTask, TTodoistProject

if is_python_3():
    # py3:
    import socketserver  # socketserver.TCPServer

else:
    # py2:
    import SocketServer as socketserver  # SocketServer.TCPServer


class TodoistTaskItem(PluginItem, TTodoistTask):
    dependencies = {
        # PluginItemDescription(plugin='uid', name='uid'),
        PluginItemDescription(plugin='task', name='task'),
    }

    def __init__(self, uid=None, todoist_id=None, text=None, schedule=None, due_date=None, parent=None):
        super(TodoistTaskItem, self).__init__(uid=uid, todoist_id=todoist_id, text=text, schedule=schedule, due_date=due_date, parent=parent)

    @property
    def text(self):
        return self._proto.Text

    @text.setter
    def text(self, text):
        self._proto.Text = text

    @property
    def parent(self):
        return self._proto.Parent

    @parent.setter
    def parent(self, parent):
        self._proto.Parent = parent

    @property
    def uid(self):
        return self._proto.Uid

    @uid.setter
    def uid(self, uid):
        self._proto.Uid = uid

    @property
    def todoist_id(self):
        return self._proto.TodoistId

    @todoist_id.setter
    def todoist_id(self, todoist_id):
        self._proto.TodoistId = todoist_id

    @property
    def schedule(self):
        return self._proto.Schedule

    @schedule.setter
    def schedule(self, schedule):
        self._proto.Schedule = schedule

    @property
    def due_date(self):
        return self._proto.DueDate

    @due_date.setter
    def due_date(self, due_date):
        self._proto.DueDate = due_date


class TodoistProjectItem(PluginItem, TTodoistProject):
    dependencies = {
        # PluginItemDescription(plugin='uid', name='uid'),
        PluginItemDescription(plugin='folder', name='folder'),
    }

    def __init__(self, uid=None, todoist_id=None, name=None, parent=None):
        super(TodoistProjectItem, self).__init__(uid=uid, todoist_id=todoist_id, name=name, parent=parent)

    @property
    def uid(self):
        return self._proto.Uid

    @uid.setter
    def uid(self, uid):
        self._proto.Uid = uid

    @property
    def todoist_id(self):
        return self._proto.TodoistId

    @todoist_id.setter
    def todoist_id(self, todoist_id):
        self._proto.TodoistId = todoist_id

    @property
    def name(self):
        return self._proto.Name

    @name.setter
    def name(self, name):
        self._proto.Name = name

    @property
    def parent(self):
        return self._proto.Parent

    @parent.setter
    def parent(self, parent):
        self._proto.Parent = parent


class Todoist(Plugin, TodoistTaskItem, TodoistProjectItem):
    # WARNING: don't need that, created in the MetaClass.
    # _items_types = { # item type name -> item type #
    #     'task': TodoistTaskItem,
    #     'project': TodoistProjectItem
    # }
    _config_type = TTodoistConfig

    def __init__(self, pa, config_path=None):
        """
        :param pa:
        :type pa: source.core.PersonalAssistant
        """
        super(Todoist, self).__init__(pa)

        self._config_path = config_path or os.path.join(self.pa.config_dir, 'todoist.config')

        # self._api = todoist.TodoistAPI(get_password(token_path))
        self.todoist_id_map = {}

        # todo: subscriptions
        # subscribe task to Task.text

    # @property
    # def default_project(self):
    #     return self.config.DefaultProject

    def launch(self):
        super(Todoist, self).launch()  # loads protobufs
        self.todoist_id_map = {}
        for task in self.items['todoist_task']:
            self.todoist_id_map[task.todoist_id] = task.uid
        for project in self.items['todoist_project']:
            self.todoist_id_map[project.todoist_id] = project.uid
        token_path = os.path.join(self.pa.config_dir, 'todoist.token')
        self._api = TodoistApiWrapper(token=get_password(token_path), allowed_paths=self.config.AllowedPaths)  # need to do after loading config or re-think.
        self.sync()  # synchronises

        # for name, item_type in self._items_types.items():
        #     protos_path = os.path.join(self.pa.config.AppData)
        #     self._items[name] = {p.Uid: item_type.from_proto(p) for p in load_protos(protos_path, item_type.proto_type)}

        # self.populate_schedule()

    def create_task(self, uid=None, todoist_id=None, text=None, project_id=None):
        """
        :param uid:
        :param todoist_id:
        :param text:
        :param project_id: uid of the project?
        :return:
        """
        # todo: need to distinguish parent project and parent task. Path concept also gets complicated
        # if todoist id is None - need to create at todoist. else already created
        # if uid is None need to create at base. Else already exists.
        if uid is None:
            uid = self.pa.get_plugin('task').create_task(text=text)
        if todoist_id is None:  # todo: implement custom project
            todoist_id = self._api.items.add(content=text, project_id=None)
        self.items['task'][uid] = TodoistTaskItem(text=text, uid=uid, todoist_id=todoist_id, project_id=project_id)

    def create_project(self, name, uid=None, todoist_id=None):
        logging.warn("Need to re-check 'create_project' method - it's not up to date.")
        if uid is None:
            uid = self.pa.plugins['folder'].create(name=name)  # todo verify that there is uid here
            assert uid in self.pa.plugins['folder'].items['folder']
        if todoist_id is None:  # todo: implement custom project
            todoist_id = self._api.projects.add(name=name)
            # todo: verify that this is an id of
        project = TodoistProjectItem(uid=uid, todoist_id=todoist_id)
        return project

    def create_todoist_task(self, uid=None, todoist_id=None, schedule=None, due_date=None):
        todoist_task = self.create_item('todoist_task', uid=uid, todoist_id=todoist_id, schedule=schedule, due_date=due_date)
        return todoist_task

    def create_todoist_project(self, uid=None, todoist_id=None, name=None, parent=None):
        todoist_project = self.create_item('todoist_project', uid=uid, todoist_id=todoist_id, name=name, parent=parent)
        return todoist_project
    # -----------------------------------------------------------------
    # scheduled events

    def sync(self):  # This should be called unfrequently, i think
        logging.info("Starting todoist sync")
        # todo: go over api items. Create missing
        # for task in self.api.tasks:
        #     if task.permitted
        for task in self.api.allowed_tasks:
            if task.id not in self.todoist_id_map:
                self.create_task(todoist_id=task.id, text=task.text)
        # todo: go over local items. Create missing?

    def populate_schedule(self):
        logging.warn("Method populate_schedule for plugin Todoist is not implemented yet!")

    def setup_callbacks(self):
        logging.warn("Method setup_callbacks for plugin Todoist is not implemented yet!")
    # ------------------------------------------------------------------
    # webhooks

    def process_webhook(self, data):
        logging.info("Received webhook event: ", data)
        # trigger pa callback

    def listen_webhooks(self):
        Handler = get_todoist_webhook_handler(self.process_webhook)
        with socketserver.TCPServer(("", self.config.WebhookServerPort), Handler) as httpd:
            sa = httpd.socket.getsockname()
            logging.info("Serving Todoist Webhook listener HTTP server on", sa[0], "port", sa[1])
            # httpd.serve_forever()
            while self.pa.active:
                httpd.handle_request()

    def launch_webhooks_listener(self):
        run_bg(self.listen_webhooks)

    # ------------------------------------------------------------------
    # properties

    @property
    def api(self):
        return self._api