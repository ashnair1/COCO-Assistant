import numpy as np
from pathlib import Path
from PIL import Image
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

    output_dir = Path(output_dir)
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True, exist_ok=True)

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
        name = Path(name)
        if name.suffix.lower() != ".png":
            name = name.stem + ".png"
        im = np.zeros((h, w), dtype=np.uint8)
        annids = cann.getAnnIds(imgIds=[imid])
        if not annids:
            # No annotations
            res = Image.fromarray(im)
            res.save(output_dir / f"{name}")
        else:
            # TODO: Handle edge case when object with higher cat id
            # overlaps one with a lower cat id - Test sample:000000143931.png
            anns = cann.loadAnns(annids)
            # areas = [i["area"] for i in anns]
            # area_ann_map = dict(zip(areas, anns))
            for ann in anns:
                bMask = cann.annToMask(ann)
                cMask = bMask * ann["category_id"]
                im = np.maximum(im, cMask)
            res = Image.fromarray(im)
            if palette:
                res.putpalette(colour_map.astype(np.uint8))
            res.save(output_dir / f"{name}")


if __name__ == "__main__":
    ann = COCO("/home/ashwin/Desktop/Projects/COCO-Assistant/data/annotations/tiny2.json")
    output_dir = "/home/ashwin/Desktop/Projects/COCO-Assistant/data/annotations/seg"
    det2seg(ann, output_dir)
