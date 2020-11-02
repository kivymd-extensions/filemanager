import os
import zipfile

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.utils import asynckivy

from kivymd_extensions.filemanager.libs.plugins import PluginBaseDialog

with open(
    os.path.join(os.path.dirname(__file__), "dialog_zip.kv"), encoding="utf-8"
) as kv:
    Builder.load_string(kv.read())


class DialogZipArchive(PluginBaseDialog):
    instance_context_menu = ObjectProperty()

    def set_progress_value(self, count_files, count):
        self.ids.progress_line.value = int(count / count_files * 100)

    def set_name_packed_file(self, file_name):
        self.ids.lbl_name_file.text = file_name

    def on_open(self):
        async def create_zip():
            if os.path.isdir(path):
                root_dir = os.path.basename(path)
                count = 0
                for dir_path, dir_names, file_names in os.walk(path):
                    await asynckivy.sleep(0)
                    for file_name in file_names:
                        count += 1
                        self.set_progress_value(count_files, count)
                        self.set_name_packed_file(file_name)
                        file_path = os.path.join(dir_path, file_name)
                        parentpath = os.path.relpath(file_path, path)
                        archive_name = os.path.join(root_dir, parentpath)
                        zip_file.write(file_path, archive_name)
            else:
                zip_file.write(path, os.path.split(path)[1])

            zip_file.close()
            self.dismiss()

        path = self.instance_context_menu.entry_object.path
        count_files = sum((len(f) for _, _, f in os.walk(path)))
        zip_file = zipfile.ZipFile(f"{path}.zip", "w", zipfile.ZIP_DEFLATED)
        asynckivy.start(create_zip())
