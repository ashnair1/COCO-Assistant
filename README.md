# COCO-Assistant

![CircleCI](https://img.shields.io/circleci/build/github/ashnair1/COCO-Assistant?&label=Build&logo=CircleCI)
[![Codacy Badge](https://img.shields.io/codacy/grade/5299d18c95da4991b4f3a6ae6e8a0b7a/master?label=Code%20Quality&logo=Codacy)](https://app.codacy.com/gh/ashnair1/COCO-Assistant/dashboard)
[![Code style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg)](https://github.com/psf/black)
[![PyPi License](https://img.shields.io/pypi/v/coco-assistant?branch=master&label=PyPi%20Version&logo=PyPi&logoColor=ffffff&labelColor=306998&color=FFD43B&style=flat)](https://pypi.org/project/coco-assistant/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://img.shields.io/github/license/ashnair1/COCO-Assistant?color=yellow&label=License&logo=MIT)

Helper for dealing with MS-COCO annotations.

## Overview

The MS COCO annotation format along with the pycocotools library is quite
popular among the computer vision community. Yet I for one found it difficult to
play around with the annotations. Deleting a specific category, combining
multiple mini datasets to generate a larger dataset, viewing distribution of
classes in the annotation file are things I would like to do without writing a
separate script for each scenario.

The COCO Assistant is designed (or being designed) to assist with this problem.
**Please note that currently, the Assistant can only help out with object
detection datasets**. Any contributions and/or suggestions are welcome.

## Package features

COCO-Assistant currently supports the following features:

-   Merge datasets.
-   Remove specfiic category from dataset.
-   Generate annotations statistics - distribution of object areas and category distribution.
-   Annotation visualiser for viewing the entire dataset.


## Credits

This package was created with the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.
