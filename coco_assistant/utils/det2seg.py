import os
from copy import deepcopy
import numpy as np
from PIL import Image, ImageDraw
from pycocotools.coco import COCO
from tqdm import tqdm


def det2seg(cann, output_dir):
    """
    Function for converting segmentation polygons in MS-COCO
    object detection dataset to segmentation masks. The seg-
    mentation masks are stored with a colour pallete that's 
    randomly assigned based on class. Change the seed if you
    want to change colours.

    :param cann: COCO annotation object
    :param output_dir: Directory to store segmentation masks.
    """
    
    if os.path.isdir(output_dir) is False:
        os.makedirs(output_dir, exist_ok=True)

    imids = cann.getImgIds()
    cats = cann.loadCats(cann.getCatIds())

    cat_colours = {0: (0,0,0)}
    
    # Set seed for palette colour
    np.random.seed(121)

    # Create category colourmap
    for i, c in enumerate(cats):
        cat_colours[c['id']] = (np.random.randint(0,256), np.random.randint(0,256), np.random.randint(0,256))

    colour_map = np.array(list(cat_colours.values()))
    if colour_map.shape != (len(cats) + 1, 3):
        raise AssertionError("Incorrect shape of color map array")

    for imid in tqdm(imids):
        img = cann.loadImgs(imid)
        if len(img) > 1:
            raise AssertionError("Multiple images with same id")
        H, W = img[0]['height'], img[0]['width']
        name = img[0]['file_name']
        im = np.zeros((H,W), dtype=np.uint8)
        annids = cann.getAnnIds(imgIds=[imid])
        if not annids:
            # No annotations
            res = Image.fromarray(im)
            res.save(os.path.join(output_dir, '{}'.format(name)))
            return
        else:
            anns = cann.loadAnns(annids)
            for ann in anns:
                poly = ann['segmentation'][0]
                cat = ann['category_id']
                img = Image.new('L', (H, W))
                if len(poly) >= 6:
                    ImageDraw.Draw(img).polygon(poly, fill=cat)
                else:
                    continue
                mask = np.array(img)
                im = np.maximum(im, mask)
            res = Image.fromarray(im)
            res.putpalette(colour_map.astype(np.uint8))
            res.save(os.path.join(output_dir, '{}'.format(name)))

if __name__ == "__main__":
    ann = COCO('./data/annotations/coco.json')
    output_dir = "./data/annotations/seg"
    det2seg(ann, output_dir)