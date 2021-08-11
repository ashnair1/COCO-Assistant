import os
import shutil
import tarfile
from pathlib import Path

import pytest
from pycocotools.coco import COCO

from coco_assistant import COCO_Assistant
from coco_assistant.utils import CatRemapper
from tests import data_getter


@pytest.fixture
def get_data():
    if os.path.isdir("./annotations") is False and os.path.isdir("./images") is False:
        # Download and extract data
        print("Downloading...")
        file_id = "1wvAnXDnMq2xDmYCZ6kUXIiMyHxYTigjy"
        destination = "test.tar.gz"
        data_getter.download_file_from_google_drive(file_id, destination)
        # Unzip data
        print("Extracting")
        tar = tarfile.open(destination, "r:gz")
        tar.extractall()
        tar.close()
    # Set up paths
    img_dir = os.path.join(os.getcwd(), "images")
    ann_dir = os.path.join(os.getcwd(), "annotations")
    return [img_dir, ann_dir]


# @pytest.mark.skip
def test_merge(get_data):
    cas = COCO_Assistant(get_data[0], get_data[1])
    cas.merge()
    comb = COCO(cas.res_dir / "merged/annotations/merged.json")
    # Get combined annotation count
    combann = len(comb.anns)
    # Get individual annotation counts
    anns = cas.anndict.values()
    ann_counts = [len(_cfile.anns) for _cfile in anns]
    print(combann)
    print(sum(ann_counts))

    # Clean up
    shutil.rmtree(cas.res_dir)
    if sum(ann_counts) != combann:
        raise AssertionError("Failure in merging datasets")


# @pytest.mark.skip
def test_cat_removal(get_data):
    cas = COCO_Assistant(get_data[0], get_data[1])

    test_ann = "tiny2.json"
    test_rcats = sorted(["plane", "ship", "Large_Vehicle"])

    cas.remove_cat(interactive=False, jc=Path(get_data[1]) / test_ann, rcats=test_rcats)

    orig = cas.anndict[test_ann[:-5]]
    rmj = COCO(cas.res_dir / "removal" / test_ann)

    orig_names = [list(orig.cats.values())[i]["name"] for i in range(len(orig.cats))]
    rmj_names = [list(rmj.cats.values())[i]["name"] for i in range(len(rmj.cats))]

    diff_names = sorted(list(set(orig_names) - set(rmj_names)))

    # Clean up
    shutil.rmtree(cas.res_dir / "removal")
    if diff_names != test_rcats:
        raise AssertionError("Failure in removing following categories: {}".format(test_rcats))


@pytest.mark.parametrize(
    "cat1, cat2, result",
    [
        (
            [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, {"id": 3, "name": "C"}],
            [{"id": 1, "name": "B"}, {"id": 2, "name": "C"}, {"id": 3, "name": "A"}],
            (
                [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}, {"id": 3, "name": "c"}],
                {3: 1, 1: 2, 2: 3},
                {},
            ),
        ),
        (
            [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, {"id": 3, "name": "C"}],
            [{"id": 1, "name": "B"}, {"id": 2, "name": "A"}, {"id": 3, "name": "F"}],
            (
                (
                    [
                        {"id": 1, "name": "a"},
                        {"id": 2, "name": "b"},
                        {"id": 3, "name": "c"},
                        {"id": 4, "name": "f"},
                    ],
                    {2: 1, 1: 2},
                    {3: 4},
                )
            ),
        ),
        (
            [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, {"id": 3, "name": "C"}],
            [{"id": 1, "name": "D"}, {"id": 2, "name": "E"}, {"id": 3, "name": "F"}],
            (
                [
                    {"id": 1, "name": "a"},
                    {"id": 2, "name": "b"},
                    {"id": 3, "name": "c"},
                    {"id": 4, "name": "d"},
                    {"id": 5, "name": "e"},
                    {"id": 6, "name": "f"},
                ],
                {},
                {1: 4, 2: 5, 3: 6},
            ),
        ),
    ],
    ids=["overlap", "overlap & new", "new"],
)
def test_cat_remapper(cat1, cat2, result):
    cmapper = CatRemapper(cat1, cat2)
    res = cmapper.remap_cats()
    if res != result:
        raise AssertionError("CatRemapper failed")
