import os

lib_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

default_token_path = os.path.join(lib_root, 'resources', 'todoist.token')
