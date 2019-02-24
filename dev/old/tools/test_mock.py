#!/usr/bin/env python
import argparse
import todoist
import os

import sys

unix_lib_path = os.path.expanduser("~/work/pa/PersonalAssistant")
win_lib_path = 'C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant'


def is_unix():
    val = os.path.join('_', '_')
    return val == "_/_"


if is_unix():
    if unix_lib_path not in sys.path:
        sys.path.append(unix_lib_path)
else:
    if win_lib_path not in sys.path:
        sys.path.append(win_lib_path)


def main():
    prototype = todoist.TodoistAPI()
    from resources import lib_root
    engine = 'pkl'  # 'json' or 'pkl'
    mock_path = os.path.join(lib_root, 'resources', 'mock_TodoistAPI.{engine}'.format(engine=engine))
    from pyutils import Mock
    mock_api = Mock(prototype, dump_path=mock_path, dump_engine=engine)

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
