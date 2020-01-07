import os
import shutil

import tarfile

from coco_assistant import COCO_Assistant

import data_getter

from pycocotools.coco import COCO

import pytest


@pytest.fixture
def get_data():
	if os.path.isdir('./annotations') is False and os.path.isdir('./images') is False:
		# Download and extract data
		print("Downloading...")
		file_id = '1WAFzdtIa56UL4wFVHg2TaBMhtzqRc0F-'
		destination = 'test.tar.gz'
		data_getter.download_file_from_google_drive(file_id, destination)
		# Unzip data
		print("Extracting")
		tar = tarfile.open(destination, "r:gz")
		tar.extractall()
		tar.close()
	# Set up paths
	img_dir = os.path.join(os.getcwd(), 'images')
	ann_dir = os.path.join(os.getcwd(), 'annotations')
	return [img_dir, ann_dir]


#@pytest.mark.skip
def test_merge(get_data):
	cas = COCO_Assistant(get_data[0], get_data[1])
	cas.merge()
	comb = COCO(os.path.join(cas.resann_dir, 'merged.json'))
	# Get combined annotation count
	combann = len(comb.anns)
	# Get individual annotation counts
	ann_counts = [len(_cfile.anns) for _cfile in cas.annfiles]
	print(combann)
	print(sum(ann_counts))

	# Clean up
	shutil.rmtree(cas.res_dir)
	if sum(ann_counts) != combann:
		raise AssertionError("Failure in merging datasets")


#@pytest.mark.skip
def test_cat_removal(get_data):
	cas = COCO_Assistant(get_data[0], get_data[1])

	test_ann = "tiny2.json"
	test_rcats = sorted(['plane', 'ship', 'Large_Vehicle'])

	cas.remove_cat(interactive=False, jc=test_ann, rcats=test_rcats)

	orig = COCO(os.path.join(cas.ann_dir, cas.jc))
	rmj = COCO(os.path.join(cas.resrm_dir, cas.jc))

	orig_names = [list(orig.cats.values())[i]['name'] for i in range(len(orig.cats))]
	rmj_names = [list(rmj.cats.values())[i]['name'] for i in range(len(rmj.cats))]

	diff_names = sorted(list(set(orig_names) - set(rmj_names)))

	# Clean up
	shutil.rmtree(cas.resrm_dir)
	if diff_names != test_rcats:
		raise AssertionError("Failure in removing following categories: {}".format(test_rcats))
