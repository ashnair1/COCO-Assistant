import json

import os

from pycocotools.coco import COCO


def coco_remover(annFile, rcats):
    ann = COCO(annFile)
    remove_cats = rcats  #['Sat Dish']

    # Gives you a list of category ids of the categories to be removed
    catids_remove = ann.getCatIds(catNms=remove_cats)
    # Gives you a list of ids of annotations that contain those categories
    annids_remove = ann.getAnnIds(catIds=catids_remove)

    # Remove from category list
    cats = ann.loadCats(catids_remove)
    # Remove from annotation list
    anns = ann.loadAnns(annids_remove)

    with open(annFile) as it:
        x = json.load(it)

    x['categories'] = [i for i in x['categories'] if i not in cats]
    x['annotations'] = [i for i in x['annotations'] if i not in anns]

    with open(annFile + "2", 'w') as oa:
        json.dump(x, oa)


if __name__ == "__main__":
    # Get Annotations Dir and Image folder
    folder = "combined"
    annFile = os.path.join(os.getcwd(),
                           'annotations',
                           "iSAID_{}.json".format(folder))
    ann = COCO(annFile)

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
    coco_remover(annFile, rcats)
