# # step 1, import todoist api
import sys, os
try:
    lib_path = os.path.abspath(__file__)
    while os.path.basename(lib_path) != "PersonalAssistant":
        lib_path = os.path.dirname(lib_path)
    sys.path.append(lib_path)
except:
    mac_lib_path = os.path.expanduser("~/work/pa/PersonalAssistant")
    win_lib_path = 'C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant'

    def is_mac():
        val = os.path.join('_', '_')
        return val == "_/_"
    if is_mac():
        if mac_lib_path not in sys.path:
            sys.path.append(mac_lib_path)
    else:
        if win_lib_path not in sys.path:
            sys.path.append(win_lib_path)


# api = TodoistAPI(get_token())
# api.sync()

# # import pyutils
# # pyutils.default_token_path
# from pyutils import get_token

import threading
import time
import datetime

import defaults


class Folder(object):
    """sample project.data:
    {'is_favorite': 0,
     'color': 21,
     'collapsed': 0,
     'id': 2201412629,
     'indent': 1,
     'name': 'personal assistant',
     'has_more_notes': False,
     'is_deleted': 0,
     'parent_id': 2183890184,
     'item_order': 52,
     'shared': False,
     'is_archived': 0}
    """

    def __init__(self, project, assistant=None):
        self._todoist_id = project.data['id']

        self._assistant = assistant
        self._children = set()
        self._tasks = set()

    @property
    def personal_assistant(self):
        if self._assistant is None:
            return defaults.assistant
        else:
            return self._assistant

    pa = personal_assistant

    def update_parent_id(self, new_id, commit=True):
        # todo:
        print("WARNING: This modifies actual value on server, need to emphasise that in the name of the method!!!")
        self.project.update(parent_id=new_id)
        if commit:
            self.api.commit()

    @property
    def id(self):
        return self._todoist_id

    @property
    def project(self):
        return self.pa.get_project(self.id)

    @property
    def path(self):
        if self.parent_id is None:
            return self.name
        else:
            return "{}/{}".format(self.parent.path, self.name)

    @property
    def name(self):
        return self.project.data['name']

    @property
    def api(self):
        return self.pa.api

    @property
    def parent_id(self):
        return self.project.data['parent_id']

    @property
    def parent(self):
        if self.parent_id is None:
            return None
        return self.pa.get_folder(self.parent_id)

    def register_task(self, task):
        self._tasks.add(task.id)

    def unregister_task(self, task):
        self._tasks.remove(task.id)

    def register_child(self, folder):
        self._children.add(folder.id)

    def unregister_child(self, folder):
        self._children.remove(folder.id)

    @property
    def children(self):
        return [self.pa.get_folder(p) for p in self._children]

    @property
    def tasks(self):
        return [self.pa.get_task(t) for t in self._tasks]


import dateutil


class Task(object):
    """sample item.data
    {'day_order': -1,
     'assigned_by_uid': 4405058,
     'is_archived': 0,
     'labels': [2149331073],
     'sync_id': None,
     'all_day': False,
     'in_history': 0,
     'date_added': 'Fri 12 Jun 2015 17:21:12 +0000',
     'indent': 1,
     'date_lang': None,
     'id': 7104735,
     'priority': 2,
     'checked': 0,
     'user_id': 4405058,
     'has_more_notes': False,
     'due_date_utc': 'Thu 30 Aug 2018 20:59:59 +0000'
     'content': 'ирригатор',
     'parent_id': None,
     'item_order': 1,
     'is_deleted': 0,
     'responsible_uid': None,
     'project_id': 143126188,
     'date_completed': None,
     'collapsed': 0,
     'date_string': "every 2 weeks"}
    """

    def __init__(self, item, personal_assistant=None):
        self._assistant = personal_assistant

        # if item is not None:
        self._todoist_id = item.data['id']
        # else:
        #     self.create_todoist_task()

        self._children = set()

        self.processed = False

        self._pa_repeat_rule = None

    @property
    def parent_id(self):
        return self.item.data['parent_id']

    @property
    def project_id(self):
        return self.item.data['project_id']

    @property
    def id(self):
        return self._todoist_id

    # @property #probably better off going directly folder->project
    # def project(self):
    #     return self.folder.project

    @property
    def folder(self):
        return self.pa.get_folder(self.project_id)

    @property
    def parent(self):
        if self.parent_id is None:
            return None
        return self.pa.get_task(self.parent_id)

    @property
    def personal_assistant(self):
        if self._assistant is None:
            return defaults.assistant
        return self._assistant

    pa = personal_assistant

    @property
    def item(self):
        return self.pa.get_item(self.id)

    # def create_todoist_task(self):

    @property
    def folder_path(self):
        return self.folder.path

    # ---------------------------------------------
    # ok, here fancy stuff begins
    def get_next_due_time(self):
        """
        :return: python datetime
        """
        # todo: output
        if self._pa_repeat_rule is not None:
            print("At some point PA should take control over scheduling, providing more flexible rules")
            raise NotImplementedError
        else:
            if not self.is_repeated():
                raise RuntimeError("Requesting next due time from non-repeated task")
            print("Need to understand how to get next due date from todoist...")

    def get_due_time(self, todoist_format=False):
        if todoist_format:
            return self.due_date_utc
        else:
            return dateutil.parser.parse(self.due_date_utc)

    @property
    def due_date_utc(self):
        # 'due_date_utc': 'Thu 30 Aug 2018 20:59:59 +0000'
        return self.item.data['due_date_utc']

    @property
    def date_string(self):
        return self.item.data['date_string']

    def is_repeated(self):
        if self._pa_repeat_rule is not None:
            return True
        return self.date_string is not None and self.date_string.lower().startswith('every')

        # next_time = task.get_next_due_time()

    # due_time = task.get_due_time()
    # current_time = datetime.datetime.now()
    # return (
    #     task.is_repeated()
    def reschedule(self, due_time=None):
        print("Need to transform due time into todoist format")
        print("Need to learn how to schedule task to next time in todoist")
        raise NotImplementedError


class PersonalAssistant(object):
    def __init__(self, api_token=None, permitted_paths=None, only_permitted=False):

        self._ASSISTANT_COOLDOWN = 1  # how often assistant performs status review
        self._COMMIT_COOLDOWN = 1  # time to wait to accumulate changes for commit

        self._lock = threading.RLock()
        self._run_assistant = False
        self._assistant_status = False
        self._assistant_thread = None
        self.autosync_api = False
        self._AUTOSYNC_COOLDOWN = 1  # how often sync happens during api usage
        self._last_api_sync_timestamp = None
        self._REVISION_COOLDOWN = 60
        self._revision_countdown = 0
        self.run_assistant = False

        self._api = None
        self.connect_to_todoist(api_token)

        self._included_paths = []
        self._excluded_paths = []
        self.configure_permitted_paths(permitted_paths=permitted_paths)

        # initialize todoist mappings
        self._items = {p.data['id']: p for p in self.api.items.all()}
        self._projects = {p.data['id']: p for p in self.api.projects.all()}

        self._folders = {project.data['id']: Folder(project) for project in self.projects}
        self._tasks = {item.data['id']: Task(item) for item in self.items}
        self._initialize_folders()
        self._initialize_tasks()

        if defaults.assistant is None:
            defaults.assistant = self

        if only_permitted:
            # todo:
            print("To reduce resource consumption theres an option to "
                  "process only tasks that are permitted, leaving everything else out of scope")
            raise NotImplementedError

        self.launch_assistant()

    def _initialize_folders(self):
        # todo: set up parents and children
        for folder in self.folders:
            if folder.parent is not None:
                folder.parent.register_child(folder)

    def _initialize_tasks(self):
        # todo: don't need anything now, actually
        # oh, apparently, tasks too have parents and childrenv
        # self._items = set()
        # self._children = set()
        for task in self.tasks:
            task.folder.register_task(task)
            if task.parent is not None:
                task.parent.register_child(task)

    @property
    def projects(self):
        return self._projects.values()

    def get_project(self, id):
        return self._projects[id]

    @property
    def items(self):
        return self._items.values()

    def get_item(self, id):
        return self._items[id]

    @property
    def folders(self):
        return self._folders.values()

    def get_folder(self, id):
        return self._folders[id]

    @property
    def tasks(self):
        return self._tasks.values()

    def get_task(self, id):
        return self._tasks[id]

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
            from dev.old.resources import default_token_path
            api_token = default_token_path
        if os.path.exists(api_token):
            from pyutils import get_token
            api_token = get_token(api_token)
        self._api = todoist.TodoistAPI(api_token)

    def sync_api(self):
        with self._lock:
            self._api.sync()
            self._process_items_updates()
            self._last_api_sync_timestamp = datetime.datetime.now()

    def _process_items_updates(self):
        # [
        # {
        #   'id': 955344370,
        #   'object_type': 'item',
        #   'object_id': 101157918,
        #   'event_type': 'updated',
        #   'event_date': 'Fri 01 Jul 2016 14:28:37 +0000',
        #   'parent_project_id': 174361513,
        #   'parent_item_id': None,
        #   'initiator_id': None,
        #   'extra_data': {
        #     'content': 'Task1',
        #     'due_date': 'Sat 02 Jul 2016 20:59:59 +0000',
        #     'last_due_date': None,
        #     'client' : 'Mozilla/5.0; Todoist/830'
        #   }
        # },
        # {
        #   'id': 955333751,
        #   'object_type': 'note',
        #   'object_id': 23685068,
        #   'event_type': 'added',
        #   'event_date': 'Fri 01 Jul 2016 14:25:04 +0000',
        #   'parent_project_id': 174361513,
        #   'parent_item_id': 101157918,
        #   'initiator_id': None,
        #   'extra_data': {
        #     'content': 'Note1',
        #     'client': 'Todoist/11.2.1'
        #   }
        # },
        #
        # "last_due_date" : null,
        # "due_date" : "Sat 02 Jul 2016 20:59:59 +0000",
        #
        # api.activity.get()
        print("Warning: items updates are not being processed")
        if self._last_api_sync_timestamp is not None:
            self.api.updates

    @property
    def api(self):
        if self.autosync_api and (datetime.datetime.now() - self._last_api_sync_timestamp > datetime.timedelta(
                seconds=self._AUTOSYNC_COOLDOWN)):
            self.sync_api()
        return self._api

    def launch_assistant(self, bg=False):
        if not self.check_assistant_status():
            self.run_assistant = True
            if bg:
                from pyutils import run_bg
                self._assistant_thread = run_bg(self._assistant)
            else:
                self._assistant()

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
        return updates

    def get_unprocessed_tasks(self):
        return [task for task in self.tasks if task.project.path_is_permitted and not task.processed]

    @property
    def tasks(self):
        return self._tasks

    # def create_project(self, name, parent):
    #
    # def _delayed_commit_bg(self):
    #     with self._lock:
    #         self._commit_request_timestamp = datetime.datetime.now()
    #         if not self.commit_scheduled:
    #             run_bg()
    #
    # def _delayed_commit(self, delay=None):
    #     try:
    #
    #         time.sleep(delay or self._COMMIT_COOLDOWN)
    #         self.api.commit()
    #
    #         with self._lock:

    def reschedule_too_overdue_tasks(self):
        # go over all permitted tasks
        for task in self.permitted_tasks:
            if PersonalAssistant.default_overdue_reschedule_condition(task):
                task.reschedule()

    @property
    def permitted_tasks(self):
        import itertools
        return itertools.chain(*[folder.tasks for folder in self.permitted_folders])
        # return [task for task in self.tasks if self.task_is_permitted(task)]

    @property
    def permitted_folders(self):
        return [folder for folder in self.folders if self.path_is_permitted(folder.path)]

    def task_is_permitted(self, task):
        return self.path_is_permitted(task.folder_path)

    @staticmethod
    def default_overdue_reschedule_condition(task):
        next_time = task.get_next_due_time()
        due_time = task.get_due_time()
        current_time = datetime.datetime.now()
        return (
                task.is_repeated()
                and (next_time - current_time) < datetime.timedelta(hours=36)  # less than 1.5 days remaining
                and (next_time - current_time) < 0.5 * (next_time - due_time)  # less than 0.5 of repeat interval.
            # There may be problems with 'every!' rule, need to consider.
        )


# def reschedule_if_too_overdue_regular_task(
#         task,
#         condition=default_overdue_reschedule_condition
# ):
#     if condition(task)

self = PersonalAssistant()


