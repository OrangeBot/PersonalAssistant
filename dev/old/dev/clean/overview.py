# 1) lib path
import sys, os

unix_lib_path = os.path.expanduser("~/work/pa/PersonalAssistant")
win_lib_path = 'C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant'


def is_unix():
    val = os.path.join('_','_')
    return val == "_/_"


if is_unix():
    if unix_lib_path not in sys.path:
        sys.path.append(unix_lib_path)
else:
    if win_lib_path not in sys.path:
        sys.path.append(win_lib_path)

import lib.stack as palib
import pyutils
import resources

# ----------------------------------------------------------------------------------------------------------------------
# 2) class TodoistAPI

from todoist.api import TodoistAPI
api = TodoistAPI(pyutils.get_token())

# ----------------------------------------------------------------------------------------------------------------------
# 3) class PersonalAssistant

pa = palib.PersonalAssistant()
