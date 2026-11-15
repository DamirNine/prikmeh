# -*- coding: utf-8 -*-
"""Проверка варианта М10: пересечения тел в мини-сборке (витки пальца и гайки, шайба) и сдвиг гайки вдоль оси — где она
упирается; картинки деталей и сборки в папку картинки/.
    python check_m10.py"""
import os, sys
from itertools import combinations
from math import sqrt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "2026-11-15", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, app, k5, qi
from build_m10 import ASM, FILES

OUT = os.path.join(HERE, "картинки"); os.makedirs(OUT, exist_ok=True)
doc = qi(app.Documents.Open(ASM, True, False), A7.IKompasDocument3D)
top = doc.TopPart
parts = {qi(top.Parts.Part(i), A7.IPart7).Name: qi(top.Parts.Part(i), A7.IPart7) for i in range(top.Parts.Count)}


def bodies(p):
    b = qi(p, A7.IFeature7).ResultBodies
    return [] if b is None else [qi(x, A7.IBody7) for x in (b if isinstance(b, tuple) else (b,))]


B = {k: bodies(p) for k, p in parts.items()}
for a, b in combinations(B, 2):
    hit = any(x.CheckIntersectionWithBody(y, False) for x in B[a] for y in B[b])
    print(f"  {a} — {b}: {'ПЕРЕСЕЧЕНИЕ' if hit else 'нет пересечения'}")
doc.Close(0)


def shot(path, png, m):
    d = app.Documents.Open(path, True, False)
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    vpm = qi(d, A7.IKompasDocument3D1).ViewProjectionManager
    vpm.SetMatrix3D(m, 1.0)
    d5.ZoomPrevNextOrAll(2)
    rp = A5.ksRasterFormatParam(d5.RasterFormatParam())
    rp.Init(); rp.format = 3; rp.extResolution = 300; rp.colorType = 3; rp.onlyThinLine = False
    ok = d5.SaveAsToRasterFormat(os.path.join(OUT, png), rp)
    d.Close(0)
    print(" ", png, "сохранено" if ok else "НЕ сохранено")


def matrix(vz):                                   # взгляд с направления vz (к наблюдателю), ось z детали — вверх на картинке
    n = sqrt(sum(c * c for c in vz)); vz = [c / n for c in vz]
    up = [0.0, 0.0, 1.0]
    vx = [up[1] * vz[2] - up[2] * vz[1], up[2] * vz[0] - up[0] * vz[2], up[0] * vz[1] - up[1] * vz[0]]
    n = sqrt(sum(c * c for c in vx)); vx = [c / n for c in vx]
    vy = [vz[1] * vx[2] - vz[2] * vx[1], vz[2] * vx[0] - vz[0] * vx[2], vz[0] * vx[1] - vz[1] * vx[0]]
    return vx + [0.0] + vy + [0.0] + vz + [0.0] + [0.0, 0.0, 0.0, 1.0]


SIDE = matrix([1.0, -1.6, 0.35])
shot(os.path.join(HERE, FILES["pin"]), "палец_М10.png", SIDE)
shot(os.path.join(HERE, FILES["nut"]), "гайка_М10.png", matrix([1.0, -1.2, 1.6]))
shot(ASM, "палец_шайба_гайка.png", SIDE)
