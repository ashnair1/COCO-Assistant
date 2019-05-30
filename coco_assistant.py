import json
from pycocotools.coco import COCO
import os
import shutil
from shutil import copyfile
import random
import argparse


class COCO_Assistant():

	def __init__(self,work_dir,out_dir):
		self.in_dir = work_dir
		self.out_dir = out_dir

	def coco_maker(self):
		dirs = [i for i in os.listdir(self.in_dir) if os.path.isdir(i) and i[0] != "." and i != "images"]

		dirs.sort()
		random.seed(121)

		#random.shuffle(dirs)

		dst = os.path.join(self.out_dir,'images')
		if os.path.exists(dst) is False:
		    os.mkdir(dst)
		    
		imext = [".png", ".jpg"]
		for d in dirs:
		    src = os.path.join(self.in_dir,d,'images')
		    imgs = [i for i in os.listdir(src) if i[-4:].lower() in imext]
		    #random.shuffle(imgs)
		    for img in imgs:
		        copyfile(os.path.join(src,img), os.path.join(dst,img))


		p = {'images':[],
		    'annotations': [],
		    'info': None,
		    'licenses': None,
		    'categories':None}


		for d in dirs:
		    ann = os.path.join(self.in_dir,d,'coco.json')
		    with open(ann) as a:
		        c = json.load(a)
		    
		    p['images'] = p['images'] + c['images']
		    p['annotations'] = p['annotations'] + c['annotations']
		    p['info'] = c['info']
		    p['licenses'] = c['licenses']
		    p['categories'] = c['categories']

		with open(os.path.join(self.out_dir,'instances_train.json'),'w') as aw:
		    json.dump(p,aw)



	def coco_remover(self):
		annFile 	= os.path.join(self.in_dir,'instances_train_mod.json')
		outAnnFile 	= os.path.join(self.out_dir,'instances_train_fil.json')
		
		coco = COCO(annFile)

		remove_cats = None#['Sat Dish']

		# Gives you a list of category ids of the categories to be removed
		catids_remove = coco.getCatIds(catNms=remove_cats) 
		# Gives you a list of ids of annotations that contain those categories
		annids_remove = coco.getAnnIds(catIds=catids_remove) 

		# Remove from category list
		cats = coco.loadCats(catids_remove)
		# Remove from annotation list
		anns = coco.loadAnns(annids_remove)

		with open(annFile) as it:
		    x = json.load(it)

		x['categories'] = [i for i in x['categories'] if i not in cats]
		x['annotations'] = [i for i in x['annotations'] if i not in anns]


		with open(outAnnFile,'w') as oa:
		    json.dump(x,oa)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', help='the directory where the stuff is')
    parser.add_argument('--out_dir', help='the directory to store results')
    parser.add_argument('--make',action='store_true',help='create coco data')
    parser.add_argument('--remove',action='store_true',help='remove certain categories from the annotations')
    args = parser.parse_args()

    return args



def main():
	
	args = parse_args()

	assert args.make != args.remove

	cas = COCO_Assistant(args.work_dir, args.out_dir)

	if args.make is True:
		cas.coco_maker()

	if args.remove is True:
		cas.coco_remover()


if __name__ == "__main__":
	main()
