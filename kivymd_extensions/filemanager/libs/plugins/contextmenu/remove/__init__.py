import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from kivymd_extensions.filemanager.libs.plugins import PluginBaseDialog

with open(
    os.path.join(os.path.dirname(__file__), "remove.kv"), encoding="utf-8"
) as kv:
    Builder.load_string(kv.read())


class DialogMoveToTrash(PluginBaseDialog):
    instance_context_menu = ObjectProperty()
