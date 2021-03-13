import os

import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.widgets

import mpl_toolkits.axes_grid1

from pycocotools.coco import COCO

import skimage.io as io


# Reference: https://stackoverflow.com/questions/41545664/view-3-dimensional-numpy-array-in-matplotlib-and-taking-arguments-from-keyboard/41552601#41552601
# Need to make a minor change in the showAnns function in coco.py which involves passing in a matplotlib axes. Changes are as follows:
# 1. def showAnns(self, anns) -> def showAnns(self,anns, ax=None)
# 2. ax = plt.gca() -> if ax = None: ax = plt.gca()


class ImageSlider(matplotlib.widgets.Slider):
    def __init__(
        self,
        ax,
        label,
        numpages=10,
        valinit=0,
        valfmt="%1d",
        closedmin=True,
        closedmax=True,
        dragging=True,
        **kwargs,
    ):

        self.facecolor = kwargs.get("facecolor", "w")
        self.activecolor = kwargs.pop("activecolor", "b")
        self.fontsize = kwargs.pop("fontsize", 10)
        self.numpages = numpages
        self.fig = ax.figure

        super(ImageSlider, self).__init__(
            ax, label, 0, numpages, valinit=valinit, valfmt=valfmt, **kwargs
        )

        self.poly.set_visible(False)
        self.vline.set_visible(False)
        self.pageRects = []
        for i in range(numpages):
            facecolor = self.activecolor if i == valinit else self.facecolor
            r = matplotlib.patches.Rectangle(
                (float(i) / numpages, 0),
                1.0 / numpages,
                1,
                transform=ax.transAxes,
                facecolor=facecolor,
            )
            ax.add_artist(r)
            self.pageRects.append(r)
            ax.text(
                float(i) / numpages + 0.5 / numpages,
                0.5,
                str(i + 1),
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=self.fontsize,
            )
        self.valtext.set_visible(False)

        divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax)
        bax = divider.append_axes("right", size="5%", pad=0.05)
        fax = divider.append_axes("right", size="5%", pad=0.05)
        self.button_back = matplotlib.widgets.Button(
            bax, label="<-", color=self.facecolor, hovercolor=self.activecolor
        )
        self.button_forward = matplotlib.widgets.Button(
            fax, label="->", color=self.facecolor, hovercolor=self.activecolor
        )
        self.button_back.label.set_fontsize(self.fontsize)
        self.button_forward.label.set_fontsize(self.fontsize)
        self.button_back.on_clicked(self.backward)
        self.button_forward.on_clicked(self.forward)
        # connect keys:
        self.fig.canvas.mpl_connect("key_press_event", self.keyevent)

    def _update(self, event):
        super(ImageSlider, self)._update(event)
        i = int(self.val)
        if i >= self.valmax:
            return
        self._colorize(i)

    def _colorize(self, i):
        for j in range(self.numpages):
            self.pageRects[j].set_facecolor(self.facecolor)
        self.pageRects[i].set_facecolor(self.activecolor)

    def forward(self, event):
        current_i = int(self.val)
        i = current_i + 1
        if (i < self.valmin) or (i >= self.valmax):
            return
        self.set_val(i)
        self._colorize(i)

    def backward(self, event):
        current_i = int(self.val)
        i = current_i - 1
        if (i < self.valmin) or (i >= self.valmax):
            return
        self.set_val(i)
        self._colorize(i)

    # define keyevent, left: backwards, right: forwards
    def keyevent(self, event):
        # print event.key
        if event.key == "right":
            self.forward(event)
        if event.key == "left":
            self.backward(event)
        self.fig.canvas.draw()


def get_imgid_dict(ann):
    """
    Returns a dictionary with img ids as keys and img filenames as values
    """
    id_fn_dict = {}
    for item in ann.imgs.items():
        id_fn_dict[item[1]["file_name"]] = item[0]
    return id_fn_dict


def visualise_all(ann, img_dir):

    # Get List of Images
    imgs = os.listdir(img_dir)

    # Get image id and image filename mapping dict
    id_fn_dict = get_imgid_dict(ann)

    num_pages = len(ann.imgs.keys())

    # Visualise first image

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.18)

    im = io.imread(os.path.join(img_dir, imgs[0]))
    imgid = id_fn_dict[imgs[0]]
    # Modification for string image ids
    if isinstance(imgid, str):
        imgid = [imgid]
    annids = ann.getAnnIds(imgIds=imgid, iscrowd=None)
    anns = ann.loadAnns(annids)
    ax.axis("off")
    ax.set_title(imgs[0])
    ax.imshow(im)
    ann.showAnns(anns)

    ax_slider = fig.add_axes([0.05, 0.05, 0.9, 0.04])
    slider = ImageSlider(ax_slider, "Image", num_pages, activecolor="orange")

    def update(val):
        ax.clear()
        ind = int(slider.val)
        im = io.imread(os.path.join(img_dir, imgs[ind]))
        imid = id_fn_dict[imgs[ind]]
        # Modification for string image ids
        if isinstance(imid, str):
            imid = [imid]
        img_annids = ann.getAnnIds(imgIds=imid, iscrowd=None)
        img_anns = ann.loadAnns(img_annids)
        ax.axis("off")
        ax.set_title(imgs[ind])
        ax.imshow(im)
        ann.showAnns(img_anns, ax=ax)

    slider.on_changed(update)

    plt.show()


def visualise_single(ann, folder, img_filename):
    if folder not in ["train", "val", "test"]:
        raise AssertionError('Folder not in ["train", "val", "test"]')
    # Get image id and image filename mapping dict
    id_fn_dict = get_imgid_dict(ann)
    img_path = os.path.join(os.getcwd(), "images", folder, img_filename)
    im = io.imread(img_path)
    annids = ann.getAnnIds(imgIds=id_fn_dict[img_filename], iscrowd=None)
    anns = ann.loadAnns(annids)

    # load and display instance annotations
    plt.figure(figsize=(15, 15))
    plt.imshow(im)
    plt.axis("off")
    plt.title(img_filename)
    ann.showAnns(anns)
    plt.show()


if __name__ == "__main__":
    # Get Annotations Dir and Image folder
    folder = "test"
    annFile = os.path.join(os.getcwd(), "annotations", "iSAID_{}.json".format(folder))
    ann = COCO(annFile)
    # Visualisation Modes
    # visualise_all(ann, folder)
    visualise_single(ann, folder, "P0009.png")
