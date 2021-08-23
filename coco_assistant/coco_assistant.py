# -*- coding: utf-8 -*-
import ast
import json
import logging
import sys
from pathlib import Path

from pycocotools.coco import COCO
from tqdm import tqdm

from coco_assistant import utils

from . import coco_stats as stats
from . import coco_visualiser as cocovis

logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("parso.python.diff").disabled = True

"""
Expected Directory Structure

.
├── images
│   ├── train/
│   ├── val/
|   ├── test/
|
├── annotations
│   ├── train.json
│   ├── val.json
│   ├── test.json


"""


class COCO_Assistant:
    """COCO_Assistant object"""

    def __init__(self, img_dir, ann_dir):
        """

        Args:
            img_dir (str): Path to images folder.
            ann_dir (str): Path to images folder.

        """
        self.img_dir = Path(img_dir)
        self.ann_dir = Path(ann_dir)
        self.res_dir = self.ann_dir.parent / "results"

        self.dh = utils.DirectoryHandler(img_dir, ann_dir, self.res_dir)

        # TODO: Add check for confirming these folders only contain .jpg and .json respectively
        logging.debug("Number of image folders = %s", len(self.dh.names))
        logging.debug("Number of annotation files = %s", len(self.dh.names))

        self.annfiles = [COCO(self.ann_dir / (i + ".json")) for i in self.dh.names]
        self.anndict = dict(zip(self.dh.names, self.annfiles))

        self.ann_anchors = []

    def merge(self):
        """
        Merge multiple coco datasets
        """

        resann_dir = self.dh.create("merged/annotations")

        cann = {"images": [], "annotations": [], "info": None, "licenses": None, "categories": None}

        logging.debug("Merging Annotations...")

        dst_ann = resann_dir / "merged.json"

        print("Merging annotations")
        for j in tqdm(self.dh.names):
            cj = self.anndict[j].dataset

            ind = self.dh.names.index(j)
            # Check if this is the 1st annotation.
            # If it is, continue else modify current annotation
            if ind == 0:
                cann["images"] = cann["images"] + cj["images"]
                cann["annotations"] = cann["annotations"] + cj["annotations"]
                if "info" in list(cj.keys()):
                    cann["info"] = cj["info"]
                if "licenses" in list(cj.keys()):
                    cann["licenses"] = cj["licenses"]
                cann["categories"] = sorted(cj["categories"], key=lambda i: i["id"])

                last_imid = cann["images"][-1]["id"]
                last_annid = cann["annotations"][-1]["id"]

                # If last imid or last_annid is a str, convert it to int
                if isinstance(last_imid, str) or isinstance(last_annid, str):
                    logging.debug("String Ids detected. Converting to int")
                    id_dict = {}
                    # Change image id in images field
                    for i, im in enumerate(cann["images"]):
                        id_dict[im["id"]] = i
                        im["id"] = i

                    # Change annotation id & image id in annotations field
                    for i, im in enumerate(cann["annotations"]):
                        im["id"] = i
                        if isinstance(last_imid, str):
                            im["image_id"] = id_dict[im["image_id"]]

                last_imid = max(im["id"] for im in cann["images"])
                last_annid = max(ann["id"] for ann in cann["annotations"])

            else:

                id_dict = {}
                # Change image id in images field
                for i, im in enumerate(cj["images"]):
                    id_dict[im["id"]] = last_imid + i + 1
                    im["id"] = last_imid + i + 1

                # Change annotation and image ids in annotations field
                for i, ann in enumerate(cj["annotations"]):
                    ann["id"] = last_annid + i + 1
                    ann["image_id"] = id_dict[ann["image_id"]]

                # Remap categories
                cmapper = utils.CatRemapper(cann["categories"], cj["categories"])
                cann["categories"], cj["annotations"] = cmapper.remap(cj["annotations"])

                cann["images"] = cann["images"] + cj["images"]
                cann["annotations"] = cann["annotations"] + cj["annotations"]
                if "info" in list(cj.keys()):
                    cann["info"] = cj["info"]
                if "licenses" in list(cj.keys()):
                    cann["licenses"] = cj["licenses"]

                last_imid = cann["images"][-1]["id"]
                last_annid = cann["annotations"][-1]["id"]

        with open(dst_ann, "w") as aw:
            json.dump(cann, aw)

    def remove_cat(self, interactive=True, jc=None, rcats=None):

        """
        Remove categories.

        In interactive mode, you can input the json and the categories to be
        removed (as a list, see Usage for example)

        In non-interactive mode, you manually pass in json filename and
        categories to be removed. Note that jc and rcats cannot be None if run
        with interactive=False.

        Raises:
            AssertionError: if specified index exceeds number of datasets
            AssertionError: if rcats is not a list of strings
            AssertionError: if jc = rcats = None
        """

        resrm_dir = self.dh.create("removal")

        if interactive:
            print(self.dh.names)
            print("Choose directory index (1:first, 2: second ..)")

            json_choice = input()
            try:
                json_choice = int(json_choice) - 1
            except ValueError:
                sys.exit("Please specify an index")

            if json_choice > len(self.dh.names):
                raise AssertionError("Index exceeds number of datasets")
            # ann = self.annfiles[json_choice]
            name = self.dh.names[json_choice]
            json_name = name + ".json"
            ann = self.anndict[name]

            print("\nCategories present:")
            cats = [i["name"] for i in ann.cats.values()]
            print(cats)

            self.rcats = []
            print("\nEnter categories you wish to remove as a list:")
            x = input()
            x = ast.literal_eval(x)
            if isinstance(x, list) is False:
                raise AssertionError("Input must be a list of categories to be removed")
            if all(elem in cats for elem in x):
                self.rcats = x
            else:
                print("Incorrect entry.")

        else:
            if jc is None or rcats is None:
                raise AssertionError(
                    "Both json choice and rcats need to be provided in non-interactive mode"
                )
            # If passed, json_choice needs to be full path
            json_choice = Path(jc)  # Full path
            name = json_choice.stem
            json_name = json_choice.name  # abc
            ann = self.anndict[name]
            self.rcats = rcats

        print("Removing specified categories...")

        # Gives you a list of category ids of the categories to be removed
        catids_remove = ann.getCatIds(catNms=self.rcats)
        # Gives you a list of ids of annotations that contain those categories
        annids_remove = ann.getAnnIds(catIds=catids_remove)

        # Get keep category ids
        catids_keep = list(set(ann.getCatIds()) - set(catids_remove))
        # Get keep annotation ids
        annids_keep = list(set(ann.getAnnIds()) - set(annids_remove))

        with open(self.ann_dir / json_name) as it:
            x = json.load(it)

        del x["categories"]
        x["categories"] = ann.loadCats(catids_keep)
        del x["annotations"]
        x["annotations"] = ann.loadAnns(annids_keep)

        with open(resrm_dir / json_name, "w") as oa:
            json.dump(x, oa)

    def ann_stats(self, stat, arearng, show_count=False, save=False):
        """Display statistics.

        Args:
            stat (str): Type of statistic to be shown. Supports ["area", "cat"]
            arearng (list[float]): Area range list
            show_count (bool, optional): Shows category countplot if True. Defaults to False.
            save (bool, optional): Save stat plot to disk if True. Defaults to False.
        """
        if stat == "area":
            stats.pi_area_split(self.anndict, areaRng=arearng, save=save)
        elif stat == "cat":
            stats.cat_count(self.anndict, show_count=show_count, save=save)

    def anchors(self, n, fmt="rect", recompute=False):
        """
        Generate top N anchors

        !!! attention
            Experimental feature

        Args:
            n (int): Number of anchors
            fmt (str): Anchor type i.e. square or rectangular. Defaults to "rect".
            recompute (bool, optional): Recomputes the anchors if True. Defaults to False.
        """

        if recompute or not self.ann_anchors:
            print("Calculating anchors...")
            names, anns = self.anndict.keys(), self.anndict.values()
            a = [utils.generate_anchors(j, n, fmt) for j in anns]
            self.ann_anchors = dict(zip(names, a))
        else:
            print("Loading pre-computed anchors")
            print(self.ann_anchors)

    def get_segmasks(self, palette=True):
        """
        Generate segmentation masks

        Args:
            palette (bool, optional): Create masks with color palette if True. Defaults to True.
        """
        for name, ann in self.anndict.items():
            output_dir = self.res_dir / "segmasks" / name
            utils.det2seg(ann, output_dir, palette)

    def visualise(self):
        """
        Visualise annotations.
        """
        print("Choose directory index (1:first, 2: second ..):")
        print(self.dh.names)

        dir_choice = input()
        try:
            dir_choice = int(dir_choice) - 1
        except ValueError:
            sys.exit("Please specify an index")

        if dir_choice > len(self.dh.names):
            raise AssertionError("Index exceeds number of datasets")
        dir_choice = self.dh.names[dir_choice]
        ann = self.anndict[dir_choice]
        img_dir = self.img_dir / dir_choice
        cocovis.visualise_all(ann, img_dir)


if __name__ == "__main__":
    p = Path("/media/ashwin/DATA1/COCO-Assistant/")
    img_dir = p / "images"
    ann_dir = p / "annotations"

    # TODO: Create tiny dummy datasets and test these functions on them

    cas = COCO_Assistant(img_dir, ann_dir)

    # cas.merge(False)
    # cas.remove_cat()
    # cas.remove_cat(interactive=False, jc=ann_dir / "tiny2.json", rcats=['Large_Vehicle', 'Small_Vehicle'])
    # cas.ann_stats(stat="area",arearng=[10,144,512,1e5],save=False)
    # cas.ann_stats(stat="cat", arearng=None, show_count=False, save=False)
    # cas.visualise()
    # cas.get_segmasks()
    # cas.anchors(2)
