# File Manager

<img align="left" width="128" src="https://github.com/kivymd-extensions/filemanager/raw/main/docs/sources/_static/logo-kivymd.png"/>

Desktop file manager developed on the Kivy platform using the KivyMD library.
Perhaps the file manager will work on mobile devices, but we are not even trying to check if this is the case.
We are not testing this library on mobile devices or adapting it for mobile devices.
Because, as the name suggests, we are developing this module for desktop use.

[![Documentation Status](https://readthedocs.org/projects/file-manager/badge/?version=latest)](https://file-manager.readthedocs.io/en/latest/?badge=latest)

## Installation

```bash
pip install kivymd_extensions.filemanager
```

### Dependencies:

- [KivyMD](https://github.com/kivymd/KivyMD) >= 0.104.1
- [Kivy](https://github.com/kivy/kivy) >= 1.10.1 ([Installation](https://kivy.org/doc/stable/gettingstarted/installation.html))
- [Python 3.6+](https://www.python.org/)

## Documentation

### Usage

```python
from kivymd.app import MDApp

from kivymd_extensions.filemanager import FileManager


class MainApp(MDApp):
    def on_start(self):
        FileManager().open()


if __name__ == "__main__":
    MainApp().run()
```

<p align="center">
  <a href="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-preview.png">
    <img width="800" src="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-preview.png" title="Preview file manager">
  </a>
</p>

### Customization

```python
FileManager(path_to_skin="/Users/macbookair/data/images").open()
```

<p align="center">
  <a href="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-custom.png">
    <img width="800" src="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-custom.png" title="Custom file manager">
  </a>
</p>

## Examples

```bash
git clone https://github.com/kivymd-extensions/filemanager.git
cd filemanager
cd examples/full_example
python main.py
```

### Support

If you need assistance or you have a question, you can ask for help on our mailing list:

- **Discord server:** https://discord.gg/wu3qBST
- _Email:_ kivydevelopment@gmail.com
