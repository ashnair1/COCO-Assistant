import os
import shutil
import random
import argparse

import numpy as np
import matplotlib.pyplot as plt
import json
from pycocotools.coco import COCO
from tqdm import tqdm

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
		        shutil.copyfile(os.path.join(src,img), os.path.join(dst,img))


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
		
	def cat_count(self,coco_ann):

		"""
		Generate a dictionairy of categories and their counts.

		Returns the dict, list of cats and list of counts
		"""

		catcount = {}
		for catid, occurrences in coco_ann.catToImgs.items():
			catcount[coco_ann.cats[catid]['name']] = len(occurrences)

		labels = [ck for ck in catcount.keys()]
		values = [cv for cv in catcount.values()]

		return catcount, labels, values

	def disp_cat_count(self, annotations=None, name="test", bar="h", show=False):
	    
	    _, labels, values = self.cat_count(annotations)

	    indexes = np.arange(len(labels))
	    width = 0.5

	    if bar == "v":
	        fig_size = (20,10)
	    elif bar == "h":
	        fig_size = (8,10)

	    plt.figure(figsize=fig_size)

	    if bar == "h":
	        plt.barh(indexes, values, width,align="edge")
	        plt.yticks(indexes+width/2,labels)
	        plt.ylabel('Classes')
	        plt.xlabel('Count')
	    elif bar == "v":
	        plt.bar(indexes, values, width,align="edge")
	        plt.xticks(indexes, labels,rotation='vertical')
	        plt.xlabel('Classes')
	        plt.ylabel('Count')


	    plt.tight_layout()
	    plt.title('Class Distribution')


	    if bar == "h":
	        for i, v in enumerate(values):
	            plt.text(v + 3, i, str(v), color='blue', fontweight='bold')
	    elif bar == "v":
	        for i, v in enumerate(values):
	            plt.text(i,v + 5, str(v), color='blue', fontsize=0.6*fig_size[0],fontweight='bold')

	    out_dir = os.path.join(os.getcwd(),'plots')
	    if os.path.exists(out_dir) is False:
		    os.mkdir(out_dir)


	    plt.savefig(os.path.join(out_dir,name + ".jpg"))
	    if show is True:
	    	plt.show()


	def split(self, x, train=0.9, test=0.1, validate=0.0, shuffle=False):  # split training data
	    n = len(x)
	    v = np.arange(n)
	    if shuffle:
	        np.random.shuffle(v)

	    i = round(n * train)  # train
	    j = round(n * test) + i  # test
	    k = round(n * validate) + j  # validate
	    return v[:i], v[i:j], v[j:k]


	# Convert COCO JSON file into YOLO format labels -------------------------------
	def coco2yolo(self, name, file):
		# Import json
	    with open(file) as f:
	        data = json.load(f)

	    # Create folders
	    path = 'yolo_annotations'
	    if os.path.exists(path):
	        shutil.rmtree(path)  # delete output folder
	    os.makedirs(path)  # make new output folder
	    os.makedirs(path + os.sep + 'labels')  # make new labels folder

	    # Write images and shapes
	    name = path + os.sep + name
	    file_id, file_name, width, height = [], [], [], []
	    for i, x in enumerate(tqdm(data['images'], desc='Files and Shapes')):
	        file_id.append(x['id'])
	        file_name.append('IMG_' + x['file_name'].split('IMG_')[-1])
	        width.append(x['width'])
	        height.append(x['height'])

	        # filename
	        with open(name + '.txt', 'a') as file:
	            file.write('%s\n' % file_name[i])

	        # shapes
	        with open(name + '.shapes', 'a') as file:
	            file.write('%g, %g\n' % (x['width'], x['height']))

	    # Write *.names file
	    for x in tqdm(data['categories'], desc='Names'):
	        with open(name + '.names', 'a') as file:
	            file.write('%s\n' % x['name'])

	    # Write labels file
	    for x in tqdm(data['annotations'], desc='Annotations'):
	        i = file_id.index(x['image_id'])  # image index
	        image_name = file_name[i]
	        extension = image_name.split('.')[-1]
	        label_name = image_name.replace(extension, 'txt')

	        # The COCO bounding box format is [top left x, top left y, width, height]
	        box = np.array(x['bbox'],dtype=np.float64)
	        box[:2] += box[2:] / 2  # xy top-left corner to center
	        box[[0, 2]] /= width[i]  # normalize x
	        box[[1, 3]] /= height[i]  # normalize y

	        # 'out/labels/' + label_name, 'a'
	        with open(os.path.join(path,'labels',label_name), 'a') as file:
	            file.write('%g %.6f %.6f %.6f %.6f\n' % (x['category_id'] - 1, *box))

	    # Split data into train, test, and validate files
	    file_name = sorted(file_name)
	    i, j, k = self.split(file_name, train=0.9, test=0.1, validate=0.0, shuffle=False)
	    datasets = {'train': i, 'test': j, 'val': k}
	    for key, item in datasets.items():
	        with open(name + '_' + key + '.txt', 'a') as file:
	            for i in item:
	                file.write('%s\n' % file_name[i])

	    print('Done. Output saved to %s' % (os.getcwd() + os.sep + path))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', help='the directory where the stuff is')
    parser.add_argument('--out_dir', help='the directory to store results')
    parser.add_argument('--make',action='store_true',help='create coco data')
    parser.add_argument('--remove',action='store_true',help='remove certain categories from the annotations')
    parser.add_argument('--cat_count',action='store_true',help='generate countplot of class occurrences')
    parser.add_argument('--to_yolo',action='store_true',help='generate yolo annotations from coco')

    args = parser.parse_args()

    return args



def main():
	
	args = parse_args()

    # Both cannot be True
	assert args.make & args.remove is False


	cas = COCO_Assistant(args.work_dir, args.out_dir)

	if args.make is True:
		cas.coco_maker()

	if args.remove is True:
		cas.coco_remover()
	
	if args.cat_count is True:
		ann_dir = os.path.join(os.getcwd(),'annotations')
		assert os.path.exists(ann_dir) is True, "Annotations directory does not exist. Please create a directory here with all the json files you want to check"
		ann_files = [os.path.join(ann_dir,i) for i in os.listdir(ann_dir) if i[-4:] == "json"]
		for i in ann_files:
			coco_ann = COCO(i)
			cas.disp_cat_count(annotations=coco_ann, name=os.path.basename(i)[:-5], bar="h", show=False)

	if args.to_yolo is True:
		name = 'yolo'  # new dataset name
		ann_dir = os.path.join(os.getcwd(),'annotations')
		assert os.path.exists(ann_dir) is True, "Annotations directory does not exist. Please create a directory here with all the json files you want to check"
		file = os.path.join(ann_dir,'coco.json')  # coco json to convert
		cas.coco2yolo(name,file)


if __name__ == "__main__":
	main()
