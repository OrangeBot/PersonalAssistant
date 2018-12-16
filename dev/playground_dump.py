# step 1, import todoist api
from todoist.api import TodoistAPI
import sys, os
# os.path.abspath(__file__)
# os.getcwd()
personal_assistant_path = 'C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant'
sys.path.append(personal_assistant_path)
# os.listdir(personal_assistant_path)
from pyutils import get_token
api = TodoistAPI(get_token())
api.sync()





api.state.keys()
# ['collaborators',
#  'day_orders_timestamp',
#  'live_notifications_last_read_id',
#  'items',
#  'collaborator_states',
#  'labels',
#  'reminders',
#  'locations',
#  'settings_notifications',
#  'project_notes',
#  'user',
#  'filters',
#  'day_orders',
#  'live_notifications',
#  'notes',
#  'projects']
projects = api.state['projects']

updates = api.activity

sample_item = api.items.all()[0]

from pyutils import dump_json, load_json

settings = {'permitted_paths':}

import threading
import time
import datetime

import defaults


class Folder(object):
    def __init__(self, project, assistant=None):
        self._todoist_project_id = project['id']
        if assistant is None:

        self._project = None
        self._parent = None
        self._children = set()

    # @classmethod
    # def from_project(cls, project):
    #     self.project_id = project['id']


# class FolderTree(object):
#     def __init__(self):
#         self._root = None
#         # self._projects = dict() # id ->
#         self._projects_by_id = dict()
#         self._projects_by_path = dict()
#         
#     
#     @property
#     def projects(self):
#         return self._projects_by_id.values()
#         
#     def load_projects(self, projects):
#         
#     def __getitem__(self, item):
#         # case 1: item == id
#         if item in self._projects_by_id

class Task(object):
    def __init__(self, item, personal_assistant=None):
        self._personal_assistant = personal_assistant or defaults.assistant

        # if item is not None:
        self._todoist_item_id = item['id']
        # else:
        #     self.create_todoist_task()

        self.processed = False

    @property
    def project(self):
        return

    @property
    def personal_assistant(self):
        return self._personal_assistant

    pa = personal_assistant

    @property
    def item(self):
        return self.pa.
        # def create_todoist_task(self):


class PersonalAssistant(object):
    def __init__(self, api_token=None):

        self._ASSISTANT_COOLDOWN = 1
        self._lock = threading.RLock()
        self._run_assistant = False
        self._assistant_status = False
        self._assistant_thread = None
        self.autosync_api = False
        self._AUTOSYNC_COOLDOWN = 1
        self._last_api_sync_timestamp = None
        self._REVISION_COOLDOWN = 60
        self._revision_countdown = 0

        self._api = None
        self.connect_to_todoist(api_token)

        self._included_paths = []
        self._excluded_paths = []
        self.configure_permitted_paths()

        self.PROJECTS_REPOSITORY = {project['id']: project for project in self.api.}

        self.launch_assistant()

        if defaults.assistant is None:
            defaults.assistant = self

    def get_state(self):
        state = self.__dict__
        # todo: remove api
        # todo: PROJECTS - only ids?
        return state

    def set_state(self, state):
        self.__dict__.update(state)
        # todo sync todoist api

    def configure_permitted_paths(self, permitted_paths=None):
        # 1) define what i can touch and what i can't
        # settings_path = os.path.join()
        permitted_paths = None
        if permitted_paths is None:
            try:
                permitted_paths = raw_input("""
        Default: "personal assistant". All missing paths will be created.
        Enter paths that personal assistant will be in control of
        Example: personal assistant, -personal assistant/private
        add '-' before the path to exclude it.
        If only excluded paths are mentioned - all paths are considered permitted except 
        If no paths are mentioned 
            """)
            except:
                permitted_paths = ''
            if permitted_paths == '':
                permitted_paths = "personal assistant"
            pp = [p.strip().strip('/') for p in permitted_paths.split(',')]
            self._included_paths = [p for p in pp if not p.startswith('-')]
            self._excluded_paths = [p[1:] for p in pp if p.startswith('-')]
            if len(self._included_paths) == 0:
                self._included_paths = [""]

    def path_is_permitted(self, path):
        return any([path.startswith(p) for p in self._included_paths]) and not any(
            [path.startswith(p) for p in self._excluded_paths])

    def connect_to_todoist(self, api_token):
        import todoist
        if api_token is None:
            from resources import default_token_path
            api_token = default_token_path
        if os.path.exists(api_token):
            from pyutils import get_token
            api_token = get_token(api_token)
        self._api = todoist.TodoistAPI(api_token)

    def sync_api(self):
        with self._lock:
            self._api.sync()
            self._last_api_sync_timestamp = datetime.datetime.now()

    @property
    def api(self):
        if self.autosync_api and (datetime.datetime.now() - self._last_api_sync_timestamp > datetime.timedelta(
                seconds=self._AUTOSYNC_COOLDOWN)):
            self.sync_api()
        return self._api

    def launch_assistant(self):
        if not self.check_assistant_status():
            self.run_assistant = True
            from pyutils import run_bg
            self._assistant_thread = run_bg(self._assistant())

    def check_assistant_status(self):
        with self._lock:
            self._assistant_status = False
        time.sleep(self._ASSISTANT_COOLDOWN + 0.5)  # if assistatn
        with self._lock:
            return self._assistant_status

    def _assistant(self):
        while self.run_assistant:
            if self._revision_countdown <= 0:
                tasks_to_process = self.get_unprocessed_tasks()
                self._revision_countdown = self._REVISION_COOLDOWN
            else:
                tasks_to_process = self.get_updated_tasks()

            for task in tasks_to_process:
                self.process_task(task)

            time.sleep(self._ASSISTANT_COOLDOWN)

    @property
    def run_assistant(self):
        with self._lock:
            return self._run_assistant

    @run_assistant.setter
    def run_assistant(self, value):
        with self._lock:
            self._run_assistant = value

    def get_updated_tasks(self):
        updates = self._api.activity
        return []

    def get_unprocessed_tasks(self):
        return [task for task in self.tasks if task.project.path_is_permitted and not task.processed]

    @property
    def tasks(self):
        return self._tasks

    def create_project(self, name, parent):


self = PersonalAssistant()  