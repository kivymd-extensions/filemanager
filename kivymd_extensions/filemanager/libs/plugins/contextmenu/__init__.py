from .properties import DialogProperties
from .remove import DialogMoveToTrash
from .rename import DialogRename
from .ziparchive import DialogZipArchive


class ContextMenuPlugin:
    def __init__(self, instance_manager=None, entry_object=None):
        # <__main__.FileManager object>
        self.instance_manager = instance_manager
        # <kivy.lang.builder.FileThumbEntry object>
        self.entry_object = entry_object

        self.plugin_dialogs = {
            "rename": DialogRename,
            "move_to_trash": DialogMoveToTrash,
            "create_zip": DialogZipArchive,
        }

    def dismiss_plugin_dialog(self, instance_plugin_dialog, name_plugin):
        if name_plugin in self.plugin_dialogs.keys():
            self.instance_manager.update_files(
                instance_plugin_dialog, self.entry_object.path
            )
            self.instance_manager.dispatch("on_context_menu", name_plugin)

    def main(self, name_plugin):
        if name_plugin == "show_properties":
            DialogProperties(instance_context_menu=self, size_hint_x=0.6).open()
        if name_plugin in self.plugin_dialogs.keys():
            self.plugin_dialogs[name_plugin](
                instance_context_menu=self,
                size_hint_x=0.6,
                on_dismiss=lambda x, name_plugin=name_plugin: self.dismiss_plugin_dialog(
                    x, name_plugin
                ),
            ).open()
