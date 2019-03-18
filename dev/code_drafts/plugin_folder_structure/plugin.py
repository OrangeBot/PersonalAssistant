from pyutils import to_snake_case, WARN

from source.plugins.base.base import PluginItem
from .proto.item_pb2 import TPlugin


class TestPluginItem(PluginItem, TPlugin):
    # single plugin item
    pass


def get_generator_name(f):
    return "create_{}".format(f)


class PluginMeta(type):
    def __new__(meta, name, bases, dct):
        res_bases = tuple(base for base in bases if not issubclass(base, PluginItem))
        return super(PluginMeta, meta).__new__(meta, name, res_bases, dct)

    def __init__(cls, name, bases, dct):
        item_bases = []
        res_bases = []
        for base in bases:
            if issubclass(base, PluginItem):
                item_bases.append(base)
            else:
                res_bases.append(base)
        cls.GEN_ITEM_PROPERTIES = True
        super(PluginMeta, cls).__init__(name, tuple(res_bases), dct)
        if cls.GEN_ITEM_PROPERTIES:
            message = ""
            for item_base in item_bases:
                name = get_generator_name(to_snake_case(item_base.__name__.rstrip("Item")))

                proto_fields = [f.name for f in cls.proto_type.DESCRIPTOR.fields]
                missing_fields = [f for f in proto_fields if not hasattr(cls, "create_{}")]
                if missing_fields:
                    message = "Some protobuf fields are missing\n"
                    message += "Add following lines to the {0} class declaration or set {0}.GEN_PROTOBUF_PROPERTIES = False\n".format(
                        cls.__name__)
                    message += "def __init__(self, {}):\n".format(', '.join(to_snake_case(f) for f in proto_fields))
                    message += "    self._proto = self.proto_type({})".format(
                        ', '.join(to_snake_case(f) for f in proto_fields))
                    for f in missing_fields:
                        message += """
def {}(         
""".format(to_snake_case(f), f)
                    WARN(message)


class Plugin(object):
    ITEM_TYPES = [TestPluginItem, ]

    def __init__(self):
        # read items from protobuf
        for item_type in self.ITEM_TYPES:
            pass

    def save_items(self):
        pass
