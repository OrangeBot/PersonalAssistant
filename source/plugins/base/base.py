import logging
import os
from collections import defaultdict

import google
import six
from pyutils import to_snake_case, WARN, trim, to_camel_case

from source.lib.common import load_protos, dump_protos, load_config
from source.plugins.base.proto.plugin_item_desctription_pb2 import TPluginItemDesctription


# from typing import Set


class ProtobufInheritanceMeta(type):
    def __new__(mcs, name, bases, dct):
        res_bases = tuple(base for base in bases if not issubclass(base, google.protobuf.message.Message))
        return super(ProtobufInheritanceMeta, mcs).__new__(mcs, name, res_bases, dct)

    def __init__(cls, name, bases, dct):
        proto_bases = []
        res_bases = []
        for base in bases:
            if issubclass(base, google.protobuf.message.Message):
                proto_bases.append(base)
            else:
                res_bases.append(base)
        cls.GEN_PROTOBUF_PROPERTIES = True
        super(ProtobufInheritanceMeta, cls).__init__(name, tuple(res_bases), dct)
        assert len(proto_bases) <= 1, "Can't subclass more than one proto type"
        if proto_bases:
            cls.proto_type = proto_bases[0]
            if cls.GEN_PROTOBUF_PROPERTIES:
                cls.proto_fields = [f.name for f in cls.proto_type.DESCRIPTOR.fields]
                missing_fields = [f for f in cls.proto_fields if not hasattr(cls, to_snake_case(f))]
                if missing_fields:
                    message = "Some protobuf fields are missing\n"
                    message += "Add following lines to the {0} class declaration or set {0}.GEN_PROTOBUF_PROPERTIES = False\n".format(
                        cls.__name__)
                    message += "def __init__(self, {}):\n".format(
                        ', '.join("{}=None".format(to_snake_case(f)) for f in cls.proto_fields))
                    message += "    super({}, self).__init__({})".format(cls.__name__,
                                                                         ', '.join("{}={}".format(to_snake_case(f), to_snake_case(f)) for f in cls.proto_fields))
                    for f in missing_fields:
                        message += """
@property
def {0}(self):
    return self._proto.{1}

@{0}.setter
def {0}(self, {0}):
    self._proto.{1} = {0}            
""".format(to_snake_case(f), f)
                    if message:
                        WARN(message)
        cls.class_name = to_snake_case(trim(name, e='Item'))


class PluginItem(object):
    """
    :type _plugin: Plugin
    """
    __metaclass__ = ProtobufInheritanceMeta
    proto_type = None
    subscriptions = defaultdict(set)
    dependencies = set()  # type: Set[PluginItemDescription]
    # init if missing
    # _pa = None  # :type _pa: source.core.PersonalAssistant
    _plugin = None

    def __init__(self, uid=None, **kwargs):
        """
        Does NOT register PluginItem into Plugin.
        """
        # if uid is missing - create uid.
        if uid is None:
            uid_item = self.pa.uid.create_uid()
            uid = uid_item.uid
        else:
            uid_item = self.pa.uid[uid]
        # 1. Fill protobuf
        proto_args = {to_camel_case(k): v for k, v in kwargs.items() if to_camel_case(k) in self.proto_type}
        self._proto = self.proto_type(Uid=uid, **proto_args)
        # register in base
        uid_item.associated_items.append(self.class_name)
        # create dependant if missing
        from source.core.personal_assistant import PluginMap
        for dependency in self.dependencies:
            if dependency not in uid_item.associated_items:
                getattr(PluginMap[dependency.plgugin], get_generator_name(dependency.name))(uid=uid, **kwargs)
        # done launch (need to do this to be able to launch)

    @classmethod
    def from_proto(cls, proto):
        # type: (object) -> PluginItem
        """
        Does NOT register PluginItem into Plugin
        """
        new = PluginItem.__new__(cls)  # todo: figure out what to call - cls or PluginItem.
        # I think pluginItem to avoid recursion? Can there be recursion?
        assert cls.proto_type == proto.__class__  # todo: check this works fine
        new._proto = proto
        return new

    # ----------------------------------------------------
    # properties
    @property
    def plugin(self):
        # type: () -> Plugin
        if self._plugin is None:
            raise RuntimeError("_plugin attribute for class {} not initialized".format(self.__class__.__name__))
        return self._plugin

    @property
    def pa(self):
        return self.plugin.pa

    # ----------------------------------------------------
    # __getattr__, __getitem__ etc
    def __setattr__(self, key, value):
        super(PluginItem).__setattr__(key, value)
        if key in self.subscriptions:  # avoid excessive defautdict garbage
            for callback in self.subscriptions[key]:
                callback(self)
        # todo: think through and implement update_time concept. Only in base? or in each item?


def get_generator_name(f):
    return "create_{}".format(f)


def schedule_method(repeated=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logging.debug("Decorating method for schedule")
            return func(*args, **kwargs)

        wrapper.for_schedule = True
        wrapper.repeated = repeated
        return wrapper

    return decorator


class PluginMeta(type):
    def __new__(mcs, name, bases, dct):
        res_bases = tuple(base for base in bases if not issubclass(base, PluginItem))
        return super(PluginMeta, mcs).__new__(mcs, name, res_bases, dct)

    def __init__(cls, name, bases, dct):
        item_bases = []
        proto_bases = []
        res_bases = []
        for base in bases:
            if issubclass(base, PluginItem):
                item_bases.append(base)
            elif issubclass(base, google.protobuf.message.Message):
                proto_bases.append(base)
                raise TypeError("Protobuf bases are not expected for Plugin class - use PluginItem instead.")
            else:
                res_bases.append(base)
        cls.GEN_ITEM_GENERATORS = True
        super(PluginMeta, cls).__init__(name, tuple(res_bases), dct)
        cls._items_types = {item_type.class_name: item_type for item_type in item_bases}

        # done: create_item methods codegen.
        if cls.GEN_ITEM_GENERATORS:
            message = ""
            for item_base in item_bases:
                generator_name = get_generator_name(item_base.class_name)
                if not hasattr(cls, generator_name):
                    attributes = ", ".join("{}=None".format(to_snake_case(f)) for f in item_base.proto_fields)
                    substituted_attributes = ", ".join(
                        "{0}={0}".format(to_snake_case(f)) for f in item_base.proto_fields)
                    message += """
def {generator_name}(self, {attributes}):
    {class_name} = self.create_item('{class_name}', {substituted_attributes})
    return {class_name}
""".format(
                        generator_name=generator_name,
                        class_name=item_base.class_name,
                        attributes=attributes,
                        substituted_attributes=substituted_attributes
                    )
            if message:
                WARN(message)
        cls.class_name = to_snake_case(name)

        cls._tasks_to_schedule = {}
        for k, v in six.iteritems(dct):
            if hasattr(v, 'for_schedule'):  # decorated methods
                logging.debug("Adding method '{}' to the schedule set of plugin '{}'".format(k, name))
                cls._tasks_to_schedule[k] = v


class Plugin(object):
    __metaclass__ = PluginMeta
    _items_types = {}
    _config_type = None

    #     ITEM_TYPES = [TestPluginItem, ]

    def __init__(self, pa):
        """ :type pa: source.core.PersonalAssistant """
        self.pa = pa
        self._items = dict()
        self._subscriptions = defaultdict(set)
        self._config_path = None
        self.config = None

    def load_config(self):  # todo: move config loading to metaclass?
        # But i want to do it on launch so that i could re-launch plugin...
        if self._config_path and os.path.exists(self._config_path):
            self.config = load_config(self._config_path, self._config_type)

    # ----------------------------------------------------
    # items
    def dump_items(self):
        for item_type in self.items_types:
            # "AppData/Items/Plugin_name/item_type_name"
            name = item_type.class_name
            dump_path = self.get_dump_path(name)
            dump_protos([i._proto for i in self._items[name]], dump_path)

    def load_items(self):
        for item_type in self.items_types:
            # "AppData/Items/Plugin_name/item_type_name"
            name = item_type.class_name
            dump_path = self.get_dump_path(name)
            protos = load_protos(dump_path, item_type.proto_type)
            self._items[name] = {p.Uid: item_type.from_proto(p) for p in protos}

    def get_dump_path(self, name):
        return os.path.join(self.items_dump_dir, "{}.pkl".format(name))

    def get_items_type(self, key):
        return self._items_types[key]

    # ----------------------------------------------------
    # launch machinery

    def populate_schedule(self):
        # todo: for task in self._tasks_to_schedule
        # todo: what is the method to add task to schedule?
        # todo: what is the time to add task at? Current?
        raise NotImplementedError

    def setup_callbacks(self):
        raise NotImplementedError

    def subscribe(self, field, callback, items_type=None):  # todo: so when do i subscribe? init vs launch.
        if items_type is None:
            assert len(self.items_types) == 1
            items_type = list(self.items_types)[0]
        self.get_items_type(items_type).subscriptions[field].add(callback)

    def launch(self):
        logging.info("Launching plugin {}".format(self.__class__.__name__))
        self.load_config()
        self.load_items()
        self.populate_schedule()
        self.setup_callbacks()

    def shutdown(self):
        self.dump_items()

    # ----------------------------------------------------
    # properties
    @property
    def items(self):  # won't do: this is defined on init stage so should only store it accordingly.
        # No - need self._items[type_name]
        if len(self._items) > 1:
            return self._items
        else:
            return next(iter(self._items.values()))

    @property
    def items_dump_dir(self):
        return os.path.join(self.pa.app_data_dir, "items", self.__class__.__name__)

    @property
    def items_types(self):
        # type: () -> list[PluginItem]
        return self._items_types.values()

    # ----------------------------------------------------
    # __getitem__, __getattr__
    def __getitem__(self, item):
        # type: (str) -> PluginItem or dict[str, PluginItem]
        return self.items[item]

    def create_item(self, item_class_name, uid=None, **kwargs):
        # type: (str, str, dict) -> PluginItem
        """
        creates PluginItem  # done
        Saves item into plugin.items[item_type]  # done
        registers item into uid.AssociatedItems  # done
        """
        if uid is not None:
            assert uid not in self._items[item_class_name]
        item = self._items_types[item_class_name](uid=uid, **kwargs)  # calls costructor
        self._items[item_class_name][item.uid] = item  # saves item into plugin.items, 1. Regiester item in the plugin
        self.pa.uid[item.uid].associated_items.append(item_class_name)
        return item


class PluginItemDescription(TPluginItemDesctription):
    __metaclass__ = ProtobufInheritanceMeta

    def __init__(self, plugin=None, name=None):
        self._proto = self.proto_type(Plugin=plugin, Name=name)

    @property
    def plugin(self):
        return self._proto.Plugin

    @plugin.setter
    def plugin(self, plugin):
        self._proto.Plugin = plugin

    @property
    def name(self):
        return self._proto.Name

    @name.setter
    def name(self, name):
        self._proto.Name = name
