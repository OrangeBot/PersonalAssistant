# 1) adding lib to project interpreter path works both for
from pyutils import trim

# 2) absolute import works
from source.core import *

# 3) relative import doesnt work
try:
    from ..test import *
except:
    print("Relative import doesnt work")