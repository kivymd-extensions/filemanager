__version__ = "0.1.1"

from kivy.factory import Factory

from kivymd_extensions.filemanager.libs import tools
from kivymd_extensions.filemanager.filemanager import FileManager

Factory.register(
    "CustomFileChooserIcon",
    module="kivymd_extensions.filemanager.file_chooser_icon",
)
