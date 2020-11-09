import os

from kivy.lang import Builder

from kivymd_extensions.filemanager.libs.plugins import PluginBaseDialog

with open(
    os.path.join(os.path.dirname(__file__), "remove.kv"), encoding="utf-8"
) as kv:
    Builder.load_string(kv.read())


class DialogMoveToTrash(PluginBaseDialog):
    pass
