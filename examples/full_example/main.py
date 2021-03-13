from kivymd.app import MDApp

from kivymd_extensions.filemanager import FileManager


class Example(MDApp):
    def on_context_menu(self, instance_file_manager, name_context_plugin):
        print(
            "Event 'on_context_menu'",
            instance_file_manager,
            name_context_plugin,
        )

    def on_tap_file(self, instance_file_manager, path):
        print("Event 'on_tap_file'", instance_file_manager, path)

    def on_tap_dir(self, instance_file_manager, path):
        print("Event 'on_tap_dir'", instance_file_manager, path)

    def on_tab_switch(
        self,
        instance_file_manager,
        instance_tabs,
        instance_tab,
        instance_tab_label,
        tab_text,
    ):
        print(
            "Event 'on_tab_switch'",
            instance_file_manager,
            instance_tabs,
            instance_tab,
            instance_tab_label,
            tab_text,
        )

    def on_start(self):
        manager = FileManager()
        manager.bind(
            on_tap_file=self.on_tap_file,
            on_tap_dir=self.on_tap_dir,
            on_tab_switch=self.on_tab_switch,
            on_context_menu=self.on_context_menu,
        )
        manager.open()


Example().run()
