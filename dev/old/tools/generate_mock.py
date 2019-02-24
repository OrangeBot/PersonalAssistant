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


def main(api_token):
    from pyutils import connected_to_internet
    if not connected_to_internet():
        raise RuntimeError("Need connection to the internet to generate mock")
    if api_token is None:
        from resources import default_token_path
        api_token = default_token_path
    if os.path.exists(api_token):
        from pyutils import get_token
        api_token = get_token(api_token)
    else:
        raise RuntimeError("Need api token to generate mock")

    prototype = todoist.TodoistAPI(api_token)
    from resources import lib_root
    engine = 'pkl'  # 'json' or 'pkl'
    mock_path = os.path.join(lib_root, 'resources', 'mock_TodoistAPI.{engine}'.format(engine=engine))
    from pyutils import Mock
    mock_api = Mock(prototype, dump_path=mock_path, dump_engine=engine)

    # now do sample requests
    mock_api.sync()
    # _ = mock_api.updates # no such field, what was i thinking
    _ = mock_api.activity
    mock_api.commit()
    mock_api.items.all()
    mock_api.projects.all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-token", default=None)
    args = parser.parse_args()
    main(api_token=args.api_token)
