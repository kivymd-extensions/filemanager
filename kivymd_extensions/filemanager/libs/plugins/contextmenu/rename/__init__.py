import os

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from kivymd_extensions.filemanager.libs.plugins import PluginBaseDialog

with open(
    os.path.join(os.path.dirname(__file__), "rename.kv"), encoding="utf-8"
) as kv:
    Builder.load_string(kv.read())


class DialogRename(PluginBaseDialog):
    instance_context_menu = ObjectProperty()

    def set_focus(self, interval):
        self.ids.field.focus = True

    def rename_file(self, new_file_name):
        os.rename(
            self.instance_context_menu.entry_object.path,
            os.path.join(
                os.path.dirname(self.instance_context_menu.entry_object.path),
                new_file_name,
            ),
        )
        self.dismiss()

    def on_open(self):
        Clock.schedule_once(self.set_focus)
