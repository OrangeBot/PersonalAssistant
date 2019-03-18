from source.plugins.base import PluginItem, Plugin
from proto.{name}_pb2 import T{Name}


class {Name}Item(PluginItem, T{Name}):


class {Name}(Plugin, {Name}Item):
    pass

