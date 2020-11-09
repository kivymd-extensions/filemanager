import datetime
import os

from kivy.clock import Clock
from kivy.lang import Builder

from kivymd_extensions.filemanager.libs.plugins import PluginBaseDialog
from kivymd_extensions.filemanager.libs.tools import (
    file_size,
    get_access_string,
)

with open(
    os.path.join(os.path.dirname(__file__), "dialog_properties.kv"),
    encoding="utf-8",
) as kv:
    Builder.load_string(kv.read())


class DialogProperties(PluginBaseDialog):
    def get_first_created(self):
        return datetime.datetime.fromtimestamp(
            int(os.path.getctime(self.instance_context_menu.entry_object.path))
        )

    def get_last_opened(self):
        return datetime.datetime.fromtimestamp(
            int(os.path.getatime(self.instance_context_menu.entry_object.path))
        )

    def get_last_changed(self):
        return datetime.datetime.fromtimestamp(
            int(os.path.getmtime(self.instance_context_menu.entry_object.path))
        )

    def get_file_size(self):
        path = self.instance_context_menu.entry_object.path
        if os.path.isfile(path):
            return file_size(self.instance_context_menu.entry_object.path)
        else:
            count = 0
            for d, dirs, files in os.walk(path):
                count += len(files)
            return f"Count files {count}"

    def get_access_string(self):
        return get_access_string(self.instance_context_menu.entry_object.path)

    def set_access(self, interval):
        access_list = list(self.get_access_string())
        access_data = {
            "Read": self.ids.r,
            "Write": self.ids.w,
            "Executable": self.ids.x,
        }
        for i, access_text in enumerate(access_data.keys()):
            access_data[
                access_text
            ].text = f"[b]{access_text}:[/b] {'Yes' if access_list[i] != '-' else 'No'}"

    def on_instance_context_menu(self, instance, value):
        Clock.schedule_once(self.set_access)

    def on_pre_open(self):
        if os.path.isdir(self.instance_context_menu.entry_object.path):
            self.ids.container.remove_widget(self.ids.x)
