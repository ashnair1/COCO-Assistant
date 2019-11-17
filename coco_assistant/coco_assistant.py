import json
import logging
import os
import shutil

from pycocotools.coco import COCO

from tqdm import tqdm

from . import coco_converters as converter
from . import coco_stats as stats
from . import coco_visualiser as cocovis
from coco_assistant.utils import anchors

logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger('parso.python.diff').disabled = True

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


class COCO_Assistant():
    def __init__(self, img_dir=None, ann_dir=None):
        """
        :param img_dir (str): path to images folder.
        :param ann_dir (str): path to annotations folder.
        """
        self.img_dir = img_dir
        self.ann_dir = ann_dir
        if os.path.dirname(ann_dir) != os.path.dirname(img_dir):
            raise AssertionError('Directory not in expected format')
        self.res_dir = os.path.join(os.path.dirname(ann_dir), 'results')

        # Create Results Directory
        if os.path.exists(self.res_dir) is False:
            os.mkdir(self.res_dir)

        self.imgfolders = sorted([i for i in os.listdir(self.img_dir) if os.path.isdir(os.path.join(self.img_dir, i)) is True])
        self.jsonfiles = sorted([j for j in os.listdir(ann_dir) if j[-5:] == ".json"])
        self.names = [n[:-5] for n in self.jsonfiles]

        if self.names != self.imgfolders:
            raise AssertionError("Image dir and corresponding json file must have the same name")

        # Note: Add check for confirming these folders only contain .jpg and .json respectively
        logging.debug("Number of image folders = {}".format(len(self.imgfolders)))
        logging.debug("Number of annotation files = {}".format(len(self.jsonfiles)))

        if len(self.jsonfiles) < 1:
            raise AssertionError("Annotation files not passed")
        if len(self.imgfolders) < 1:
            raise AssertionError("Image folders not passed")

        self.annfiles = [COCO(os.path.join(ann_dir, i)) for i in self.jsonfiles]
        self.anndict = dict(zip(self.jsonfiles, self.annfiles))

        self.ann_anchors = []

    def combine(self):
        """
        Function for combining multiple coco datasets
        """

        self.resim_dir = os.path.join(self.res_dir, 'combination', 'images')
        self.resann_dir = os.path.join(self.res_dir, 'combination', 'annotations')

        # Create directories for combination results and clear the previous ones
        # The exist_ok is for dealing with combination folder
        # TODO: Can be done better
        if os.path.exists(self.resim_dir) is False:
            os.makedirs(self.resim_dir, exist_ok=True)
        else:
            shutil.rmtree(self.resim_dir)
            os.makedirs(self.resim_dir, exist_ok=True)
        if os.path.exists(self.resann_dir) is False:
            os.makedirs(self.resann_dir, exist_ok=True)
        else:
            shutil.rmtree(self.resann_dir)
            os.makedirs(self.resann_dir, exist_ok=True)

        # Combine images
        print("Merging image dirs")
        im_dirs = [os.path.join(self.img_dir, folder) for folder in self.imgfolders]
        imext = [".png", ".jpg"]

        logging.debug("Combining Images...")

        for imdir in tqdm(im_dirs):
            ims = [i for i in os.listdir(imdir) if i[-4:].lower() in imext]
            for im in ims:
                shutil.copyfile(os.path.join(imdir, im), os.path.join(self.resim_dir, im))

        # Combine annotations
        cann = {'images': [],
                'annotations': [],
                'info': None,
                'licenses': None,
                'categories': None}

        logging.debug("Combining Annotations...")

        dst_ann = os.path.join(self.resann_dir, 'combined.json')

        print("Merging annotations")
        for j in tqdm(self.jsonfiles):
            with open(os.path.join(self.ann_dir, j)) as a:
                c = json.load(a)

            ind = self.jsonfiles.index(j)
            cocofile = self.annfiles[ind]
            # Check if this is the 1st annotation.
            # If it is, continue else modify current annotation
            if ind == 0:
                cann['images'] = cann['images'] + c['images']
                cann['annotations'] = cann['annotations'] + c['annotations']
                if 'info' in list(c.keys()):
                    cann['info'] = c['info']
                if 'licenses' in list(c.keys()):
                    cann['licenses'] = c['licenses']
                cann['categories'] = c['categories']

                last_imid = cann['images'][-1]['id']
                last_annid = cann['annotations'][-1]['id']

                logging.debug("String Ids detected. Converting to int")

                # If last imid or last_annid is a str, convert it to int
                if isinstance(last_imid, str):
                    id_dict = {}
                    # Change image id in images field
                    for i, im in enumerate(cann['images']):
                       id_dict[im['id']] = i
                       im['id'] = i

                if isinstance(last_annid, str):
                    # Change annotation id & image id in annotations field
                    for i, im in enumerate(cann['annotations']):
                        im['id'] = i
                        if isinstance(last_imid, str):
                            im['image_id'] = id_dict[im['image_id']]

                last_imid = cann['images'][-1]['id']
                last_annid = cann['annotations'][-1]['id']

            else:
                new_imids = [(last_imid + i + 1) for i in sorted(list(cocofile.imgs.keys()))]
                new_annids = [(last_annid + i + 1) for i in sorted(list(cocofile.anns.keys()))]

                def modify_ids(jf, imids, annids):
                    id_dict = {}
                    for img, newimid in zip(jf['images'], imids):
                        id_dict[img['id']] = newimid
                        img['id'] = newimid
                    for ann, newannid in zip(jf['annotations'], annids):
                        ann['id'] = newannid
                        ann['image_id'] = id_dict[ann['image_id']]
                    return jf

                c = modify_ids(c, new_imids, new_annids)
                cann['images'] = cann['images'] + c['images']
                cann['annotations'] = cann['annotations'] + c['annotations']
                if 'info' in list(c.keys()):
                    cann['info'] = c['info']
                if 'licenses' in list(c.keys()):
                    cann['licenses'] = c['licenses']
                cann['categories'] = c['categories']

                last_imid = cann['images'][-1]['id']
                last_annid = cann['annotations'][-1]['id']

        with open(dst_ann, 'w') as aw:
            json.dump(cann, aw)

    def remove_cat(self, jc=None, rcats=None):
        """
        Function for removing certain categories
        """

        self.resrm_dir = os.path.join(self.res_dir, 'removal')
        if os.path.exists(self.resrm_dir) is False:
            os.makedirs(self.resrm_dir, exist_ok=True)
        else:
            shutil.rmtree(self.resrm_dir)
            os.makedirs(self.resrm_dir, exist_ok=True)

        if jc is None or rcats is None:
            ###########################################################
            print(self.jsonfiles)
            print("Who needs a cat removal?")
            self.jc = input()
            if self.jc.lower() not in [item.lower() for item in self.jsonfiles]:
                raise AssertionError("Choice not in json file list")
            ind = self.jsonfiles.index(self.jc.lower())
            ann = self.annfiles[ind]

            print("\nCategories present:")
            cats = [i['name'] for i in ann.cats.values()]
            print(cats)

            self.rcats = []
            print("\nEnter categories you wish to remove:")
            while True:
                x = input()
                if x.lower() in [cat.lower() for cat in cats]:
                    catind = [cat.lower() for cat in cats].index(x.lower())
                    self.rcats.append(cats[catind])
                    print(self.rcats)
                    print("Press n if you're done entering categories, else continue")
                elif x == "n":
                    break
                else:
                    print("Incorrect Entry. Enter either the category to be added or press 'n' to quit.")
            ###############################################################

        else:
            self.jc = jc
            ind = self.jsonfiles.index(self.jc.lower())
            ann = self.annfiles[ind]
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

        with open(os.path.join(self.ann_dir, self.jc)) as it:
            x = json.load(it)

        x['categories'] = [i for i in x['categories'] if i not in cats]
        x['annotations'] = [i for i in x['annotations'] if i not in anns]

        with open(os.path.join(self.resrm_dir, self.jc), 'w') as oa:
            json.dump(x, oa)

    def ann_stats(self, stat, arearng, show_count=False, save=False):
        """
        Function for displaying statistics.
        """
        if stat == "area":
            stats.pi_area_split(self.annfiles, self.names, areaRng=arearng, save=save)
        elif stat == "cat":
            stats.cat_count(self.annfiles, self.names, show_count=show_count, save=save)

    def anchors(self, num, fmt=None, recompute=False):
        """
        Function for generating top anchors
        """
        if recompute or not self.ann_anchors:
            print("Calculating anchors...")
            a = [anchors.generate_anchors(j, num, fmt) for j in self.annfiles]
            self.ann_anchors = dict(zip(self.names, a))
        else:
            print("Loading pre-computed anchors")
            print(self.ann_anchors)

    def converter(self, to="TFRecord"):
        """
        Function for converting annotations to other formats
        """
        print("Choose directory:")
        print(self.imgfolders)

        dir_choice = input()

        if dir_choice.lower() not in [item.lower() for item in self.imgfolders]:
            raise AssertionError("Choice not in images folder")
        ind = self.imgfolders.index(dir_choice.lower())
        ann = self.annfiles[ind]
        img_dir = os.path.join(self.img_dir, dir_choice)

        converter.convert(ann, img_dir, _format=to)

    def visualise(self):
        """
        Function for visualising annotations.
        """
        print("Choose directory:")
        print(self.imgfolders)

        dir_choice = input()

        if dir_choice.lower() not in [item.lower() for item in self.imgfolders]:
            raise AssertionError("Choice not in images folder")
        ind = self.imgfolders.index(dir_choice.lower())
        ann = self.annfiles[ind]
        img_dir = os.path.join(self.img_dir, dir_choice)
        cocovis.visualise_all(ann, img_dir)


if __name__ == "__main__":
    p = "/home/ashwin/Desktop/Projects/COCO-Assistant"
    img_dir = os.path.join(p, 'images')
    ann_dir = os.path.join(p, 'annotations')

    # TODO: Create tiny dummy datasets and test these functions on them

    cas = COCO_Assistant(img_dir, ann_dir)

    #cas.combine()
    #cas.remove_cat()
    #cas.ann_stats(stat="area",arearng=[10,144,512,1e5],save=False)
    #cas.ann_stats(stat="cat", show_count=False, save=False)
    #cas.visualise()
    #cas.anchors(2)
