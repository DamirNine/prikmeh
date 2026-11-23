# -*- coding: utf-8 -*-
"""21.11 (Корнеев А.Е.: на слайде «Прототипирование» — детали до и после МКЭ): изометрия деталей до доработки по МКЭ
(модели APM: кулиса, ползун, камень — 09.11, направляющая — 15.11) и после (модели 16.11 — доработанные по МКЭ, до разрезки
под печать); масса — для сверки с таблицей МКЭ. Картинки — fig/фэм_до_*.png, fig/фэм_после_*.png.
    python render_fem_parts.py"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
KURS = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "..", "2026-11-21", "kompas"))
from kompas_build import A5, A7, C, app, k5, qi
from PIL import Image, ImageChops

FIG = os.path.join(HERE, "fig")
PARTS = {"кулиса": (os.path.join(KURS, "2026-11-09", "apm", "Детали", "УКП.01.001 Кулиса (APM).m3d"),
                    os.path.join(KURS, "2026-11-16", "kompas", "Детали", "УКП.01.001 Кулиса.m3d")),
         "ползун": (os.path.join(KURS, "2026-11-09", "apm", "Детали", "УКП.03.001 Ползун (APM).m3d"),
                    os.path.join(KURS, "2026-11-16", "kompas", "Детали", "УКП.03.001 Ползун.m3d")),
         "камень": (os.path.join(KURS, "2026-11-09", "apm", "Детали", "УКП.02.001 Камень (APM).m3d"),
                    os.path.join(KURS, "2026-11-16", "kompas", "Детали", "УКП.02.001 Камень.m3d")),
         "направляющая": (os.path.join(KURS, "2026-11-15", "apm", "УКП.00.002 Направляющая (APM).m3d"),
                          os.path.join(KURS, "2026-11-16", "kompas", "Детали", "УКП.00.002 Направляющая.m3d"))}
SIZES = {}


def render(src, out):
    d = app.Documents.Open(src, True, False)
    d.Active = True
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    mass = qi(top, A7.IMassInertiaParam7).Mass
    coll = d5.GetViewProjectionCollection()
    next(coll.GetByIndex(i) for i in range(coll.GetCount()) if "зометр" in coll.GetByIndex(i).name).SetCurrent()
    d5.ZoomPrevNextOrAll(2)
    rp = d5.RasterFormatParam()
    rp.Init()
    rp.format, rp.colorType, rp.extResolution, rp.extScale, rp.onlyThinLine = C.ksRasterFormatPNG, 3, 300, 1.0, False
    assert d5.SaveAsToRasterFormat(out, rp), out
    d.Close(0)
    im = Image.open(out).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 10 else 0).getbbox()
    im = im.crop((max(bb[0] - 15, 0), max(bb[1] - 15, 0), min(bb[2] + 15, im.width), min(bb[3] + 15, im.height)))
    im.thumbnail((1200, 1200))
    im.save(out)
    SIZES[os.path.basename(out)] = im.size
    return mass


