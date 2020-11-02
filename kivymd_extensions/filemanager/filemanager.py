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

import ast
import importlib
import os

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    StringProperty,
    ObjectProperty,
    BooleanProperty,
    ListProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.utils import get_hex_from_color
from kivymd.font_definitions import fonts
from kivymd.icon_definitions import md_icons

Config.set("input", "mouse", "mouse,disable_multitouch")

from kivymd.uix.menu import MDDropdownMenu, RightContent
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineListItem
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.dialog import BaseDialog

# Loading overridden rules.
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

Builder.load_string(
    """
#:import os os
#:import Path pathlib.Path
#:import images_path kivymd.images_path


<RightContentCls>
    disabled: True
    size_hint_x: None
    width: icon.width
    pos_hint: {"right": 1}

    MDIconButton:
        id: icon
        icon: root.icon
        user_font_size: "16sp"
        pos_hint: {"center_y": .5}
        #md_bg_color_disabled: 0, 0, 0, 0


<FileManager>

    MDBoxLayout:
        orientation: "vertical"
        padding: "5dp"
        md_bg_color: root.theme_cls.bg_normal if not root.bg_color else root.bg_color

        canvas:
            Rectangle:
                pos: self.pos
                size: self.size
                source:
                    os.path.join(images_path, "transparent.png") \
                    if not root.bg_texture else root.bg_texture

        MDBoxLayout:
            id: header_box_menu
            adaptive_height: True
            md_bg_color:
                (0, 0, 0, 0) if root.bg_texture \
                else (root.theme_cls.bg_dark if not root.bg_color else root.bg_color)

        MDBoxLayout:
            adaptive_height: True
            spacing: "10dp"

            MDTextField:
                id: field_current_path
                font_size: "13sp"
                text: root.path

        MDTabs:
            id: tabs
            tab_bar_height: "24dp"
            background_color: header_box_menu.md_bg_color
            color_indicator: app.theme_cls.primary_color
            text_color_normal: 1, 1, 1, 1
            text_color_active: 1, 1, 1, 1
            allow_stretch: False
            elevation: 0  #8
            tab_indicator_height: 2
            on_ref_press: root.remove_tab(*args)
            on_tab_switch: root._on_tab_switch(*args)


<Tab>
    padding: 0, "2dp", 0, 0

    Splitter:
        direction: "right-left"
        sizable_from: "right"
        rescale_with_parent: False
        size_hint_x: .4
        strip_size: "5dp"

        MDBoxLayout:
            md_bg_color: app.theme_cls.bg_dark

            # Directory tree on the left.
            FileChooserListView:
                id: file_chooser_list
                path: str(Path.home())
                filters: [root.manager.is_dir]
                callback: root.manager.set_path
                manager: root.manager

                canvas.before:
                    Color:
                        rgba:
                            root.manager.theme_cls.bg_dark \
                            if not root.manager.bg_color \
                            else root.manager.bg_color
                    Rectangle:
                        pos: self.pos
                        size: self.size

    CustomFileChooserIcon:
        id: file_chooser_icon
        icon_folder:
            os.path.join(root.manager.path_to_skin, "folder.png") \
            if root.manager.path_to_skin else "folder"
        get_icon_file: root.manager.get_icon_file
        text_color: app.theme_cls.text_color
        path: root.manager.path if not root.path else root.path
        manager: root.manager


<ContextMenuItemMore>
    text: root.text
    font_style: "Caption"
    _txt_left_pad: "16dp"
    _txt_bot_pad: "10dp"

    IconRightWidget:
        icon: root.icon
        user_font_size: "20sp"
        disabled: True
"""
)


class RightContentCls(RightContent):
    pass


class Tab(BoxLayout, MDTabsBase):
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

    auto_dismiss = False

    _instance_file_chooser_icon = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ext_files = {}
        self.current_open_tab_manager = None

        self.register_event_type("on_tab_switch")
        self.register_event_type("on_tap_file")
        self.register_event_type("on_tap_dir")
        self.register_event_type("on_context_menu")

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

    def set_path(self, path):
        """Sets the directory path for the `FileChooserIconLayout` class."""

        self.path = path
        self.current_open_tab_manager.ids.file_chooser_icon.path = path
        tab_text = self.get_formatting_text_for_tab(os.path.split(path)[1])
        self.current_open_tab_manager.text = tab_text

    def get_formatting_text_for_tab(self, text):
        icon_font = fonts[-1]["fn_regular"]
        icon = md_icons["close"]
        text = (
            f"[color={get_hex_from_color(self.theme_cls.text_color)}]"
            f"[size=16][font={icon_font}][ref=]{icon}[/ref][/size][/font]"
            f" {text}[/color]"
        )
        return text

    def add_tab(self, path_to_file):
        """
        Adds a new tab in the file manager.
        :param path_to_file: The path to the file or folder that was right-clicked.
        """

        tab_text = self.get_formatting_text_for_tab(os.path.split(path_to_file)[1])
        tab = Tab(manager=self, text=tab_text, path=path_to_file)
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
                        if name_icon_item not in ["home", "settings"]
                        else False,
                        md_bg_color_disabled=(0, 0, 0, 0),
                    )
                )

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

    def call_context_menu_plugin(self, name_plugin, entry_object):
        module = importlib.import_module(f"kivymd_extensions.filemanager.libs.plugins.contextmenu")
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

    def on_context_menu(self, *args):
        """
        Called at the end of any actions of the context menu, be it copying,
        archiving files and other actions.
        """

    def on_open(self):
        """Called when the ModalView is opened."""

        self.add_tab(self.path)
        self.create_header_menu()

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
