<h1> Usage </h1>

## Requirements

Your data directory should look as follows:

```markdown
Example:
.
├── images
│   ├── train
│   ├── val
|   ├── test
|   
├── annotations
│   ├── train.json
│   ├── val.json
│   ├── test.json

```

Usage is similar to how you would use `pycocotools`.

```markdown
from coco_assistant import COCO_Assistant

# Specify image and annotation directories
img_dir = os.path.join(os.getcwd(), 'images')
ann_dir = os.path.join(os.getcwd(), 'annotations')

# Create COCO_Assistant object
cas = COCO_Assistant(img_dir, ann_dir)
```

## Package features

### 1. Merge datasets

The `merge` function allows you to merge multiple datasets.

```markdown
>>> cas = COCO_Assistant(img_dir, ann_dir)                                                                                                                                                              
loading annotations into memory...
Done (t=0.09s)
creating index...
index created!
loading annotations into memory...
Done (t=0.06s)
creating index...
index created!

>>> cas.merge(merge_images=True)                                                                                                                                                                                       
Merging image dirs
100%|█████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 18.33it/s]
Merging annotations
100%|█████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 14.72it/s]

```

The merged dataset (images and annotation) can be found in `./results/merged`

### 2. Remove categories

Removes a specific category from an annotation file.

```markdown
>>> cas = COCO_Assistant(img_dir, ann_dir)                                                                                                                                                              
loading annotations into memory...
Done (t=0.09s)
creating index...
index created!
loading annotations into memory...
Done (t=0.06s)
creating index...
index created!
 
# In interactive mode
>>> cas.remove_cat(interactive=True)
['tiny.json', 'tiny2.json']
Choose directory index (1:first, 2: second ..):
1

Categories present:
['building', 'vehicles']

Enter categories you wish to remove as a list:
['building']
Removing specified categories...

# In non-interactive mode
>>> cas.remove_cat(interactive=False, jc="tiny.json", rcats=['building'])
Removing specified categories...
```

The modified annotation can be found in `./results/removal`

### 3. Generate annotation statistics

1.  Generate countplot of instances per category that occur in the annotation files. 
    ```python
    >>> cas.ann_stats(stat="area",arearng=[10,144,512,1e5],save=False)
    ```

2.  Generate pie-chart that shows distribution of objects according to their size (as specified in areaRng). 
    ```python
    >>> cas.ann_stats(stat="cat", arearng=None, show_count=False, save=False)
    ```

### 4. Visualise annotations

Couldn't `pycocotools` visualise annotations (via [showAnns](https://github.com/cocodataset/cocoapi/blob/636becdc73d54283b3aac6d4ec363cffbb6f9b20/PythonAPI/pycocotools/coco.py#L233)) as well? Sure it could, but I required a way to freely view all the annotations of a particular dataset so here we are.

```console
>>> cas.visualise()
Choose directory index (1:first, 2: second ..):
['tiny', 'tiny2']
1
```

![](assets/visualiser.gif)

### 5. Generate segmentation masks

The `cas.get_segmasks()` function allows you to create segmentation masks from your MS COCO object detection datasets. **Please ensure your category ids start from 1.** Similar to the Pascal VOC dataset, the mask values are their classes and a colour palette is applied (optional) to enable visualisation. The generated masks are stored in the `./results` folder. Samples are shown below.

|              | Detection                                                                      | Segmentation                                                                                  |
| ------------ | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| **SpaceNet** | <img src="../assets/SpaceNet.png" alt="SpaceNet" title="SpaceNet" width=310 /> | <img src="../assets/SpaceNet_mask.png" alt="SpaceNet_mask" title="SpaceNet_mask" width=310 /> |
| **iSAID**    | <img src="../assets/iSAID.png" alt="iSAID" title="iSAID" width=310 />          | <img src="../assets/iSAID_mask.png" alt="iSAID_mask" title="iSAID_mask" width=310 />          |
