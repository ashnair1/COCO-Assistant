import ast
import json
import logging
import sys
import shutil

from pathlib import Path
from pycocotools.coco import COCO
from tqdm import tqdm

from . import coco_stats as stats
from . import coco_visualiser as cocovis
from coco_assistant import utils

logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("parso.python.diff").disabled = True

"""
Expected Directory Structure

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


"""


class COCO_Assistant:
    def __init__(self, img_dir, ann_dir):
        """
        :param img_dir (str): path to images folder.
        :param ann_dir (str): path to annotations folder.
        """
        self.img_dir = Path(img_dir)
        self.ann_dir = Path(ann_dir)

        # Parent dir should be the same
        if self.ann_dir.parents[0] != self.img_dir.parents[0]:
            raise AssertionError("Directory not in expected format")
        self.res_dir = self.ann_dir.parents[0] / "results"

        # Create Results Directory
        if not self.res_dir.exists():
            self.res_dir.mkdir()

        self.imgfolders = sorted(
            [i for i in self.img_dir.iterdir() if i.is_dir() and not i.name.startswith(".")]
        )
        imnames = [n.stem for n in self.imgfolders]

        self.jsonfiles = sorted([j for j in self.ann_dir.iterdir() if j.suffix == ".json"])
        jnames = [n.stem for n in self.jsonfiles]

        if imnames != jnames:
            raise AssertionError("Image dir and corresponding json file must have the same name")

        self.names = imnames

        # TODO: Add check for confirming these folders only contain .jpg and .json respectively
        logging.debug("Number of image folders = %s", len(self.imgfolders))
        logging.debug("Number of annotation files = %s", len(self.jsonfiles))

        if not self.jsonfiles:
            raise AssertionError("Annotation files not passed")
        if not self.imgfolders:
            raise AssertionError("Image folders not passed")

        self.annfiles = [COCO(i) for i in self.jsonfiles]
        self.anndict = dict(zip(self.jsonfiles, self.annfiles))

        self.ann_anchors = []

    def merge(self, merge_images=True):
        """
        Function for merging multiple coco datasets
        """
        self.resim_dir = self.res_dir / "merged" / "images"
        self.resann_dir = self.res_dir / "merged" / "annotations"

        utils.make_clean(self.resim_dir)
        utils.make_clean(self.resann_dir)

        if merge_images:
            print("Merging image dirs")
            im_dirs = self.imgfolders
            imext = [".png", ".jpg", ".jpeg"]

            logging.debug("Merging Image Dirs...")

            for imdir in tqdm(im_dirs):
                ims = [i for i in imdir.iterdir() if i.suffix.lower() in imext]
                for im in ims:
                    shutil.copyfile(im, self.resim_dir / im.name)

        else:
            logging.debug("Not merging Image Dirs...")

        cann = {"images": [], "annotations": [], "info": None, "licenses": None, "categories": None}

        logging.debug("Merging Annotations...")

        dst_ann = self.resann_dir / "merged.json"

        print("Merging annotations")
        for j in tqdm(self.jsonfiles):
            with open(j) as a:
                cj = json.load(a)

            ind = self.jsonfiles.index(j)
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

                last_imid = cann["images"][-1]["id"]
                last_annid = cann["annotations"][-1]["id"]

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
        Function for removing certain categories.
        In interactive mode, you can input the json and the categories
        to be removed (as a list, see README for example)
        In non-interactive mode, you manually pass in json filename and
        categories to be removed. Note that jc and
        rcats cannot be None if run with interactive=False.

        :param interactive: Run category removal in interactive mode
        :param jc: Json choice
        :param rcats: Categories to be removed
        """
        resrm_dir = self.res_dir / "removal"
        utils.make_clean(resrm_dir)
        # jnames == imnames -> No extension

        if interactive:
            print(self.names)
            print("Choose directory index (1:first, 2: second ..)")

            json_choice = input()
            try:
                json_choice = int(json_choice) - 1
            except ValueError:
                sys.exit("Please specify an index")

            if json_choice > len(self.names):
                raise AssertionError("Index exceeds number of datasets")
            ann = self.annfiles[json_choice]
            json_name = self.jsonfiles[json_choice].name
            self.jc = json_name  # hack

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
            json_name = json_choice.name  # abc.json
            self.jc = json_name  # hack
            ann = self.anndict[Path(json_choice)]
            self.rcats = rcats

        print("Removing specified categories...")

        # Gives you a list of category ids of the categories to be removed
        catids_remove = ann.getCatIds(catNms=self.rcats)
        # Gives you a list of ids of annotations that contain those categories
        annids_remove = ann.getAnnIds(catIds=catids_remove)

        # Remove from category list
        cats = ann.loadCats(catids_remove)
        # Remove from annotation list
        anns = ann.loadAnns(annids_remove)
        with open(self.ann_dir / json_name) as it:
            x = json.load(it)

        x["categories"] = [i for i in x["categories"] if i not in cats]
        x["annotations"] = [i for i in x["annotations"] if i not in anns]

        with open(resrm_dir / json_name, "w") as oa:
            json.dump(x, oa)

    def ann_stats(self, stat, arearng, show_count=False, save=False):
        """
        Function for displaying statistics.
        """
        if stat == "area":
            stats.pi_area_split(self.annfiles, self.names, areaRng=arearng, save=save)
        elif stat == "cat":
            stats.cat_count(self.annfiles, self.names, show_count=show_count, save=save)

    def anchors(self, n, fmt=None, recompute=False):
        """
        Function for generating top 'n' anchors

        :param n: Number of anchors
        :param fmt: Format of anchors ['square', None]
        :param recompute: Rerun k-means and recompute anchors
        """
        if recompute or not self.ann_anchors:
            print("Calculating anchors...")
            a = [utils.generate_anchors(j, n, fmt) for j in self.annfiles]
            self.ann_anchors = dict(zip(self.names, a))
        else:
            print("Loading pre-computed anchors")
            print(self.ann_anchors)

    def get_segmasks(self, palette=True):
        """
        Function for generating segmentation masks.
        """
        for ann, name in zip(self.annfiles, self.names):
            output_dir = self.res_dir / "segmasks" / name
            utils.det2seg(ann, output_dir, palette)

    def visualise(self):
        """
        Function for visualising annotations.
        """
        print("Choose directory index (1:first, 2: second ..):")
        print([s.stem for s in self.imgfolders])

        dir_choice = input()
        try:
            dir_choice = int(dir_choice) - 1
        except ValueError:
            sys.exit("Please specify an index")

        if dir_choice > len(self.imgfolders):
            raise AssertionError("Index exceeds number of datasets")
        ann = self.annfiles[dir_choice]
        img_dir = self.imgfolders[dir_choice]
        cocovis.visualise_all(ann, img_dir)


if __name__ == "__main__":
    p = Path("/home/ashwin/Desktop/Projects/COCO-Assistant/data/tiny_coco/")
    img_dir = p / "images"
    ann_dir = p / "annotations"

    # TODO: Create tiny dummy datasets and test these functions on them

    cas = COCO_Assistant(img_dir, ann_dir)

    # cas.merge(False)
    # cas.remove_cat()
    # cas.ann_stats(stat="area",arearng=[10,144,512,1e5],save=False)
    # cas.ann_stats(stat="cat", arearng=None, show_count=False, save=False)
    # cas.visualise()
    # cas.get_segmasks()
    # cas.anchors(2)
