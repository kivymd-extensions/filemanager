from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.modalview import ModalView

from kivymd.theming import ThemableBehavior


Builder.load_string(
    """
#:import images_path kivymd.images_path


<PluginBaseDialog>
    background:
        '{}/transparent.png'.format(images_path) \
        if not root.bg_background else root.bg_background

    canvas:
        Color:
            rgba:
                root.theme_cls.bg_light if not root.bg_color else root.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
"""
)


class PluginBaseDialog(ThemableBehavior, ModalView):
    """Base class for context menu windows."""

    bg_color = ListProperty()  # background color of the dialog
    bg_background = ListProperty()  # path to background image of the dialog
