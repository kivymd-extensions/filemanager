"""
Components/File Manager
=======================

File manager for the desktop.

.. image:: https://github.com/kivymd/storage/raw/main/filemanager/images/preview.png
    :align: center

.. warning::

    We have not tested the file manager for Windows OS. Therefore, we do not
    guarantee the absence of bugs in this OS. Contact `technical support <https://discord.gg/HjHDr8s>`_ if you
    have any problems using the file manager.

Usage
-----

.. code-block:: python

    from kivymd.app import MDApp

    from kivymd_extensions.filemanager import FileManager


    class Example(MDApp):
        def on_start(self):
            FileManager().open()

Customization
=============

If you want to use custom icons in the file manager, you need to specify the path to the icon theme:

.. code-block:: python

    FileManager(path_to_skin="path/to/images").open()

.. image:: https://github.com/kivymd/storage/raw/main/filemanager/images/customization.png
    :align: center

The resource directory structure for the file manager theme looks like this:

.. image:: https://github.com/kivymd/storage/raw/main/filemanager/images/skin-structure.png
    :align: center

The ``files`` directory contains images whose names correspond to the file types:

.. image:: https://github.com/kivymd/storage/raw/main/filemanager/images/skin-structure-files.png
    :align: center

Color
-----

.. code-block:: python

    FileManager(bg_color=(1, 0, 0, 0.2)).open()

.. image:: https://github.com/kivymd/storage/raw/main/filemanager/images/bg-color.png
    :align: center

Texture
-------

.. code-block:: python

    FileManager(bg_texture="path/to/texture.png").open()

.. image:: https://github.com/kivymd/storage/raw/main/filemanager/images/bg-texture.png
    :align: center

.. warning::

    If you are using ``bg_texture`` parameter then ``bg_color`` parameter will be ignored.

Events
======

    `on_tab_switch`
        Called when switching tabs.
    `on_tap_file`
        Called when the file is clicked.
    `on_tap_dir`
        Called when the folder is clicked.
    `on_context_menu`
        Called at the end of any actions of the context menu,
        be it copying, archiving files and other actions.

.. code-block::

    from kivymd.app import MDApp

    from kivymd_extensions.filemanager import FileManager


    class Example(MDApp):
        def on_context_menu(self, instance_file_manager, name_context_plugin):
            print("Event 'on_context_menu'", instance_file_manager, name_context_plugin)

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

        def build(self):
            self.theme_cls.primary_palette = "Red"

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
"""

import re
import ast
import importlib
import os
import threading

from kivy.factory import Factory
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import (
    StringProperty,
    ObjectProperty,
    BooleanProperty,
    ListProperty,
    OptionProperty,
    DictProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config, ConfigParser
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, get_hex_from_color

Config.set("input", "mouse", "mouse,disable_multitouch")

from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.list import (
    OneLineAvatarIconListItem,
    OneLineListItem,
    OneLineAvatarListItem,
    ILeftBody,
)
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.dialog import BaseDialog
from kivymd.font_definitions import fonts
from kivymd.icon_definitions import md_icons
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDSeparator
from kivymd.color_definitions import palette
from kivymd.color_definitions import colors
from kivymd.uix.expansionpanel import MDExpansionPanel
from kivymd.uix.expansionpanel import MDExpansionPanelOneLine
from kivymd.uix.relativelayout import MDRelativeLayout

from kivymd_extensions.filemanager.libs.plugins import PluginBaseDialog

with open(
    os.path.join(os.path.dirname(__file__), "file_chooser_list.kv"),
    encoding="utf-8",
) as kv:
    Builder.load_string(kv.read())
with open(
    os.path.join(os.path.dirname(__file__), "custom_splitter.kv"),
    encoding="utf-8",
) as kv:
    Builder.load_string(kv.read())
with open(
    os.path.join(os.path.dirname(__file__), "filemanager.kv"),
    encoding="utf-8",
) as kv:
    Builder.load_string(kv.read())


class RightContentCls(RightContent):
    pass


class FileManagerTab(BoxLayout, MDTabsBase):
    """Class implementing content for a tab."""

    manager = ObjectProperty()
    """
    :class:`FileManager` object.
    """

    path = StringProperty()
    """
    Path to root directory for instance :attr:`manager`.

    :attr:`path` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """


class FileManagerTextFieldSearch(ThemableBehavior, MDRelativeLayout):
    """The class implements a text field for searching files.

    See rule ``FileManagerTextFieldSearch``
    in ``kivymd_extensions/filemanager/filemanager.kv file``.
    """

    hint_text = StringProperty()
    """
    See :attr:`~kivy.uix.textinput.TextInput.hint_text
    """

    background_normal = StringProperty()
    """
    See :attr:`~kivy.uix.textinput.TextInput.background_normal
    """

    background_active = StringProperty()
    """
    See :attr:`~kivy.uix.textinput.TextInput.background_active
    """

    type = OptionProperty("name", options=["name", "ext"])
    """
    Search files by name or extension. Available options are `'name'`, `'ext'`.

    :attr:`icon` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'name'`.
    """

    manager = ObjectProperty()
    """
    See :class:`FileManager` object.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        # Signal to interrupt the search process
        self.canceled_search = False
        # <FileManagerTextFieldSearchDialog object>
        self.text_field_search_dialog = None
        # <kivymd.uix.menu.MDDropdownMenu object>
        self.context_menu_search_field = None
        # Whether to search the entire disk or the current directory.
        self.search_all_disk = False
        self.end_search = False
        Clock.schedule_once(self.create_menu)

    def on_enter(self, instance, value):
        """Called when the user hits 'Enter' in text field."""

        def wait_result(interval):
            if self.end_search:
                Clock.unschedule(wait_result)
                if data_results:
                    FileManagerFilesSearchResultsDialog(
                        data_results=data_results, manager=self.manager
                    ).open()
                    self.manager.dialog_files_search_results_open = True

        def start_search(interval):
            threading.Thread(
                target=get_matching_files,
                args=(
                    "/" if self.search_all_disk else self.manager.path,
                    value,
                ),
            ).start()

        def get_matching_files(path, name_file):
            for d, dirs, files in os.walk(path):
                if self.canceled_search:
                    break
                self.text_field_search_dialog.ids.lbl_dir.text = d
                for f in files:
                    self.text_field_search_dialog.ids.lbl_file.text = f
                    self.manager.ids.lbl_task.text = (
                        f"Search in [color="
                        f"{get_hex_from_color(self.theme_cls.primary_color)}]"
                        f"{os.path.dirname(d)}:[/color] {f}"
                    )
                    if self.ids.text_field.hint_text == "Search by name":
                        if name_file in f:
                            data_results[f] = os.path.join(d, f)
                    elif self.ids.text_field.hint_text == "Search by extension":
                        if f.endswith(name_file):
                            data_results[f] = os.path.join(d, f)
            if self.canceled_search:
                self.canceled_search = False
            self.end_search = True
            self.text_field_search_dialog.dismiss()

        self.text_field_search_dialog = FileManagerTextFieldSearchDialog(
            manager=self.manager
        )
        self.text_field_search_dialog.open()
        self.end_search = False
        data_results = {}
        Clock.schedule_once(start_search, 1)
        Clock.schedule_interval(wait_result, 0)

    def create_menu(self, interval):
        menu = []
        for text in (
            "Search by extension",
            "Search by name",
            "All over the disk",
        ):
            menu.append(
                {
                    "text": f"[size=14]{text}[/size]",
                    "height": "36dp",
                    "top_pad": "4dp",
                    "bot_pad": "10dp",
                    "divider": None,
                }
            )
        self.context_menu_search_field = MDDropdownMenu(
            caller=self.ids.lbl_icon_right,
            items=menu,
            width_mult=4,
            background_color=self.theme_cls.bg_dark,
            max_height=dp(240),
        )
        self.context_menu_search_field.bind(on_release=self.set_type_search)

    def set_type_search(self, instance_context_menu, instance_context_item):
        self.context_menu_search_field.dismiss()
        self.search_all_disk = False
        item_text = re.sub(
            "\[size\s*([^\]]+)\]", "", instance_context_item.text
        )
        item_text = re.sub("\[/size\s*\]", "", item_text)
        if item_text == "Search by extension":
            self.type = "ext"
        elif item_text == "Search by name":
            self.type = "name"
        elif item_text == "All over the disk":
            self.search_all_disk = True
            self.ids.text_field.hint_text += f" {item_text.lower()}"
            return
        self.ids.text_field.hint_text = item_text


class FileManagerFilesSearchResultsDialog(PluginBaseDialog):
    """
    The class implements displaying a list with the results of file search.
    """

    data_results = DictProperty()

    manager = ObjectProperty()
    """
    See :class:`FileManager` object.
    """

    def on_open(self):
        self.ids.rv.data = []
        for name_file in self.data_results.keys():
            text = (
                f"[color={get_hex_from_color(self.theme_cls.primary_color)}]"
                f"{name_file}[/color] {self.data_results[name_file]}"
            )
            self.ids.rv.data.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": text,
                    "on_release": lambda x=self.data_results[name_file]: self.go_to_directory_found_file(x)
                }
            )

    def on_dismiss(self):
        self.manager.dialog_files_search_results_open = False

    def go_to_directory_found_file(self, path_to_found_file):
        self.manager.add_tab(os.path.dirname(path_to_found_file))


class FileManagerSettingsLeftWidgetItem(ILeftBody, Widget):
    pass


class FileManagerSettingsColorItem(OneLineAvatarListItem):
    color = ListProperty()


class FileManagerSettings(MDBoxLayout):
    pass


class FileManagerTextFieldSearchDialog(PluginBaseDialog):
    manager = ObjectProperty()


class ContextMenuBehavior(ThemableBehavior, HoverBehavior):
    def on_enter(self):
        self.bg_color = (
            self.theme_cls.bg_light
            if self.theme_cls.theme_style == "Dark"
            else self.theme_cls.bg_darkest
        )

    def on_leave(self):
        self.bg_color = self.theme_cls.bg_normal


class ContextMenuItemMore(OneLineAvatarIconListItem, ContextMenuBehavior):
    """Context menu item."""

    icon = StringProperty()
    """
    Icon of item.

    :attr:`icon` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids._right_container.size = (dp(24), dp(48))


class ContextMenuItem(OneLineListItem, ContextMenuBehavior):
    """Context menu item."""

    icon = StringProperty()
    """
    Icon of item.

    :attr:`icon` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._txt_left_pad = dp(16)
        self._txt_bot_pad = dp(10)


class FileManager(BaseDialog):
    """
    :Events:
        `on_tab_switch`
            Called when switching tabs.
        `on_tap_file`
            Called when the file is clicked.
        `on_tap_dir`
            Called when the folder is clicked.
        `on_context_menu`
            Called at the end of any actions of the context menu,
            be it copying, archiving files and other actions.
        `on_open_plugin_dialog`
            Description.
        `on_dismiss_plugin_dialog`
            Description.
    """

    with open(
        os.path.join(
            os.path.dirname(__file__), "data", "context-menu-items.json"
        ),
        encoding="utf-8",
    ) as data:
        menu_right_click_items = ast.literal_eval(data.read())

    path = StringProperty(os.getcwd())
    """
    The path to the directory in which the file manager will open by
    default.

    :attr:`path` is an :class:`~kivy.properties.StringProperty`
    and defaults to ``os.getcwd()``.
    """

    context_menu_open = BooleanProperty(False)
    """
    Open or close context menu.

    :attr:`context_menu_open` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    path_to_skin = StringProperty()
    """
    Path to directory with custom images.

    :attr:`path_to_skin` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    bg_color = ListProperty()
    """
    Background color of file manager in the format (r, g, b, a).

    :attr:`bg_color` is a :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    bg_texture = StringProperty()
    """
    Background texture of file manager.

    :attr:`bg_texture` is a :class:`~kivy.properties.StringProperty` and
    defaults to `''`.
    """

    _overlay_color = ListProperty([0, 0, 0, 0])

    auto_dismiss = False

    _instance_file_chooser_icon = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ext_files = {}
        # The object of the currently open tab.
        self.current_open_tab_manager = None
        # Open or closed the settings panel.
        self.settings_panel_open = False
        # Open or close the theme selection panel in the settings panel.
        self.settings_theme_panel_open = False
        # Open or close the dialog of plugin.
        self.dialog_plugin_open = False
        # Open or close dialog with search results.
        self.dialog_files_search_results_open = False

        self.instance_search_field = None

        self.config = ConfigParser()
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.config.read(os.path.join(self.data_dir, "settings.ini"))

        self.register_event_type("on_tab_switch")
        self.register_event_type("on_tap_file")
        self.register_event_type("on_tap_dir")
        self.register_event_type("on_context_menu")
        self.register_event_type("on_open_plugin_dialog")
        self.register_event_type("on_dismiss_plugin_dialog")

        self.theme_cls.bind(theme_style=self.update_background_search_field)

        if self.path_to_skin and os.path.exists(self.path_to_skin):
            path_to_directory_exts = os.path.join(self.path_to_skin, "files")
            for name_file in os.listdir(path_to_directory_exts):
                self.ext_files[name_file.split(".")[0]] = os.path.join(
                    path_to_directory_exts, name_file
                )
        if not self.ext_files:
            with open(
                os.path.join(
                    os.path.dirname(__file__), "data", "default_files_type.json"
                ),
                encoding="utf-8",
            ) as data:
                self.ext_files = ast.literal_eval(data.read())

    def add_color_panel(self):
        def set_list_colors_themes(*args):
            self.settings_theme_panel_open = True
            if not theme_panel.content.ids.rv.data:
                for name_theme in palette:
                    theme_panel.content.ids.rv.data.append(
                        {
                            "viewclass": "FileManagerSettingsColorItem",
                            "color": get_color_from_hex(
                                colors[name_theme]["500"]
                            ),
                            "text": name_theme,
                            "manager": self,
                        }
                    )

        # Adds a panel.
        theme_panel = MDExpansionPanel(
            icon="palette",
            content=Factory.FileManagerChangeTheme(),
            panel_cls=MDExpansionPanelOneLine(text="Select theme"),
        )
        theme_panel.bind(
            on_open=set_list_colors_themes,
            on_close=self._set_state_close_theme_panel,
        )
        self.ids.settings.add_widget(theme_panel)

        # Adds a close button to the settings panel.
        box = MDBoxLayout(adaptive_height=True)
        box.add_widget(Widget())
        box.add_widget(
            MDFlatButton(
                text="CLOSE",
                on_release=lambda x: self.hide_settings(theme_panel),
            )
        )
        self.ids.settings.add_widget(box)

    def apply_palette(self):
        """Applies the color theme from the settings file when opening the
        file manager window."""

        palette = self.config.get("General", "palette")
        theme = self.config.get("General", "theme")
        memorize_palette = self.config.getint("General", "memorize_palette")

        if memorize_palette:
            self.theme_cls.primary_palette = palette
            self.theme_cls.theme_style = theme

    def apply_properties_on_show_settings(self):
        """Applies the settings from the "settings.ini" file to the checkboxes
        of items on the settings panel."""

        self.ids.settings.ids.tooltip_check.active = self.config.getint(
            "General", "tooltip"
        )
        self.ids.settings.ids.memorize_check.active = self.config.getint(
            "General", "memorize_palette"
        )
        self.ids.settings.ids.theme_switch.active = (
            1 if self.theme_cls.theme_style == "Dark" else 0
        )

    def show_taskbar(self):
        def on_complete_animation(*args):
            self.ids.task_spinner.active = True
            self.ids.lbl_task.opacity = 1

        Animation(height=dp(24), d=0.2).start(self.ids.taskbar)
        Animation(user_font_size=sp(18), d=0.2).start(self.ids.button_expand)
        anim = Animation(opacity=1, d=0.2)
        anim.bind(on_complete=on_complete_animation)
        anim.start(self.ids.task_spinner)

    def hide_taskbar(self):
        def on_complete_animation(*args):
            self.ids.task_spinner.active = False
            self.ids.lbl_task.opacity = 0
            self.instance_search_field.text_field_search_dialog.ids.check_background.active = (
                False
            )
            self.instance_search_field.text_field_search_dialog.open()

        Animation(height=0, d=0.2).start(self.ids.taskbar)
        Animation(user_font_size=0.1, d=0.2).start(self.ids.button_expand)
        anim = Animation(opacity=1, d=0.2)
        anim.bind(on_complete=on_complete_animation)
        anim.start(self.ids.task_spinner)

    def show_settings(self, instance_button):
        """Opens the settings panel."""

        self.apply_properties_on_show_settings()
        Animation(
            settings_container_y=self.ids.settings.height,
            d=0.2,
        ).start(self.ids.settings_container)
        Animation(
            _overlay_color=[0, 0, 0, 0.4],
            d=0.2,
        ).start(self)
        self.settings_panel_open = True

    def hide_settings(self, theme_panel):
        """Closes the settings panel."""

        def hide_settings(interval):
            Animation(settings_container_y=0, d=0.2).start(
                self.ids.settings_container
            )
            self._set_state_close_theme_panel()

        if self.settings_theme_panel_open:
            theme_panel.check_open_panel(theme_panel)
        Clock.schedule_once(hide_settings, 0.5)
        Animation(
            _overlay_color=[0, 0, 0, 0],
            d=0.2,
        ).start(self)
        self.settings_panel_open = False

    def set_path(self, path):
        """Sets the directory path for the `FileChooserIconLayout` class."""

        self.path = path
        self.current_open_tab_manager.ids.file_chooser_icon.path = path
        tab_text = self.get_formatting_text_for_tab(os.path.split(path)[1])
        self.current_open_tab_manager.text = tab_text

    def get_formatting_text_for_tab(self, text):
        icon_font = fonts[-1]["fn_regular"]
        icon = md_icons["close"]
        text = f"[size=16][font={icon_font}][ref=]{icon}[/ref][/size][/font] {text}"
        return text

    def add_tab(self, path_to_file):
        """
        Adds a new tab in the file manager.

        :param path_to_file: The path to the file or folder that was right-clicked.
        """

        tab_text = self.get_formatting_text_for_tab(
            os.path.split(path_to_file)[1]
        )
        tab = FileManagerTab(manager=self, text=tab_text, path=path_to_file)
        self._instance_file_chooser_icon = tab.ids.file_chooser_icon
        self.ids.tabs.add_widget(tab)
        self.current_open_tab_manager = tab
        self.ids.tabs.switch_tab(tab_text)
        self.path = path_to_file

    def remove_tab(
        self,
        instance_tabs,
        instance_tab_label,
        instance_tab,
        instance_tab_bar,
        instance_carousel,
    ):
        """Removes an open tab in the file manager.

        :param instance_tabs: <kivymd.uix.tab.MDTabs object>
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>
        :param instance_tab: <__main__.Tab object>
        :param instance_tab_bar: <kivymd.uix.tab.MDTabsBar object>
        :param instance_carousel: <kivymd.uix.tab.MDTabsCarousel object>
        """

        for instance_tab in instance_carousel.slides:
            if instance_tab.text == instance_tab_label.text:
                instance_tabs.remove_widget(instance_tab_label)
                break

    def create_header_menu(self):
        """Creates a menu in the file manager header."""

        with open(
            os.path.join(os.path.dirname(__file__), "data", "header_menu.json"),
            encoding="utf-8",
        ) as data:
            menu_header = ast.literal_eval(data.read())
            for name_icon_item in menu_header:
                self.ids.header_box_menu.add_widget(
                    MDIconButton(
                        icon=name_icon_item,
                        user_font_size="18sp",
                        disabled=True
                        if name_icon_item not in ("home", "settings")
                        else False,
                        md_bg_color_disabled=(0, 0, 0, 0),
                    )
                )
        self.ids.header_box_menu.add_widget(MDSeparator(orientation="vertical"))
        self.ids.header_box_menu.add_widget(
            MDIconButton(
                icon="cog",
                user_font_size="18sp",
                on_release=self.show_settings,
            )
        )
        background_normal = os.path.join(
            self.data_dir,
            "images",
            "bg-field.png"
            if self.theme_cls.theme_style == "Light"
            else "bg-field-dark.png",
        )
        self.instance_search_field = FileManagerTextFieldSearch(
            background_normal=background_normal,
            background_active=background_normal,
            manager=self,
        )
        self.ids.header_box_menu.add_widget(Widget())
        self.ids.header_box_menu.add_widget(self.instance_search_field)

    def update_background_search_field(self, instance, value):
        background_normal = os.path.join(
            self.data_dir,
            "images",
            "bg-field.png" if value == "Light" else "bg-field-dark.png",
        )
        self.instance_search_field.background_normal = background_normal
        self.instance_search_field.background_active = background_normal

    def open_context_menu(self, entry_object, type_chooser):
        """Opens a context menu on right-clicking on a file or folder."""

        menu = MDDropdownMenu(
            caller=entry_object,
            items=self.get_menu_right_click(entry_object, type_chooser),
            width_mult=4,
            background_color=self.theme_cls.bg_dark,
            max_height=dp(240),
        )
        menu.bind(
            on_release=lambda *args: self.tap_to_context_menu_item(
                *args, entry_object
            ),
            on_dismiss=self.context_menu_dismiss,
        )
        menu.open()
        self.context_menu_open = True

    def tap_on_file_dir(self, *touch):
        """Called when the file/dir is clicked."""

        type_click = touch[0][1].button
        # "FileChooserList" or "FileChooserIcon".
        type_chooser = touch[1]
        # FileThumbEntry object from file_chooser_icon.py file.
        entry_object = touch[0][0]

        if type_click == "right" and entry_object.path != "../":
            self.open_context_menu(entry_object, type_chooser)
        else:
            if entry_object.path == "../":
                entry_object.path = os.path.dirname(self.path)
            entry_object.collide_point(
                *touch[0][1].pos
            ) and self._instance_file_chooser_icon.entry_touched(
                entry_object, touch[0][1]
            )
            if os.path.isdir(entry_object.path):
                self.set_path(entry_object.path)
                self.dispatch("on_tap_dir", entry_object.path)
            else:
                self.dispatch("on_tap_file", entry_object.path)
        if hasattr(entry_object, "remove_tooltip"):
            entry_object.remove_tooltip()

    def call_context_menu_plugin(self, name_plugin, entry_object):
        module = importlib.import_module(
            f"kivymd_extensions.filemanager.libs.plugins.contextmenu"
        )
        plugin_cls = module.ContextMenuPlugin(
            instance_manager=self,
            entry_object=entry_object,
        )
        plugin_cls.main(name_plugin)

    def tap_to_context_menu_item(
        self, instance_menu, instance_item, entry_object
    ):
        """
        :type entry_object:  <kivy.lang.builder.FileThumbEntry object>
        :type instance_item: <kivymd.uix.menu.MDMenuItemIcon object>
        :type instance_menu: <kivymd.uix.menu.MDDropdownMenu object>
        """

        for data_item in self.menu_right_click_items:
            if (
                list(data_item.items())
                and instance_item.text in list(data_item.items())[0]
            ):
                if "cls" in data_item:
                    self.call_context_menu_plugin(
                        data_item["cls"], entry_object
                    )
                    break

        if instance_item.text == "Open in new tab":
            self.add_tab(entry_object.path)
            self.dismiss_context_menu()

    def dismiss_context_menu(self):
        if self.context_menu_open:
            for widget in Window.children:
                if isinstance(widget, MDDropdownMenu):
                    widget.dismiss()
                    break

    def context_menu_dismiss(self, *args):
        """Called when closing the context menu."""

        self.context_menu_open = False

    def get_menu_right_click(self, entry_object, type_chooser):
        """Returns a list of dictionaries for creating context menu items."""

        menu_right_click_items = []
        if type_chooser == "FileChooserIcon":
            for data_item in self.menu_right_click_items:
                if data_item:
                    if list(data_item.items())[0][1].endswith(">"):
                        menu_right_click_items.append(
                            {
                                "right_content_cls": RightContentCls(
                                    icon="menu-right-outline",
                                ),
                                "icon": list(data_item.items())[0][0],
                                "text": list(data_item.items())[0][1][:-2],
                                "height": "36dp",
                                "top_pad": "4dp",
                                "bot_pad": "10dp",
                                "divider": None,
                            }
                        )
                    else:
                        menu_right_click_items.append(
                            {
                                "text": list(data_item.items())[0][1],
                                "icon": list(data_item.items())[0][0],
                                "font_style": "Caption",
                                "height": "36dp",
                                "divider": None,
                                "top_pad": "4dp",
                                "bot_pad": "10dp",
                            }
                        )
                else:
                    menu_right_click_items.append(
                        {"viewclass": "MDSeparator", "height": dp(1)}
                    )
        if type_chooser == "FileChooserList":
            menu_right_click_items.append(
                {
                    "text": "Open in new tab",
                    "font_style": "Caption",
                    "height": "36dp",
                    "divider": None,
                    "top_pad": "4dp",
                    "bot_pad": "10dp",
                }
            )
        return menu_right_click_items

    def get_icon_file(self, path_to_file):
        """Method that returns the icon path for the file."""

        return self.ext_files.get(
            os.path.splitext(path_to_file)[1].replace(".", ""),
            os.path.join(self.path_to_skin, "file.png")
            if self.path_to_skin
            else "file-outline",
        )

    def update_files(self, instance_pludin_dialog, path):
        # FIXME: Unable to update directory. You have to go to a higher level
        #  and go back.
        self.set_path(os.getcwd())
        self.set_path(os.path.dirname(path))

    def is_dir(self, directory, filename):
        return os.path.isdir(os.path.join(directory, filename))

    def on_tap_file(self, *args):
        """Called when the file is clicked."""

    def on_tap_dir(self, *args):
        """Called when the folder is clicked."""

    def on_tab_switch(self, *args):
        """Called when switching tab."""

    def on_open_plugin_dialog(self, *args):
        self.dialog_plugin_open = True

    def on_dismiss_plugin_dialog(self, *args):
        self.dialog_plugin_open = False

    def on_context_menu(self, *args):
        """
        Called at the end of any actions of the context menu, be it copying,
        archiving files and other actions.
        """

    def on_open(self):
        """Called when the ModalView is opened."""

        self.add_tab(self.path)
        self.create_header_menu()
        self.apply_palette()
        self.add_color_panel()

    def _on_tab_switch(
        self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        self.current_open_tab_manager = instance_tab
        self.dispatch(
            "on_tab_switch",
            instance_tabs,
            instance_tab,
            instance_tab_label,
            tab_text,
        )

    def _set_state_close_theme_panel(self, *args):
        self.settings_theme_panel_open = False
