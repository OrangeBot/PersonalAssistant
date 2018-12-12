def trim(l, s=None, e=None):
    if s is not None and l.startswith(s) and len(s) > 0:
        l = l[len(s):]
    if e is not None and l.endswith(e) and len(e) > 0:
        l = l[:-len(e)]
    return l


def read(path):
    with open(path, 'r') as f:
        return f.read()


def write(what, where, mode='w'):
    with open(where, mode=mode) as f:
        return f.write(what)


from resources import token_path


def get_token(path=token_path):
    return read(path)


def load_json(where_from):
    import os
    import json
    if os.path.exists(where_from):
        with open(where_from, 'r') as f:
            return json.load(f)
    else:
        return json.loads(where_from)


def dump_json(what, where, mode='w'):
    import json
    with open(where, mode=mode) as f:
        return json.dump(what, f)


def get_source_code(func):
    import inspect
    lines = inspect.getsourcelines(func)[0]

    # define tabulation:
    import re

    tabulation = re.findall(r'(\s*)', lines[0])[0]
    return ''.join([trim(l, s=tabulation) for l in lines])


def create_script_from_method(func, path, add_shortcuts=True):
    import os
    import inspect
    name = func.__name__
    if os.path.isdir(path):
        # get method name
        path = os.path.join(path, name)
    if not '.' in path:
        path = path + '.py'

    script_code = """#!python
from __future__ import print_function"""

    # arguments
    argspec = inspect.getargspec(func)
    # argparse
    if len(argspec.args) > 0:
        script_code += """
import argparse
parser = argparse.ArgumentParser()

"""

        k = len(argspec.args) - len(argspec.defaults)

        for i, arg in enumerate(argspec.args):
            arg_line = "parser.add_argument('--{arg}'".format(arg=arg)
            if add_shortcuts:
                comps = arg.split('_')
                if len(comps) > 1:
                    arg_line += ", '--{short_arg}'".format(short_arg=''.join([c[0] for c in comps]))
                elif len(arg) > 1:
                    arg_line += ", '-{short_arg}'".format(short_arg=comps[0][0])
            if i >= k:
                # default
                arg_line += ", default={default}".format(default=repr(argspec.defaults[i - k]))
            else:
                arg_line += ", required=True"
            arg_line += ')\n'
            script_code += arg_line
        script_code += """
args = parser.parse_args()
"""

    # source_code
    script_code += get_source_code(func)

    script_code += """
if __name__ == "__main__":
    result = {func_name}({args})
    if result is not None:
        print(result)
""".format(func_name=name, args=', '.join(['args.' + arg for arg in argspec.args]))

    write(script_code, path)
