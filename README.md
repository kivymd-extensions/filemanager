# File Manager

<img align="left" width="128" src="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-logo.png"/>

### Desktop file manager developed on the Kivy platform using the KivyMD library.

Perhaps the file manager will work on mobile devices, but we are not even trying to check if this is the case.
We are not testing this library on mobile devices or adapting it for mobile devices.
Because, as the name suggests, we are developing this module for desktop use.

### Usage

```python
from kivymd.app import MDApp

from kivymd.components.filemanager import FileManager


class Example(MDApp):
    def on_start(self):
        FileManager().open()

Example().run()
```

<p align="center">
  <a href="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-preview.png">
    <img width="800" src="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/filemanager/filemanager-preview.png" title="Preview file manager">
  </a>
</p>

### Installation

```bash
pip install kivymd-components
componemts install filemanager
```

### Dependencies

- [Kivy](https://github.com/kivy/kivy) >= 1.10.1 ([Installation](https://kivy.org/doc/stable/gettingstarted/installation.html))
- [KivyMD](https://github.com/kivymd/KivyMD) >= 0.104.2 (`pip install https://github.com/kivymd/KivyMD/archive/master.zip
`)
- [Python 3.6+](https://www.python.org/) _(Python 2 not supported)_

### Run demo

```batch
pip install kivymd-components
components install filemanager
git clone git@github.com:kivymd-components/filemanager.git
cd filemanager/demo
python main.py
```

### Support

If you need assistance or you have a question, you can ask for help on our mailing list:

- **Discord server:** https://discord.gg/HjHDr8s
- _Email:_ kivydevelopment@gmail.com
