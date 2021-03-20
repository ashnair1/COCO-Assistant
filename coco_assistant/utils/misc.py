import shutil

def make_clean(dpath):
    if dpath.exists():
        shutil.rmtree(dpath)
        dpath.mkdir(parents=True)
    else:
        dpath.mkdir(parents=True)