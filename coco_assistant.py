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
		
	def coco_cat_count(self,annotations):
	    
	    with open(annotations) as a:
	    	ann = json.load(a)
	    
	    a_cats = []

	    for i in ann['annotations']:
	        j = i['category_id']
	        for cat in ann['categories']:
	            if j == cat['id']:
	                a_cats.append(cat['name'])
	        
	        
	    # Create dictionary of category and counts
	    a_count_dict = dict(Counter(a_cats))
	    
	    # Create dictionary of category and ids
	    ids = []
	    cats = []
	    for ind in range(len(a['categories'])):
	        cat_id,cat,_ = zip(a['categories'][ind].values())
	        ids.append(cat_id[0])
	        cats.append(cat[0])
	    cat_dict = dict(zip(ids, cats))
	    
	    missing_train = set(list(cat_dict.values())) - set(list(a_count_dict.keys()))
	    a_add = dict(zip(missing_train, [0]*len(missing_train)))
	    a_count_dict.update(a_add)
	    
	    return [a_count_dict,a_add]

	def show_class_distribution_both(annotations=None, dist="train",bar="h"):
	    gtrain,gval = annotations
	    assert dist in ["train","val"], "Has to be either 'train' or 'val' data"
	    train_cats, val_cats, _ = cat_count([gtrain,gval])
	    train_labels, train_values = zip(*Counter(train_cats).items())
	    val_labels, val_values = zip(*Counter(val_cats).items())


	    dat = ["train","val"]
	    
	    for name in dat:
	        
	        if name == "train":
	            labels = train_labels
	            values = train_values
	        elif name == "val":
	            labels = val_labels
	            values = val_values
	        
	        
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
	                plt.text(v + 3, i , str(v), color='blue', fontweight='bold')
	        elif bar == "v":
	            for i, v in enumerate(values):
	                plt.text(i,v + 5,str(v), color='blue', fontsize=0.6*fig_size[0],fontweight='bold')

	        plt.savefig(name + ".jpg")
	        plt.show()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', help='the directory where the stuff is')
    parser.add_argument('--out_dir', help='the directory to store results')
    parser.add_argument('--make',action='store_true',help='create coco data')
    parser.add_argument('--remove',action='store_true',help='remove certain categories from the annotations')
    parser.add_argument('--cat_count',action='store_true',help='generate countplot of class occurrences')
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
	
	if args.cat_count is True:
		ann_file = None
		cas.coco_cat_count(annotations=ann_file)

if __name__ == "__main__":
	main()
