import logging
import os

import matplotlib.pyplot as plt

import pandas as pd

from pycocotools.coco import COCO

import seaborn as sns


logging.basicConfig(level=logging.DEBUG)


def cat_count(anns, names, show_count=False, save=False):

    fig, axes = plt.subplots(1, len(anns), sharey=False)

    # Making axes iterable if only single annotation is present
    if len(anns) == 1:
        axes = [axes]

    # Prepare annotations dataframe
    # This should be done at the start
    for ann, name, ax in zip(anns, names, axes):
        ann_df = pd.DataFrame(ann.anns).transpose()
        if "category_name" in ann_df.columns:
            chart = sns.countplot(
                data=ann_df,
                x="category_name",
                order=ann_df["category_name"].value_counts().index,
                palette="Set1",
                ax=ax,
            )
        else:
            # Add a new column -> category name
            ann_df["category_name"] = ann_df.apply(
                lambda row: ann.cats[row.category_id]["name"], axis=1
            )
            chart = sns.countplot(
                data=ann_df,
                x="category_name",
                order=ann_df["category_name"].value_counts().index,
                palette="Set1",
                ax=ax,
            )

        chart.set_title(name)
        chart.set_xticklabels(chart.get_xticklabels(), rotation=90)

        if show_count is True:
            for p in chart.patches:
                height = p.get_height()
                chart.text(p.get_x() + p.get_width() / 2.0, height + 0.9, height, ha="center")

    plt.suptitle("Instances per category", fontsize=14, fontweight="bold")
    plt.tight_layout()

    fig = plt.gcf()
    fig.set_size_inches(11, 11)

    out_dir = os.path.join(os.getcwd(), "results", "plots")
    if save is True:
        if os.path.exists(out_dir) is False:
            os.mkdir(out_dir)
        plt.savefig(
            os.path.join(out_dir, "cat_dist" + ".png"),
            bbox_inches="tight",
            pad_inches=0,
            dpi=plt.gcf().dpi,
        )

    plt.show()


def get_areas(ann):
    obj_areas = []
    for key in ann.anns:
        obj_areas.append(ann.anns[key]["area"])
    return obj_areas


def view_area_dist(ann):
    obj_areas = get_areas(ann)
    plt.plot(range(len(obj_areas)), obj_areas)
    plt.xlabel("Objects")
    plt.ylabel("Areas")
    plt.title("Area Distribution")
    plt.show()


def get_object_size_split(ann, areaRng):

    obj_areas = get_areas(ann)

    if areaRng != sorted(areaRng):
        raise AssertionError("Area ranges incorrectly provided")

    small = len(ann.getAnnIds(areaRng=[(areaRng[0] ** 2), areaRng[1] ** 2]))
    medium = len(ann.getAnnIds(areaRng=[(areaRng[1] ** 2), areaRng[2] ** 2]))
    large = len(ann.getAnnIds(areaRng=[(areaRng[2] ** 2), areaRng[3] ** 2]))
    left_out = len(ann.getAnnIds(areaRng=[0 ** 2, (areaRng[0] ** 2)])) + len(
        ann.getAnnIds(areaRng=[areaRng[3] ** 2, (1e5 ** 2)])
    )

    logging.debug("Number of small objects in set = %s", small)
    logging.debug("Number of medium objects in set = %s", medium)
    logging.debug("Number of large objects in set = %s", large)
    if left_out != 0:
        logging.debug("Number of objects ignored in set = %s", left_out)

    logging.debug("Number of objects = %s", len(obj_areas))

    if len(obj_areas) != small + medium + large + left_out:
        raise AssertionError("Sum of objects in different area ranges != Total number of objects")
    return small, medium, large, left_out


def pi_area_split_single(ann, areaRng):

    # Pie chart
    small, medium, large, left_out = get_object_size_split(ann, areaRng)

    if left_out != 0:
        sizes = [small, large, left_out, medium]
        labels = "Small", "Large", "Ignored", "Medium"
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]
    else:
        sizes = [small, large, medium]
        labels = "Small", "Large", "Medium"
        colors = ["#ff9999", "#66b3ff", "#ffcc99"]

    _, ax1 = plt.subplots()
    ax1.pie(sizes, colors=colors, labels=labels, autopct="%1.2f%%", startangle=90)
    # draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis("equal")
    plt.title("Object Size Distribution", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.show()


def pi_area_split(anns, names, areaRng, save=False):

    stuff = []

    for ann in anns:
        small, medium, large, left_out = get_object_size_split(ann, areaRng)

        if left_out != 0:
            sizes = [small, large, left_out, medium]
            labels = "Small", "Large", "Ignored", "Medium"
            colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]
        else:
            sizes = [small, large, medium]
            labels = "Small", "Large", "Medium"
            colors = ["#ff9999", "#66b3ff", "#ffcc99"]

        stuff.append([sizes, labels, colors])

    fig, axs = plt.subplots(1, len(anns), figsize=(11, 11))

    for s, name, ax in zip(stuff, names, axs.flat):
        ax.clear()
        ax.pie(s[0], labels=s[1], colors=s[2], autopct="%1.2f%%", startangle=90)
        # draw circle
        # centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        # fig = plt.gcf()
        # fig.gca().add_artist(centre_circle)
        # Equal aspect ratio ensures that pie is drawn as a circle
        # ax.axis('equal')
        # from matplotlib import rcParams
        # rcParams['axes.titlepad'] = 100
        ax.set_title(name)

    # plt.title('Object Size Distribution', pad=20)
    fig.suptitle("Object Size Distribution", fontsize=14, fontweight="bold")
    # plt.tight_layout()

    # fig = plt.gcf()
    # fig.set_size_inches(11,11)

    out_dir = os.path.join(os.getcwd(), "results", "plots")

    if save is True:
        if os.path.exists(out_dir) is False:
            os.mkdir(out_dir)
        plt.savefig(os.path.join(out_dir, "area_dist" + ".png"), dpi=fig.dpi)
    plt.show()


if __name__ == "__main__":
    # Get Annotations Dir and Image folder
    folder1 = "test1"
    annFile1 = os.path.join(os.getcwd(), "annotations", "{}.json".format(folder1))
    ann1 = COCO(annFile1)

    folder2 = "test2"
    annFile2 = os.path.join(os.getcwd(), "annotations", "{}.json".format(folder2))
    ann2 = COCO(annFile2)

    folder3 = "test3"
    annFile3 = os.path.join(os.getcwd(), "annotations", "{}.json".format(folder3))
    ann3 = COCO(annFile3)

    # cat_count(ann, folder, show_count=True)
    # pi_area_split(ann, areaRng=[0, 144, 512, 1e5])
    # pi_area_split_multi([ann1, ann2, ann3], folders=[folder1, folder2, folder3], areaRng=[10, 144, 512, 1e5])
    # view_area_dist(ann)
