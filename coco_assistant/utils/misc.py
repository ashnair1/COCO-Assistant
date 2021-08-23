import shutil
from pathlib import Path
from typing import Union


def make_clean(dpath):
    if dpath.exists():
        shutil.rmtree(dpath)
    dpath.mkdir(parents=True)


class DirectoryHandler:
    def __init__(
        self, img_dir: Union[str, Path], ann_dir: Union[str, Path], res_dir: Union[str, Path]
    ) -> None:

        self.img_dir = Path(img_dir)
        self.ann_dir = Path(ann_dir)

        self.names = self.check()

        # Create directory to store results
        self.res_dir = Path(res_dir)
        if not res_dir.exists():
            self.res_dir.mkdir()
        # else: warn user

    def create(self, folder: str) -> Path:
        dpath = self.res_dir / folder
        if dpath.exists():
            shutil.rmtree(dpath)
        dpath.mkdir(parents=True)
        return dpath

    def check(self):
        # Check if filenames are the same
        imgs = sorted(
            [i for i in self.img_dir.iterdir() if i.is_dir() and not i.name.startswith(".")]
        )

        jsons = sorted([j for j in self.ann_dir.iterdir() if j.suffix == ".json"])

        return [img.stem for img, ann in zip(imgs, jsons) if img.stem == ann.stem]
