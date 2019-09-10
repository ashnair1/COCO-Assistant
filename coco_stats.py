import logging
import os

import matplotlib.pyplot as plt

import pandas as pd

from pycocotools.coco import COCO

import seaborn as sns


logging.basicConfig(level=logging.DEBUG)


def cat_count(ann, name="test", show_count=False):
    # Prepare annotations dataframe
    # This should be done at the start
    ann_df = pd.DataFrame(ann.anns).transpose()

    plt.figure(figsize=(10, 10))
    chart = sns.countplot(
                data=ann_df,
		x='category_name',
		order=ann_df['category_name'].value_counts().index,
		palette='Set1')
    chart.set_title("Instances per category")
    chart.set_xticklabels(chart.get_xticklabels(), rotation=90)

    if show_count is True:
        for p in chart.patches:
            height = p.get_height()
            chart.text(p.get_x() + p.get_width() / 2., height + 0.9, height, ha="center")

    out_dir = os.path.join(os.getcwd(),'plots')
    if os.path.exists(out_dir) is False:
        os.mkdir(out_dir)

    plt.savefig(os.path.join(out_dir, name + "_cat_dist" ".jpg"))


    plt.show()


def get_areas(ann):
    obj_areas = []
    for key in ann.anns:
        obj_areas.append(ann.anns[key]['area'])
    return obj_areas


def view_area_dist(ann):
    obj_areas = get_areas(ann)
    import matplotlib.pyplot as plt
    plt.plot(range(len(obj_areas)), obj_areas)
    plt.xlabel("Objects")
    plt.ylabel("Areas")
    plt.title("Area Distribution")
    plt.show()


def get_object_size_split(ann, areaRng):

	obj_areas = get_areas(ann)

	assert areaRng == sorted(areaRng), "Area ranges incorrectly provided"

	small    = len(ann.getAnnIds(areaRng=[(areaRng[0]**2) - 1, areaRng[1]**2]))
	medium   = len(ann.getAnnIds(areaRng=[(areaRng[1]**2) - 1, areaRng[2]**2]))
	large    = len(ann.getAnnIds(areaRng=[(areaRng[2]**2) - 1, areaRng[3]**2]))
	left_out = len(ann.getAnnIds(areaRng=[0**2, (areaRng[0]**2)])) + len(ann.getAnnIds(areaRng=[areaRng[3]**2, (1e5**2)]))

	logging.debug("Number of small objects in set = {}".format(small))
	logging.debug("Number of medium objects in set = {}".format(medium))
	logging.debug("Number of large objects in set = {}".format(large))
	if left_out != 0:
		logging.debug("Number of objects ignored in set = {}".format(left_out))

	logging.debug("Number of objects = {}".format(len(obj_areas)))

	assert len(obj_areas) == small + medium + large + left_out
	return small, medium, large, left_out


def pi_area_split(ann, areaRng):
    
    # Pie chart
    small, medium, large, left_out = get_object_size_split(ann, areaRng)

    if left_out != 0:
    	sizes = [small, large, left_out, medium]
    	labels = 'Small', 'Large', 'Ignored', 'Medium'
    	colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    else:
    	sizes = [small, large, medium]
    	labels = 'Small', 'Large', 'Medium'
    	colors = ['#ff9999', '#66b3ff', '#ffcc99']


    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, colors=colors, labels=labels, autopct='%1.2f%%', startangle=90)
    #draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')  
    plt.title('Object Size Distribution', pad=20)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
	# Get Annotations Dir and Image folder
    folder = "combined"
    annFile = os.path.join(os.getcwd(), 'annotations', "iSAID_{}.json".format(folder))
    ann = COCO(annFile)

    cat_count(ann, folder, show_count=True)

    #pi_area_split(ann, areaRng=[0, 144, 512, 1e5])

    #view_area_dist(ann)
