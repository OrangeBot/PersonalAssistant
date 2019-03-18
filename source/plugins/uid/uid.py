import uuid

from proto.uid_pb2 import TUid
from source.plugins.base import PluginItem, Plugin


class UidItem(PluginItem, TUid):
    dependencies = {}

    def __init__(self, uid=None, associated_items=None):
        # this is core item so logic is slightly different from everything else
        uid = uid or self.generate_uid()
        assert uid not in self.plugin.items  # trying to initialize item with already existing uid - bad.
        associated_items = associated_items or []
        super(UidItem, self).__init__(uid=self.uid, associated_items=associated_items)

    @classmethod
    def generate_uid(cls):
        """
        Generate unique string identifier for PersonalAssistant item.
        """
        while True:
            uid = "pa_uid_" + str(uuid.uuid4())[:8]
            if uid not in cls._plugin.items:
                return uid

    @property
    def uid(self):
        return self._proto.Uid

    @uid.setter
    def uid(self, uid):
        self._proto.Uid = uid

    @property
    def associated_items(self):
        return self._proto.AssociatedItems

    @associated_items.setter
    def associated_items(self, associated_items):
        self._proto.AssociatedItems = associated_items


class Uid(Plugin, UidItem):
    def create_uid(self, uid=None, associated_items=None):
        uid = self.create_item('uid', uid=uid, associated_items=associated_items)
        return uid
