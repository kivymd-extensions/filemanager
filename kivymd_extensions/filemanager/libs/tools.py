import string
import os

from os import walk
from os.path import expanduser, isdir, dirname, join, sep

from kivy.utils import platform


def convert_bytes(num):
    """Convert bytes to MB.... GB... etc."""

    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """Return the file size."""

    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def get_access_string(path):
    """Return strind `rwx`."""

    access_string = ""
    access_data = {"r": os.R_OK, "w": os.W_OK, "x": os.X_OK}
    for access in access_data.keys():
        access_string += access if os.access(path, access_data[access]) else "-"
    return access_string


def get_icon_for_treeview(path, ext, isdir):
    icon_image = "file"
    if isdir:
        access_string = get_access_string(path)
        if "r" not in access_string:
            icon_image = "folder-lock"
        else:
            icon_image = "folder"
    else:
        if ext == ".py":
            icon_image = "language-python"
    return icon_image


def get_home_directory():
    if platform == "win":
        user_path = expanduser("~")
        if not isdir(join(user_path, "Desktop")):
            user_path = dirname(user_path)
    else:
        user_path = expanduser("~")

    return user_path


def get_drives():
    drives = []
    if platform == "win":
        from ctypes import windll, create_unicode_buffer

        bitmask = windll.kernel32.GetLogicalDrives()
        GetVolumeInformationW = windll.kernel32.GetVolumeInformationW

        for letter in string.ascii_uppercase:
            if bitmask & 1:
                name = create_unicode_buffer(64)
                # get name of the drive
                drive = letter + ":"
                res = GetVolumeInformationW(
                    drive + sep, name, 64, None, None, None, None, 0
                )
                if isdir(drive):
                    drives.append((drive, name.value))
            bitmask >>= 1
    elif platform == "linux":
        drives.append((sep, sep))
        drives.append((expanduser("~"), "~/"))
        places = (sep + "mnt", sep + "media")
        for place in places:
            if isdir(place):
                for directory in next(walk(place))[1]:
                    drives.append((place + sep + directory, directory))
    elif platform == "macosx":
        drives.append((expanduser("~"), "~/"))
        vol = sep + "Volume"
        if isdir(vol):
            for drive in next(walk(vol))[1]:
                drives.append((vol + sep + drive, drive))
    return drives
