#!/usr/bin/env python
import argparse
import os
import sys

import todoist

sys.path.append('/Users/plavrov/work/pyutils/')
# from secrets import lib_root
from pyutils import is_unix, is_python_3

if not is_python_3():
    import copy_reg
    import types


    def _pickle_method(m):
        if m.im_self is None:
            return getattr, (m.im_class, m.im_func.func_name)
        else:
            return getattr, (m.im_self, m.im_func.func_name)


    copy_reg.pickle(types.MethodType, _pickle_method)

if is_unix():
    lib_root = "/Users/plavrov/work/PersonalAssistant"
else:
    lib_root = "C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant"

sys.path.append(lib_root)


def main(api_token, output_path):
    from pyutils import connected_to_internet
    if not connected_to_internet():
        raise RuntimeError("Need connection to the internet to generate mock")
    if api_token is None:
        api_token = os.path.join(lib_root, 'config', 'todoist.token')
    if os.path.exists(api_token):
        from pyutils import get_password
        api_token = get_password(api_token)
    else:
        raise RuntimeError("Need api token to generate mock")

    prototype = todoist.TodoistAPI(api_token)
    engine = 'pkl'  # 'json' or 'pkl'
    mock_path = output_path or os.path.join(lib_root, 'app_data', 'mock_TodoistAPI_py{}.{}'.format('3' if is_python_3() else '2', engine))

    from pyutils import Mock
    mock_api = Mock(prototype, dump_path=mock_path, dump_engine=engine)

    # now do sample requests
    mock_api.sync()
    # _ = mock_api.updates # no such field, what was i thinking
    _ = mock_api.activity
    mock_api.commit()
    mock_api.items.all()
    mock_api.projects.all()

    # mock_api.


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-token", default=None)
    parser.add_argument("--output-path", default=None)
    args = parser.parse_args()
    main(api_token=args.api_token, output_path=args.output_path)
