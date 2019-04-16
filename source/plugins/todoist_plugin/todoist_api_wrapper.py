# -*- coding: utf-8 -*-
# encoding: utf-8
import itertools
import os
import threading

import dateutil
import six
from pyutils import connected_to_internet, format_to_string, is_python_3, soft_encode
from todoist import TodoistAPI
from typing import Iterable


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
    _api_wrapper = None

    def __init__(self, project):
        self._todoist_id = project.data['id']
        self._children = set()
        self._tasks = set()

    def register_task(self, task):
        self._tasks.add(task.id)

    def unregister_task(self, task):
        self._tasks.remove(task.id)

    def register_child(self, folder):
        self._children.add(folder.id)

    def unregister_child(self, folder):
        self._children.remove(folder.id)

    # ----------------------------------------------------------------------
    # properties

    @property
    def children(self):
        return [self.pa.get_folder(p) for p in self._children]

    @property
    def tasks(self):
        return [self.pa.get_task(t) for t in self._tasks]

    @property
    def api_wrapper(self):
        return self._api_wrapper

    pa = api_wrapper

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
            return "{}/{}".format(self.parent.path, format_to_string(self.name))

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

    # ----------------------------------------------------------------------
    # modifying items

    def update_parent_id(self, new_id, commit=True):
        # todo:
        print("WARNING: This modifies actual value on server, need to emphasise that in the name of the method!!!")
        self.project.update(parent_id=new_id)
        if commit:
            self.api.commit()

    move = update_parent_id


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
     'content': 'non-ascii-task',
     'parent_id': None,
     'item_order': 1,
     'is_deleted': 0,
     'responsible_uid': None,
     'project_id': 143126188,
     'date_completed': None,
     'collapsed': 0,
     'date_string': "every 2 weeks"}
    """
    _api_wrapper = None

    def __init__(self, item):

        # if item is not None:
        self._todoist_id = item.data['id']
        # else:
        #     self.create_todoist_task()

        self._children = set()

        self.processed = False

        self._pa_repeat_rule = None

    # def path_is_allowed(self):
    #     return self.pa.

    def register_child(self, folder):
        self._children.add(folder.id)

    def unregister_child(self, folder):
        self._children.remove(folder.id)

    # ----------------------------------------------------------------
    # properties

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
    def api_wrapper(self):
        return self._api_wrapper

    pa = api_wrapper

    @property
    def item(self):
        return self.pa.get_item(self.id)

    @property
    def folder_path(self):
        return self.folder.path

    @property
    def text(self):
        return self.item['content']

    # ----------------------------------------------------------------
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
        #  todo: Need to transform due time into todoist format
        print("Need to learn how to schedule task to next time in todoist")
        # todo: Need to learn how to schedule task to next time in todoist
        raise NotImplementedError


class TodoistApiWrapper(object):
    def __init__(self, token=None, allowed_paths=None):
        # self._api = TodoistAPI(token=token)
        assert Task._api_wrapper is None, "More than one instance of TodoistApiWrapper is created, crash."
        Task._api_wrapper = self
        assert Folder._api_wrapper is None, "More than one instance of TodoistApiWrapper is created, crash."
        Folder._api_wrapper = self

        # self._ASSISTANT_COOLDOWN = 1  # how often assistant performs status review
        # self._COMMIT_COOLDOWN = 1  # time to wait to accumulate changes for commit

        self._lock = threading.RLock()
        # self._run_assistant = False
        # self._assistant_status = False
        # self._assistant_thread = None
        # self.autosync_api = False
        # self._AUTOSYNC_COOLDOWN = 1  # how often sync happens during api usage
        # self._last_api_sync_timestamp = None
        # self._REVISION_COOLDOWN = 60
        # self._revision_countdown = 0
        # self.run_assistant = False

        # ----------------------------------------------------------
        self._api = None
        self.connect_to_todoist(token)

        self._items = {}
        self._projects = {}
        self._folders = {}
        self._tasks = {}

        self.configure_allowed_paths(allowed_paths=allowed_paths)

        self.sync_api()
        # ----------------------------------------------------------

    def _initialize_folders(self):
        # todo: set up parents and children
        for folder in self.folders:
            if folder.parent is not None:
                folder.parent.register_child(folder)

    def _initialize_tasks(self):
        # todo: don't need anything now, actually
        # oh, apparently, tasks too have parents and children
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
        # type: () -> Iterable[Task]
        return self._tasks.values()

    def get_task(self, id):
        return self._tasks[id]

    def configure_allowed_paths(self, allowed_paths=None):
        # 1) define what i can touch and what i can't
        # settings_path = os.path.join()
        if allowed_paths is None:
            try:
                allowed_paths = input("""
        Default: "personal assistant". All missing paths will be created.
        Enter paths that personal assistant will be in control of
        Example: personal assistant, -personal assistant/private
        add '-' before the path to exclude it.
        If only excluded paths are mentioned - all paths are considered allowed except 
        If no paths are mentioned 
            """)
            except:
                allowed_paths = ''
        if allowed_paths == '':
            allowed_paths = "personal assistant"
        if isinstance(allowed_paths, six.string_types):
            allowed_paths = allowed_paths.split(',')
        pp = [soft_encode(p.strip().strip('/')) for p in allowed_paths]
        self._included_paths = [p for p in pp if not p.startswith('-')]
        self._excluded_paths = [p[1:] for p in pp if p.startswith('-')]
        if len(self._included_paths) == 0:
            self._included_paths = ["", ]

    def path_is_allowed(self, path):
        try:
            return any([path.startswith(p) for p in self._included_paths]) and not any(
                [path.startswith(p) for p in self._excluded_paths])
        except:
            print(path)
            print(p)
            print(self._included_paths)
            print(self._excluded_paths)

    @property
    def allowed_tasks(self):
        # type: () -> Iterable[Task]
        return itertools.chain(*[folder.tasks for folder in self.allowed_folders])
        # return [task for task in self.tasks if self.task_is_allowed(task)]

    @property
    def allowed_folders(self):
        return [folder for folder in self.folders if self.path_is_allowed(folder.path)]

    def task_is_allowed(self, task):
        return self.path_is_allowed(task.folder_path)

    def connect_to_todoist(self, api_token=None):
        if connected_to_internet():
            if api_token is None:
                from dev.old.resources import default_token_path
                api_token = default_token_path
            if os.path.exists(api_token):
                from pyutils import get_token
                api_token = get_token(api_token)
            if True:
                print("WARNING - using mock to generate mock.")
                prototype = TodoistAPI(api_token)
                engine = 'pkl'  # 'json' or 'pkl'
                from secrets import lib_root
                mock_path = os.path.join(lib_root, 'app_data', 'mock_TodoistAPI_py{}.{}'.format('3' if is_python_3() else '2', engine))
                from pyutils import Mock
                self._api = Mock(prototype, dump_path=mock_path, dump_engine=engine)
            else:
                self._api = TodoistAPI(api_token)
        else:
            prototype = TodoistAPI()
            engine = 'pkl'  # 'json' or 'pkl'
            from secrets import lib_root
            mock_path = os.path.join(lib_root, 'app_data', 'mock_TodoistAPI_py{}.{}'.format('3' if is_python_3() else '2', engine))
            from pyutils import Mock
            self._api = Mock(prototype, dump_path=mock_path, dump_engine=engine)

    def sync_api(self):
        with self._lock:
            self._api.sync()

            self._items = {p.data['id']: p for p in self.api.items.all()}
            self._projects = {p.data['id']: p for p in self.api.projects.all()}

            self._folders = {project.data['id']: Folder(project) for project in self.projects}
            self._tasks = {item.data['id']: Task(item) for item in self.items}
            self._initialize_folders()
            self._initialize_tasks()

            # todo: implement iterative updates
            # self._process_items_updates()
            # self._last_api_sync_timestamp = datetime.datetime.now()

    def _process_items_updates(self):
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
        # raise NotImplementedError()
        # if self._last_api_sync_timestamp is not None:
        #     self.api.updates

    @property
    def api(self):
        # if self.autosync_api and (datetime.datetime.now() - self._last_api_sync_timestamp > datetime.timedelta(
        #         seconds=self._AUTOSYNC_COOLDOWN)):
        #     self.sync_api()
        return self._api

    def get_updated_tasks(self):
        updates = self._api.activity
        return updates

    # def get_unprocessed_tasks(self):
    #     return [task for task in self.tasks if task.project.path_is_allowed and not task.processed]
