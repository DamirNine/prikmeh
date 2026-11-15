# -*- coding: utf-8 -*-
"""Картинки новых деталей 15.11 (стойка с выемкой, направляющая) и узла сборки — PNG из КОМПАСа в папку картинки/.
Ракурс — изометрия спереди-справа-сверху (матрица вида: ось X экрана, ось Y, к наблюдателю, сдвиг)."""
import os
from math import sqrt
from kompas_build import A5, A7, C, FILES, HERE, PARTS_DIR, app, k5, qi

OUT = os.path.join(HERE, "картинки")
os.makedirs(OUT, exist_ok=True)


def view_matrix(d7):
    # к наблюдателю: (1, 0.8, 1.6) — спереди (z), справа (x) и сверху (y)
    vz = [1.0, 0.8, 1.6]; n = sqrt(sum(c * c for c in vz)); vz = [c / n for c in vz]
    up = [0.0, 1.0, 0.0]
    vx = [up[1] * vz[2] - up[2] * vz[1], up[2] * vz[0] - up[0] * vz[2], up[0] * vz[1] - up[1] * vz[0]]
    n = sqrt(sum(c * c for c in vx)); vx = [c / n for c in vx]
    vy = [vz[1] * vx[2] - vz[2] * vx[1], vz[2] * vx[0] - vz[0] * vx[2], vz[0] * vx[1] - vz[1] * vx[0]]
    m = vx + [0.0] + vy + [0.0] + vz + [0.0] + [0.0, 0.0, 0.0, 1.0]
    vpm = qi(d7, A7.IKompasDocument3D1).ViewProjectionManager
    vpm.SetMatrix3D(m, 1.0)


def shot(path, png, hide=()):
    d = app.Documents.Open(path, True, False)
    assert d is not None, path
    d7 = qi(d, A7.IKompasDocument3D)
    for i in range(d7.TopPart.Parts.Count if hide else 0):
        p = qi(d7.TopPart.Parts.Part(i), A7.IPart7)
        if p.Name in hide:
            o = qi(p, A7.IModelObject); o.Hidden = True; o.Update()
    view_matrix(d)
    d7.TopPart.RebuildModel(True) if hide else None
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    d5.zoomPrevNextOrAll(2) if hasattr(d5, "zoomPrevNextOrAll") else None
    rp = A5.ksRasterFormatParam(d5.RasterFormatParam())
    rp.Init(); rp.format = 3; rp.extResolution = 110; rp.colorType = 3; rp.onlyThinLine = False
    ok = d5.SaveAsToRasterFormat(os.path.join(OUT, png), rp)
    d.Close(0)
    print(png, "сохранено" if ok else "НЕ сохранено")


shot(os.path.join(PARTS_DIR, FILES["guide"]), "направляющая.png")
shot(os.path.join(PARTS_DIR, FILES["cover"]), "кожух_с_защёлками.png")
shot(os.path.join(PARTS_DIR, FILES["stand"]), "стойка_с_выемкой.png")
shot(os.path.join(HERE, "УКП.00.000 Укупориватель.a3d"), "сборка_без_кожуха.png", hide=("Кожух", "Бутылка"))
shot(os.path.join(HERE, "УКП.00.000 Укупориватель.a3d"), "сборка_с_кожухом.png", hide=("Бутылка",))
