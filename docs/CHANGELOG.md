# History

## 0.3.5 (2021-05-06)

**Changes**:

-   Replace os with pathlib for managing paths.
-   Fixed bug in det2seg where small annotations were covered by larger annotations.
-   Faster category removal by [@xychen9459](https://github.com/xychen9459).

## 0.3.4 (2021-03-14)

**Changes**:

-   Add support for merging datasets with different categories.
-   Adding colour palette to segmasks is now optional.
-   Ignore hidden files.

## 0.3.1 (2020-05-18)

**Bugfix**:

-   Fix for coco_stats by [@Lplenka](https://github.com/Lplenka). Refer [#15](https://github.com/ashnair1/COCO-Assistant/pull/15)

## 0.3.0 (2020-04-19)

**Changes**:

-   `combine` has been renamed to `merge`.
-   Add support for merging annotations only.

**Deprecations**:

-   Deprecate converters. This was motivated by two reasons:
    -   There are too many conversion formats. Trying to include even the most popular ones makes the project unwieldy. Better to use one of the readily available scripts online.
    -   Until now, the repository only supported TFRecord. Tensorflow is a large library and it does not make sense for it to be a project requirement when it's only used for a singular task of converting to TFRecord.

## 0.2.0 (2019-11-28)

**New features**:

-   Generate anchors from the dataset using K-means.
-   Generate segmentation masks from dataset.

**Changes**:

-   Modified category removal to accept a list of categories as opposed to entering categories one after the other.

## 0.1.0 (2019-10-07)

First release on PyPI. Supports the following functions:

-   Merge datasets.
-   Remove specfiic category from dataset.
-   Generate annotations statistics - distribution of object areas and category distribution.
-   Annotation visualiser for viewing the entire dataset.
-   Converter for converting annotations to TFRecord format.
