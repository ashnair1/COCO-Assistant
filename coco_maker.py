import json

import os

import shutil

#from pycocotools.coco import COCO


def coco_maker(jsons, folders):
	img_dir = os.path.join(os.getcwd(), 'images')
	ann_dir = os.path.join(os.getcwd(), 'annotations')

	folders = [folder1, folder2]

	# Create the destination image folder
	dst_im_dir = os.path.join(img_dir, 'combined')
	if os.path.exists(dst_im_dir) is False:
	    os.mkdir(dst_im_dir)
	    #os.mkdir(dst_ann_dir)
	    


	# Combine images
	im_dirs = [os.path.join(img_dir, folder) for folder in folders]
	imext = [".png", ".jpg"]

    print("Combining Images...")
	for imdir in im_dirs:
		ims = [i for i in os.listdir(imdir) if i[-4:].lower() in imext]
		for im in ims:
			shutil.copyfile(os.path.join(imdir, im), os.path.join(dst_im_dir, im))

	# Combine annotations

	cann = {'images': [],
	    'annotations': [],
	    'info': None,
	    'licenses': None,
	    'categories': None}

	#ann_files = [os.path.join(ann_dir, "iSAID_{}.json".format(folder)) for folder in folders]

	#ann_jsons = os.listdir(ann_dir)

	anns = [i for i in jsons if i[-5:] == ".json"]

	print("Combining Annotations...")
	for each_ann in anns:
		#c = COCO(os.path.join(ann_dir, each_ann))
		with open(os.path.join(ann_dir, each_ann)) as a:
			c = json.load(a)

		cann['images'] = cann['images'] + c['images']
		cann['annotations'] = cann['annotations'] + c['annotations']
		if 'info' in list(c.keys()):
			cann['info'] = c['info']
		if 'licenses' in list(c.keys()):
			cann['licenses'] = c['licenses']
		cann['categories'] = c['categories']

	with open(os.path.join(ann_dir, 'combined.json'), 'w') as aw:
	    json.dump(cann, aw)


if __name__ == "__main__":
	# Get Annotations that you want to combine

    folder1 = "test2"
    #annFile1 = os.path.join(os.getcwd(), 'annotations', "iSAID_{}.json".format(folder1))
    #ann1 = COCO(annFile1)
    json1 = os.path.join(os.getcwd(), 'annotations', "iSAID_test.json")

    folder2 = "val2"
    #annFile2 = os.path.join(os.getcwd(), 'annotations', "iSAID_{}.json".format(folder2))
    #ann2 = COCO(annFile2)
    json2 = os.path.join(os.getcwd(), 'annotations', "iSAID_val.json")

    coco_maker([json1, json2], [folder1, folder2])
