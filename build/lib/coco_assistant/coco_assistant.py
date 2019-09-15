import os
import shutil

import json
from pycocotools.coco import COCO
import logging
import pdb

from . import coco_stats as stats
from . import coco_visualiser as cocovis

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
		:param jsonfiles (list): list of annotation files
		:param folders (list): list of img folders
		"""

		self.img_dir = img_dir
		self.ann_dir = ann_dir
		assert os.path.dirname(ann_dir) == os.path.dirname(img_dir)
		self.res_dir = os.path.join(os.path.dirname(ann_dir), 'results')

		# Create Results Directory
		if os.path.exists(self.res_dir) is False:
			os.mkdir(self.res_dir)

		self.imgfolders = [i for i in os.listdir(self.img_dir) if os.path.isdir(os.path.join(self.img_dir,i)) is True]
		self.jsonfiles = sorted([j for j in os.listdir(ann_dir) if j[-5:] == ".json"])
		self.names = [n[:-5] for n in self.jsonfiles]

		# Note: Add check for confirming these folders only contain .jpg and .json respectively

		logging.debug("Number of image folders = {}".format(len(self.imgfolders)))
		logging.debug("Number of annotation files = {}".format(len(self.jsonfiles)))

		assert len(self.jsonfiles) >= 1, "Annotation files not passed"
		assert len(self.imgfolders) >= 1, "Image folders not passed"

		self.annfiles = [COCO(os.path.join(ann_dir, i)) for i in self.jsonfiles]

		self.anndict = dict(zip(self.jsonfiles, self.annfiles))

		#print(self.anndict.keys())


	def combine(self):
		"""
		Function for combining multiple coco datasets
		"""

		resim_dir = os.path.join(self.res_dir, 'combination', 'images')
		resann_dir = os.path.join(self.res_dir, 'combination', 'annotations')

		# Create directories for combination results and clear the previous ones
		# The exist_ok is for dealing with combination folder
		# TODO: Can be done better
		if os.path.exists(resim_dir) is False:
			os.makedirs(resim_dir, exist_ok=True)
		else:
			shutil.rmtree(resim_dir) 
			os.makedirs(resim_dir, exist_ok=True)
		if os.path.exists(resann_dir) is False:
			os.makedirs(resann_dir, exist_ok=True)
		else:
			shutil.rmtree(resann_dir) 
			os.makedirs(resann_dir, exist_ok=True)


		# Combine images
		im_dirs = [os.path.join(self.img_dir, folder) for folder in self.imgfolders]
		imext = [".png", ".jpg"]

		logging.debug("Combining Images...")

		for imdir in im_dirs:
			ims = [i for i in os.listdir(imdir) if i[-4:].lower() in imext]
			for im in ims:
				shutil.copyfile(os.path.join(imdir, im), os.path.join(resim_dir, im))


		# Combine annotations
		cann = {'images': [],
		        'annotations': [],
		        'info': None,
		        'licenses': None,
		        'categories': None}

		logging.debug("Combining Annotations...")

		dst_ann = os.path.join(resann_dir, 'combined.json')


		for j in self.jsonfiles:
			#c = COCO(os.path.join(ann_dir, each_ann))
			with open(os.path.join(self.ann_dir, j)) as a:
				c = json.load(a)

			cann['images'] = cann['images'] + c['images']
			cann['annotations'] = cann['annotations'] + c['annotations']
			if 'info' in list(c.keys()):
				cann['info'] = c['info']
			if 'licenses' in list(c.keys()):
				cann['licenses'] = c['licenses']
			cann['categories'] = c['categories']

		with open(dst_ann, 'w') as aw:
			json.dump(cann, aw)


	def remove_cat(self):
		"""
		Function for removing certain categories
		"""

		resrm_dir = os.path.join(self.res_dir, 'removal')
		if os.path.exists(resrm_dir) is False:
			os.makedirs(resrm_dir, exist_ok=True)
		else:
			shutil.rmtree(resrm_dir) 
			os.makedirs(resrm_dir, exist_ok=True)

		print(self.jsonfiles)
		print("Who needs a cat removal?")
		jc = input()
		assert jc.lower() in [item.lower() for item in self.jsonfiles], "Choice not in json file list"
		#ann = self.anndict[jc]
		ind = self.jsonfiles.index(jc.lower())
		ann = self.annfiles[ind]

		print("\nCategories present:")
		cats = [i['name'] for i in ann.cats.values()]
		print(cats)

		rcats = []
		print("\nEnter categories you wish to remove:")
		while True:
			x = input()
			if x.lower() in [cat.lower() for cat in cats]:
				catind = [cat.lower() for cat in cats].index(x.lower())
				rcats.append(cats[catind])
				print(rcats)
				print("Press n if you're done entering categories, else continue")
			elif x == "n":
				break
			else:
				print("Incorrect Entry. Enter either the category to be added or press 'n' to quit.")
		print("Removing specified categories...")

		# Gives you a list of category ids of the categories to be removed
		catids_remove = ann.getCatIds(catNms=rcats)
		# Gives you a list of ids of annotations that contain those categories
		annids_remove = ann.getAnnIds(catIds=catids_remove)

		# Remove from category list
		cats = ann.loadCats(catids_remove)
		# Remove from annotation list
		anns = ann.loadAnns(annids_remove)

		with open(os.path.join(self.ann_dir,jc)) as it:
			x = json.load(it)

		x['categories'] = [i for i in x['categories'] if i not in cats]
		x['annotations'] = [i for i in x['annotations'] if i not in anns]

		with open(os.path.join(resrm_dir,jc), 'w') as oa:
			json.dump(x, oa)


	def ann_stats(self, stat, show_count=False, arearng=[0,32,96,1e5], save=False):
		"""
		Function for displaying statistics
		"""
		if stat == "area":
			stats.pi_area_split(self.annfiles, self.names, areaRng=arearng, save=save)
			#stats.pi_area_split_single(self.annfiles[0], kwargs['arearng'])
		elif stat == "cat":
			stats.cat_count(self.annfiles, self.names, show_count=show_count, save=save)


	def visualise(self):
		"""
		Function for visualising annotations
		"""
		
		print("Choose directory:")
		print(self.imgfolders)
		
		dir_choice = input()

		assert dir_choice.lower() in [item.lower() for item in self.imgfolders], "Choice not in images folder"
		#ann = self.anndict[dir_choice + ".json"]
		ind = self.imgfolders.index(dir_choice.lower())
		ann = self.annfiles[ind]
		img_dir = os.path.join(self.img_dir,dir_choice)
		cocovis.visualise_all(ann, img_dir)


if __name__ == "__main__":

	img_dir = os.path.join(os.getcwd(), 'images')
	ann_dir = os.path.join(os.getcwd(), 'annotations')

	# TODO: Create tiny dummy datasets and test these functions on them

	cas = COCO_Assistant(img_dir,ann_dir)

	#cas.combine()
	#cas.remove_cat()
	cas.ann_stats(stat="area",arearng=[10,144,512,1e5],save=False)
	cas.ann_stats(stat="cat", show_count=False, save=False)
	#cas.visualise()
