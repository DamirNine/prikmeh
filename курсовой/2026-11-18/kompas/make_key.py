# -*- coding: utf-8 -*-
"""Г-образный шестигранный ключ под гнездо S5 установочного винта М10 (18.11, для печати; в сборку не входит).
Шестигранник 4,7 под ключ (гнездо винта S5 — по 0,15 мм на сторону: напечатанное гнездо меньше, пруток толще), короткое плечо
25 мм (входит в гнездо глубиной 5), длинное 75 мм. Обе части — шестигранные призмы с гранью, параллельной плоскости XZ:
ключ лежит в этой плоскости и печатается плашмя, гранью на столе, без поддержек. Угол — наружный, прямой (призмы
перекрываются). Материал — PETG, как резьбовые детали.
    python make_key.py"""
import os
from math import cos, sin, radians
from kompas_build import A7, C, C3, PARTS_DIR, Part, k5, qi

S = 4.7                                           # размер под ключ
R = S / 2 / cos(radians(30))                      # радиус по вершинам
L_SHORT, L_LONG = 25.0, 75.0
FILE = "Ключ шестигранный S5 (печать).m3d"
hexagon = lambda: [(R * cos(radians(60 * k)), R * sin(radians(60 * k))) for k in range(6)]   # вершина на первой оси эскиза

p = Part("Ключ шестигранный S5", "", ("PETG (печать)", 1.27), "#d08a2a")
# длинное плечо вдоль z: в плоскости XY вершины на оси x → грани с нормалью ±y (лежит гранью на столе)
p.extrude(p.sketch(-R, lambda s: s.poly_fixed(hexagon())), L_LONG + R)
# короткое плечо вдоль −x: эскиз в плоскости YZ; гранями к ±y — вершины на оси z (какая ось эскиза — z, проверяется ниже)
top = qi(k5.TransferInterface(p.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
faces = lambda x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
# в плоскости YZ первая ось эскиза — по z (вершины на ней → грани к ±y), выдавливание идёт к −x (проверено 18.11)
p.extrude(p.sketch(0, lambda s: s.poly_fixed(hexagon()), p.p.GetDefaultEntity(C3.o3d_planeYOZ)), L_SHORT)
assert faces(-12.0, S / 2, 0.0) and faces(-12.0, -S / 2, 0.0), "короткое плечо не лежит гранью — поменять оси эскиза"
assert faces(0.0, S / 2, 40.0) and faces(0.0, -S / 2, 40.0), "длинное плечо не лежит гранью"
o = p.p.GetDefaultEntity(C3.o3d_pointCS); o.hidden = True; o.Update()            # на картинках — без начала координат и эскизов
for sk in p.sketches:
    sk.hidden = True; sk.Update()
p.save(FILE)
print(f"ключ: S{S} × ({L_SHORT:g} + {L_LONG:g}) мм → {os.path.join(PARTS_DIR, FILE)}")
