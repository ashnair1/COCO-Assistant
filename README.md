# COCO-Assistant

Helper for dealing with MS-COCO annotations

Functions:

1. Maker

Assuming you have multiple directories containing a folder of images and a COCO style annotation file for each set
"""
Example:
.
├── IMAGE_SET1
│   ├── coco.json
│   ├── images
├── IMAGE_SET2
│   ├── coco.json
│   ├── images
""" 

The coco_maker functionality will combine the images and annotations to generate an image folder containing all images and an annotation file corresponding to it. Note however, that the individiual annotations needs to have different annotation ids so that they can be seamlesslt merged. In the future, functionality will be added to check annotation ids automatically.

2. Remover

Suppose you wanted to remove certain categories from the annotation file. The coco_remover does just that.
