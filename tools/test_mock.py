#!/usr/bin/env python
from __future__ import print_function

import os
import sys

import todoist

sys.path.append('/Users/plavrov/work/pyutils/')
from pyutils import is_unix, is_python_3

if is_unix():
    lib_root = "/Users/plavrov/work/PersonalAssistant"
else:
    lib_root = "C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant"

sys.path.append(lib_root)


def main():
    prototype = todoist.TodoistAPI()
    engine = 'pkl'  # 'json' or 'pkl'
    mock_path = os.path.join(lib_root, 'app_data', 'mock_TodoistAPI_py{}.{}'.format('3' if is_python_3() else '2', engine))
    from pyutils import Mock
    mock_api = Mock(prototype, dump_path=mock_path, dump_engine=engine)

    print("Following fields are mocked:")
    print(mock_api.mock.keys())

    # now do sample requests
    print("Sync:\n", mock_api.sync().__repr__()[:200])

    # _ = mock_api.updates # no such field, what was i thinking
    print("\n\tActivity:\n", mock_api.activity.__repr__()[:200])
    print("\n\tcommit:\n", mock_api.commit().__repr__()[:200])
    print("\n\titems:\n", mock_api.items.all().__repr__()[:200])
    print("\n\tprojects:\n", mock_api.projects.all().__repr__()[:200])
    print('It seems mock is doing alright')


if __name__ == "__main__":
    main()
