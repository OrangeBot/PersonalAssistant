from proto.folder_pb2 import TFolder
from source.plugins.base import PluginItem, Plugin


class FolderItem(PluginItem, TFolder):
    dependencies = {}  # don't need to always mention uid. PluginItemDescription(plugin='uid', name='uid')


class Folder(Plugin, FolderItem):
    def setup_callbacks(self):
        pass

    def populate_schedule(self):
        pass

    # todo launch: create_folder
