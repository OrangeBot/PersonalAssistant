# 1) adding lib to project interpreter path works both for

# 2) absolute import works

# 3) relative import doesnt work
try:
    from ..test import *
except:
    print("Relative import doesnt work")

# 4) protobuf works fine, but autocompletion doesnt

# 5) cross-imports don't work

# 6) Small: pycharm detects error on self.active = False incorrectly - it works fine.

# 7) Logging basic config effects logging throughout the whole program
