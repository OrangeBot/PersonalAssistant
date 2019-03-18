import logging
import os

import socketserver
from pyutils import get_password, run_bg

from source.plugins.base import PluginItem, Plugin, PluginItemDescription
from source.plugins.todoist_plugin.todoist_api_wrapper import TodoistApiWrapper
from source.plugins.todoist_plugin.todoist_webhooks import get_todoist_webhook_handler
# import todoist
from .proto.config_pb2 import TTodoistConfig
from .proto.todoist_pb2 import TTodoistTask, TTodoistProject


class TodoistTaskItem(PluginItem, TTodoistTask):
    dependencies = {
        # PluginItemDescription(plugin='uid', name='uid'),
        PluginItemDescription(plugin='task', name='task'),
    }


class TodoistProjectItem(PluginItem, TTodoistProject):
    dependencies = {
        # PluginItemDescription(plugin='uid', name='uid'),
        PluginItemDescription(plugin='folder', name='folder'),
    }


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

        token_path = os.path.join(self.pa.config_dir, 'todoist.token')
        # self._api = todoist.TodoistAPI(get_password(token_path))
        self._api = TodoistApiWrapper(token=get_password(token_path))
        self.todoist_id_map = {}

        # todo: subscriptions
        # subscribe task to Task.text

    # @property
    # def default_project(self):
    #     return self.config.DefaultProject

    def launch(self):
        super(Todoist).launch()  # loads protobufs
        self.todoist_id_map = {}
        for task in self.items['todoist_task']:
            self.todoist_id_map[task.todoist_id] = task.uid
        for project in self.items['todoist_project']:
            self.todoist_id_map[project.todoist_id] = project.uid
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
        :param project_id: uid of the project
        :return:
        """
        # if todoist id is None - need to create at todoist. else already created
        # if uid is None need to create at base. Else already exists.
        if uid is None:
            uid = self.pa.plugins['task'].create_task(text=text)
        if todoist_id is None:  # todo: implement custom project
            todoist_id = self._api.items.add(content=text, project_id=None)
        self.items['task'][uid] = TodoistTaskItem(text=text, uid=uid, todoist_id=todoist_id, project_id=project_id)

    def create_project(self, name, uid=None, todoist_id=None):
        if uid is None:
            uid = self.pa.plugins['folder'].create(name=name)  # todo verify that there is uid here
            assert uid in self.pa.plugins['folder'].items['folder']
        if todoist_id is None:  # todo: implement custom project
            todoist_id = self._api.projects.add(name=name)
            # todo: verify that this is an id of
        project = TodoistProjectItem(uid=uid, todoist_id=todoist_id)

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
