# -*- coding: utf-8 -*-
from proto.folder_pb2 import TFolder
from source.plugins.base import PluginItem, Plugin


class FolderItem(PluginItem, TFolder):
    dependencies = {}  # don't need to always mention uid. PluginItemDescription(plugin='uid', name='uid')

    def __init__(self, uid=None):
        super(FolderItem, self).__init__(uid=uid)

    @property
    def uid(self):
        return self._proto.Uid

    @uid.setter
    def uid(self, uid):
        self._proto.Uid = uid

class Folder(Plugin, FolderItem):
    def setup_callbacks(self):
        pass

    def populate_schedule(self):
        pass

    # todo launch: create_folder
    def create_folder(self, uid=None):
        folder = self.create_item('folder', uid=uid)
        return folder
