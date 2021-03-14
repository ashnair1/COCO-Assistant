#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.install import install

# Package meta-data.
NAME = "coco_assistant"
DESCRIPTION = "Helper for dealing with MS-COCO annotations"
URL = "https://github.com/ashnair1/COCO-Assistant"
EMAIL = "ash1995@gmail.com"
AUTHOR = "Ashwin Nair"
REQUIRES_PYTHON = ">=3.6.0"


# What packages are required for this module to be executed?
def list_reqs(fname="requirements.txt"):
    with open(fname) as f:
        requirements = f.read().splitlines()

    required = []
    dependency_links = []
    # do not add to required lines pointing to git repositories
    EGG_MARK = "#egg="
    for line in requirements:
        if (
            line.startswith("-e git:")
            or line.startswith("-e git+")
            or line.startswith("git:")
            or line.startswith("git+")
        ):
            if EGG_MARK in line:
                package_name = line[line.find(EGG_MARK) + len(EGG_MARK) :]
                # Ignore possible subdirectories
                if "&" in package_name:
                    package_name = package_name[0 : package_name.find("&")]
                required.append(package_name)
                dependency_links.append(line)
            else:
                print("Dependency to a git repository should have the format:")
                print("git+ssh://git@github.com/xxxxx/xxxxxx#egg=package_name")
        else:
            required.append(line)

    return required, dependency_links


here = Path(__file__).cwd()

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(here / Path("README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except OSError:
    long_description = DESCRIPTION


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")
        VERSION = about["__version__"]

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, VERSION)
            sys.exit(info)


# Load the package's __version__.py module as a dictionary.
ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = ROOT_DIR / NAME
about = {}
with open(PACKAGE_DIR / "VERSION") as f:
    _version = f.read().strip()
    about["__version__"] = _version

required, dependency_links = list_reqs()

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url="https://github.com/ashnair1/COCO-Assistant/archive/v0.1.0.tar.gz",
    packages=find_packages(exclude=("tests",)),
    package_data={"coco_assistant": ["VERSION"]},
    install_requires=required,
    dependency_links=dependency_links,
    extras_require={},
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    cmdclass={
        "verify": VerifyVersionCommand,
    },
)
