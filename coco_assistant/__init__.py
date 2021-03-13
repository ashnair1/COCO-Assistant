import os
import pathlib

from .coco_assistant import COCO_Assistant
import coco_assistant

PACKAGE_ROOT = pathlib.Path(coco_assistant.__file__).resolve().parent
# PACKAGE_ROOT = os.getcwd()

with open(os.path.join(PACKAGE_ROOT, "VERSION")) as version_file:
    __version__ = version_file.read().strip()
