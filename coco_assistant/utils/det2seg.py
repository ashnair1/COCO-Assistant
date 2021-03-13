import os
import numpy as np
from PIL import Image, ImageDraw
from pycocotools.coco import COCO
from tqdm import tqdm


def det2seg(cann, output_dir, palette=True):
    """
    Function for converting segmentation polygons in MS-COCO
    object detection dataset to segmentation masks. The seg-
    mentation masks are stored with a colour palette that's
    randomly assigned based on class if specified. Change
    the seed if you want to change colours.

    :param cann: COCO annotation object
    :param output_dir: Directory to store segmentation masks.
    :param palette: bool -> True (use palette)/ False (no palette)
    """

    if os.path.isdir(output_dir) is False:
        os.makedirs(output_dir, exist_ok=True)

    imids = cann.getImgIds()
    cats = cann.loadCats(cann.getCatIds())

    cat_colours = {0: (0, 0, 0)}

    # Set seed for palette colour
    np.random.seed(121)

    # Create category colourmap
    for c in cats:
        cat_colours[c["id"]] = (
            np.random.randint(0, 256),
            np.random.randint(0, 256),
            np.random.randint(0, 256),
        )

    colour_map = np.array(list(cat_colours.values()))
    if colour_map.shape != (len(cats) + 1, 3):
        raise AssertionError("Incorrect shape of color map array")

    for imid in tqdm(imids):
        img = cann.loadImgs(imid)
        if len(img) > 1:
            raise AssertionError("Multiple images with same id")
        h, w = img[0]["height"], img[0]["width"]
        name = img[0]["file_name"]
        if name[-4:] != ".png":
            name = name[:-4] + ".png"
        im = np.zeros((h, w), dtype=np.uint8)
        annids = cann.getAnnIds(imgIds=[imid])
        if not annids:
            # No annotations
            res = Image.fromarray(im)
            res.save(os.path.join(output_dir, "{}".format(name)))
        else:
            anns = cann.loadAnns(annids)
            for ann in anns:
                poly = ann["segmentation"][0]
                cat = ann["category_id"]
                img = Image.new("L", (w, h))
                if len(poly) >= 6:
                    ImageDraw.Draw(img).polygon(poly, fill=cat)
                else:
                    continue
                mask = np.array(img)
                im = np.maximum(im, mask)
            res = Image.fromarray(im)
            if palette:
                res.putpalette(colour_map.astype(np.uint8))
            res.save(os.path.join(output_dir, "{}".format(name)))


if __name__ == "__main__":
    ann = COCO("/home/ashwin/Desktop/Projects/COCO-Assistant/data/annotations/tiny2.json")
    output_dir = "/home/ashwin/Desktop/Projects/COCO-Assistant/data/annotations/seg"
    det2seg(ann, output_dir)
