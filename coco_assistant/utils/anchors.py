"""
Modified version of gen_anchors.py by Ngoc Anh Huynh (@experiencor)
Link: https://github.com/experiencor/keras-yolo2/blob/master/gen_anchors.py
"""

import random
import numpy as np
from pycocotools.coco import COCO


def iou(ann, centroids):
    w, h = ann
    similarities = []

    for centroid in centroids:
        c_w, c_h = centroid

        if c_w >= w and c_h >= h:
            similarity = w * h / (c_w * c_h)
        elif c_w >= w and c_h <= h:
            similarity = w * c_h / (w * h + (c_w - w) * c_h)
        elif c_w <= w and c_h >= h:
            similarity = c_w * h / (w * h + c_w * (c_h - h))
        else:  # means both w,h are bigger than c_w and c_h respectively
            similarity = (c_w * c_h) / (w * h)
        similarities.append(similarity)  # will become (k,) shape

    return np.array(similarities)


def avg_iou(anns, centroids):
    n, _ = anns.shape
    s = 0

    for i in range(anns.shape[0]):
        s += max(iou(anns[i], centroids))

    return s / n


def print_anchors(centroids):
    anchors = centroids.copy()

    widths = anchors[:, 0]
    sorted_indices = np.argsort(widths)

    r = "anchors: ["
    for i in sorted_indices[:-1]:
        r += "%0.2f,%0.2f, " % (anchors[i, 0], anchors[i, 1])

    # there should not be comma after last anchor, that's why
    r += "%0.2f,%0.2f" % (anchors[sorted_indices[-1:], 0], anchors[sorted_indices[-1:], 1])
    r += "]"
    print(r)
    print("")


def run_kmeans(ann_dims, anchor_num):
    ann_num = ann_dims.shape[0]
    prev_assignments = np.ones(ann_num) * (-1)
    iteration = 0
    old_distances = np.zeros((ann_num, anchor_num))

    r = random.SystemRandom()
    indices = [r.randrange(ann_dims.shape[0]) for i in range(anchor_num)]
    centroids = ann_dims[indices]
    anchor_dim = ann_dims.shape[1]

    while True:
        distances = []
        iteration += 1
        for i in range(ann_num):
            d = 1 - iou(ann_dims[i], centroids)
            distances.append(d)
        distances = np.array(distances)  # distances.shape = (ann_num, anchor_num)

        print(
            "iteration {}: dists = {}".format(iteration, np.sum(np.abs(old_distances - distances)))
        )

        # assign samples to centroids
        assignments = np.argmin(distances, axis=1)

        if (assignments == prev_assignments).all():
            return centroids

        # calculate new centroids
        centroid_sums = np.zeros((anchor_num, anchor_dim), np.float)
        for i in range(ann_num):
            centroid_sums[assignments[i]] += ann_dims[i]
        for j in range(anchor_num):
            centroids[j] = centroid_sums[j] / (np.sum(assignments == j) + 1e-6)

        prev_assignments = assignments.copy()
        old_distances = distances.copy()


def format_anchors(centroids):
    new_anchors = [[max(i)] * 2 for i in centroids.round(0)]
    return sorted(new_anchors)


def generate_anchors(cann, num_anchors, fmt=None):
    anns = cann.anns
    # dims is a list of tuples (w,h) for each bbox
    dims = [tuple(map(float, (anns[i]["bbox"][-2], anns[i]["bbox"][-1]))) for i in anns]
    dims = np.array(dims)
    centroids = run_kmeans(dims, num_anchors)

    # write anchors to file
    print("\naverage IOU for", num_anchors, "anchors:", "%0.2f" % avg_iou(dims, centroids))
    if fmt == "square":
        print("formatted anchors: {}\n".format(format_anchors(centroids)))
        return format_anchors(centroids)
    else:
        print_anchors(centroids.round(0))
        return centroids


if __name__ == "__main__":
    x = "/home/ashwin/Desktop/Projects/COCO-Assistant/data/annotations/val.json"
    xc = COCO(x)
    num_anchors = 2
    generate_anchors(xc, num_anchors, "square")
