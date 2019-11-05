import logging
import os
from random import shuffle

from PIL import Image

from pycocotools.coco import COCO

import tensorflow as tf

from .utils import dataset_util

logging.basicConfig(level=logging.WARNING)

# flags = tf.app.flags
# flags.DEFINE_string('data_dir', '', 'Root directory to raw Microsoft COCO dataset.')
# flags.DEFINE_string('set', 'train', 'Convert training set or validation set')
# flags.DEFINE_string('output_filepath', '', 'Path to output TFRecord')
# flags.DEFINE_bool('shuffle_imgs',True,'whether to shuffle images of coco')
# FLAGS = flags.FLAGS


def load_coco_detection_dataset(imgs_dir, annotations, shuffle_img=True):
    """Load data from dataset by pycocotools. This tools can be download from "http://mscoco.org/dataset/#download"
    Args:
        imgs_dir: directories of coco images
        annotations_filepath: file path of coco annotations file
        shuffle_img: wheter to shuffle images order
    Return:
        coco_data: list of dictionary format information of each image
    """
    coco = annotations
    img_ids = coco.getImgIds()  # totally 82783 images
    cat_ids = coco.getCatIds()  #totally 90 catagories, however, the number of categories is not continuous, \
                               # [0,12,26,29,30,45,66,68,69,71,83] are missing, this is the problem of coco dataset.

    if shuffle_img:
        shuffle(img_ids)

    coco_data = []

    nb_imgs = len(img_ids)
    for index, img_id in enumerate(img_ids):
        if index % 100 == 0:
            print("Readling images: %d / %d " % (index, nb_imgs))
        img_info = {}
        bboxes = []
        labels = []

        img_detail = coco.loadImgs(img_id)[0]
        try:
            pic_height = img_detail['height']
            pic_width = img_detail['width']
        except KeyError:
            logging.warning("Image dimension is missing from the image field."
                            " Proceeding to read it manually")
            im = Image.open(os.path.join(imgs_dir, img_detail['file_name']))
            pic_height = im.size[1]
            pic_width = im.size[0]

        ann_ids = coco.getAnnIds(imgIds=img_id, catIds=cat_ids)
        anns = coco.loadAnns(ann_ids)
        for ann in anns:
            bboxes_data = ann['bbox']
            # the format of coco bounding boxs is [Xmin, Ymin, width, height]
            bboxes_data = [bboxes_data[0] / float(pic_width), bboxes_data[1] / float(pic_height),
                           bboxes_data[2] / float(pic_width), bboxes_data[3] / float(pic_height)]
            bboxes.append(bboxes_data)
            labels.append(ann['category_id'])

        img_path = os.path.join(imgs_dir, img_detail['file_name'])
        img_bytes = tf.gfile.FastGFile(img_path, 'rb').read()

        img_info['pixel_data'] = img_bytes
        img_info['height'] = pic_height
        img_info['width'] = pic_width
        img_info['bboxes'] = bboxes
        img_info['labels'] = labels

        coco_data.append(img_info)

    return coco_data


def dict_to_coco_example(img_data):
    """Convert python dictionary formath data of one image to tf.Example proto.
    Args:
        img_data: infomation of one image, inclue bounding box, labels of bounding box,\
            height, width, encoded pixel data.
    Returns:
        example: The converted tf.Example
    """
    bboxes = img_data['bboxes']
    xmin, xmax, ymin, ymax = [], [], [], []
    for bbox in bboxes:
        xmin.append(bbox[0])
        xmax.append(bbox[0] + bbox[2])
        ymin.append(bbox[1])
        ymax.append(bbox[1] + bbox[3])

    example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(img_data['height']),
        'image/width': dataset_util.int64_feature(img_data['width']),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmin),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmax),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymin),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymax),
        'image/object/class/label': dataset_util.int64_list_feature(img_data['labels']),
        'image/encoded': dataset_util.bytes_feature(img_data['pixel_data']),
        'image/format': dataset_util.bytes_feature('jpeg'.encode('utf-8')),
    }))
    return example


def convert(ann, img_dir, _format):

    dst = os.path.join(os.path.dirname(os.path.dirname(img_dir)),
                       'annotations',
                       os.path.basename(img_dir) + ".tfrecord")

    if _format == "TFRecord":
        # load total coco data
        coco_data = load_coco_detection_dataset(img_dir, ann, shuffle_img=True)
        total_imgs = len(coco_data)
        # write coco data to tf record
        with tf.python_io.TFRecordWriter(dst) as tfrecord_writer:
            for index, img_data in enumerate(coco_data):
                if index % 100 == 0:
                    print("Converting images: %d / %d" % (index, total_imgs))
                example = dict_to_coco_example(img_data)
                tfrecord_writer.write(example.SerializeToString())


if __name__ == "__main__":
    _format = "TFRecord"
    ann = COCO("/home/ashwin/Desktop/keras-retinanet/data/IIAI/annotations/train.json")
    img_dir = "/home/ashwin/Desktop/keras-retinanet/data/IIAI/images/train"
    convert(ann, img_dir, _format)
