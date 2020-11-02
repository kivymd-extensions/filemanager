import os

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.uix.filechooser import FileChooserController
from kivy.utils import QueryDict

Builder.load_string(
    """
[FileThumbEntry@Widget+HoverBehavior]:
    image: image
    locked: False
    path: ctx.path
    selected: self.path in ctx.controller().selection
    size_hint: None, None
    on_touch_down:
        root.entry_released_allow = True
        if self.collide_point(*args[1].pos): \
        ctx.controller().manager.tap_on_file_dir(args, "FileChooserIcon")
    on_touch_up:
        if not ctx.controller().manager.context_menu_open: self.collide_point(*args[1].pos) \
        and ctx.controller().entry_released(self, args[1]) and root.entry_released_allow
    size: ctx.controller().thumbsize + dp(52), ctx.controller().thumbsize + dp(52)
    #on_enter: ctx.controller().set_list_contents_preview(self, ctx.path)
    #on_leave:

    canvas:
        Color:
            rgba: 1, 1, 1, 1 if self.selected else 0
        BorderImage:
            border: 8, 8, 8, 8
            pos: root.pos
            size: root.size
            source: "atlas://data/images/defaulttheme/filechooser_selected"

    MDIconButton:
        id: image
        user_font_size:
            sp(int(ctx.controller().thumbsize)) \
            if self.icon == "folder" else sp(int(ctx.controller().thumbsize / 2))
        pos:
            root.x + (dp(12) if self.icon == "folder" else dp(32)), \
            root.y + (dp(40) if self.icon == "folder" else dp(56))
        theme_text_color: "Custom"
        pos_hint: {"center_x": .5}
        text_color:
            app.theme_cls.primary_color if self.icon == "folder" \
            else app.theme_cls.disabled_hint_text_color
        disabled: True

    MDLabel:
        text: ctx.name
        size_hint: None, None
        -text_size: (ctx.controller().thumbsize, self.height)
        halign: "center"
        shorten: True
        size: ctx.controller().thumbsize, "16dp"
        pos: root.center_x - self.width / 2, root.y + dp(32)
        color: ctx.controller().text_color
        font_style: "Caption"

    MDLabel:
        text: ctx.controller()._gen_label(ctx)
        font_style: "Caption"
        color: .8, .8, .8, 1
        size_hint: None, None
        -text_size: None, None
        size: ctx.controller().thumbsize, "16sp"
        pos: root.center_x - self.width / 2, root.y + dp(16)
        halign: "center"
        color: ctx.controller().text_color


<CustomFileChooserIcon>:
    on_entry_added: stack.add_widget(args[1])
    on_entries_cleared: stack.clear_widgets()
    _scrollview: scrollview

    ScrollView:
        id: scrollview
        do_scroll_x: False

        Scatter:
            do_rotation: False
            do_scale: False
            do_translation: False
            size_hint_y: None
            height: stack.height

            StackLayout:
                id: stack
                width: scrollview.width
                size_hint_y: None
                height: self.minimum_height
                spacing: "10dp"
                padding: "10dp"
"""
)


class CustomFileChooserIcon(FileChooserController):
    _ENTRY_TEMPLATE = "FileThumbEntry"

    thumbsize = NumericProperty(dp(72))
    """
    The size of the thumbnails.

    :attr:`thumbsize` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `dp(48)`.
    """

    icon_folder = StringProperty()
    """
    Path to icon folder.

    :attr:`icon_folder` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    text_color = ListProperty()
    """
    Label color for file and directory names.

    :attr:`text_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    get_icon_file = ObjectProperty()
    """
    Method that returns the icon path for the file.

    :attr:`get_icon_file` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    manager = ObjectProperty()
    """
    ``MDDesktopFileManager`` object.

    :attr:`manager` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_released_allow = False

    def entry_released(self, entry, touch):
        """
        This method must be called by the template when an entry
        is touched by the user.
        """

        # FIXME: For some reason, this method is called twice. So I had to
        #  redefine it and include the ``entry_released_allow`` variable to
        #  control the number of calls.
        if self.entry_released_allow:
            self.entry_released_allow = False
            if "button" in touch.profile and touch.button in (
                "scrollup",
                "scrolldown",
                "scrollleft",
                "scrollright",
            ):
                return False
            if not self.multiselect:
                if self.file_system.is_dir(entry.path) and not self.dirselect:
                    self.open_entry(entry)
                elif touch.is_double_tap:
                    if self.dirselect and self.file_system.is_dir(entry.path):
                        return
                    else:
                        self.dispatch("on_submit", self.selection, touch)

    def _create_entry_widget(self, ctx):
        widget = super()._create_entry_widget(ctx)
        kctx = QueryDict(ctx)
        if os.path.isdir(kctx["path"]):
            widget.image.icon = self.icon_folder
        else:
            if self.get_icon_file:
                widget.image.icon = self.get_icon_file(kctx["path"])

        return widget

    def _gen_label(self, ctx):
        return ctx.get_nice_size()
