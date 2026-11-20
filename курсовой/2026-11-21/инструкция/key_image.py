# -*- coding: utf-8 -*-
"""Картинка ключа-шестигранника для списка деталей инструкции (img/p_key.png): деталь не входит в сборку, поэтому снимается
отдельно — изометрия, по габариту ~1300 пикселей (как кадры p_* в make_images.py).
    python key_image.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, C, PARTS_DIR, app, k5
from PIL import Image

SRC = os.path.join(PARTS_DIR, "Ключ шестигранный S5 (печать).m3d")
OUT = os.path.join(HERE, "img", "p_key.png")
d = app.Documents.Open(SRC, True, True)
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
coll = d5.GetViewProjectionCollection()
next(coll.GetByIndex(i) for i in range(coll.GetCount()) if "зометр" in coll.GetByIndex(i).name).SetCurrent()
d5.ZoomPrevNextOrAll(2)


def raster(dpi):
    rp = d5.RasterFormatParam(); rp.Init()
    rp.format, rp.colorType, rp.extResolution, rp.extScale, rp.onlyThinLine = C.ksRasterFormatPNG, 3, dpi, 1.0, False
    assert d5.SaveAsToRasterFormat(OUT, rp), OUT
    im = Image.open(OUT).convert("RGB")
    return im, Image.eval(im.convert("L"), lambda v: 255 if v < 250 else 0).getbbox()


im, bb = raster(100)
im, bb = raster(min(1500, 100 * 1300 / max(bb[2] - bb[0], bb[3] - bb[1])))
im = im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height)))
im.thumbnail((1300, 1300))
im.save(OUT, optimize=True)
d.Close(0)
print("  p_key:", im.size)
