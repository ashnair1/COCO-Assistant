# COCO-Assistant <img src="images/coco.png" height="50">

Helper for dealing with MS-COCO annotations. 

## Overview
The MS COCO annotation format along with the pycocotools library is quite popular among the computer vision community. Yet I for one found it difficult to play around with the annotations. Deleting a specific category, combining multiple mini datasets to generate a larger dataset, viewing distribution of classes in the annotation file are things I would like to do without writing a separate script for each. The COCO Assistant is designed (or being designed) to assist with this exact problem.

## Functions:

#### Maker

Assuming you have multiple directories containing a folder of images and a COCO style annotation file for each set

```
Example:
.
├── IMAGE_SET1
│   ├── coco.json
│   ├── images
├── IMAGE_SET2
│   ├── coco.json
│   ├── images
``` 

The `coco_maker` functionality will combine the images and annotations to generate an image folder containing all images and an annotation file corresponding to it. Note however, that the individiual annotations needs to have different annotation ids so that they can be seamlesslt merged. In the future, functionality will be added to check annotation ids automatically.

#### Remover

Suppose you wanted to remove certain categories from the annotation file. The `coco_remover` does just that.

#### Cat Counter

Counts and displays a countplot of the categories.

#### COCO to YOLO Converter

Converts COCO annotations to YOLO format (modified version of ultralytics's [original repo](https://github.com/ultralytics/COCO2YOLO))
