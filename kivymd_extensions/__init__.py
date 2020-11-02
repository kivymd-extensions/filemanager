import os
import sys

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
sys.path.append(os.path.join(__path__[0], "filemanager"))
