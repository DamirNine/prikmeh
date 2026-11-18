# -*- coding: utf-8 -*-
"""Г-образный шестигранный ключ под гнездо S5 установочного винта М10 (18.11, для печати; в сборку не входит).
Как настоящий ключ: шестигранный пруток, согнутый по радиусу. Шестигранник 4,7 под ключ (гнездо винта S5 — по 0,15 мм на
сторону под печать) протягивается кинематической операцией по траектории «отрезок — дуга R7 по оси прутка — отрезок» в
плоскости XZ: длинное плечо вдоль z до 75, короткое — вдоль −x до 25 (внутренний радиус гиба 4,3). Грани шестигранника
параллельны плоскости XZ — ключ лежит гранью на столе и печатается без поддержек. Материал — PETG.
    python make_key.py"""
import os
from math import cos, sin, radians
from kompas_build import A7, C, C3, PARTS_DIR, Part, k5, qi

S = 4.7                                           # размер под ключ
R = S / 2 / cos(radians(30))                      # радиус по вершинам
RB = 7.0                                          # радиус гиба по оси прутка
L_SHORT, L_LONG = 25.0, 75.0                      # от оси другого плеча до торца
FILE = "Ключ шестигранный S5 (печать).m3d"

p = Part("Ключ шестигранный S5", "", ("PETG (печать)", 1.27), "#d08a2a")
# профиль — в начале траектории (торец длинного плеча, z = 75): вершины на оси x → грани с нормалью ±y
prof = p.sketch(L_LONG, lambda s: s.poly_fixed([(R * cos(radians(60 * k)), R * sin(radians(60 * k))) for k in range(6)]))


def path(s):
    """траектория в плоскости XZ, координаты эскиза (u, v) = (x, −z): (0, 75) → (0, RB) → дуга → (−RB, 0) → (−25, 0)"""
    a = s.d2.ksLineSeg(0, -L_LONG, 0, -RB, 1)
    b = s.d2.ksArcByPoint(-RB, -RB, RB, 0, -RB, -RB, 0, 1, 1)           # центр (−RB, −RB), против часовой
    c = s.d2.ksLineSeg(-RB, 0, -L_SHORT, 0, 1)
    for obj, pts in ((a, (0, 1)), (b, (0, 1, 2)), (c, (0, 1))):
        for i in pts:
            s.cons(obj, C.ksCFixedPoint, i)


traj = p.sketch(0, path, p.p.GetDefaultEntity(C3.o3d_planeXOZ))
ev = p.p.NewEntity(C3.o3d_baseEvolution)
ed = ev.GetDefinition()
ed.sketchShiftType = 1
ed.SetSketch(prof)
ed.PathPartArray().Add(traj)
assert ev.Create(), "ключ не построен"
top = qi(k5.TransferInterface(p.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
faces = lambda x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
assert faces(0.0, S / 2, 40.0) and faces(0.0, -S / 2, 40.0), "длинное плечо не лежит гранью"
assert faces(-18.0, S / 2, 0.0) and faces(-18.0, -S / 2, 0.0), "короткое плечо не лежит гранью"
o = p.p.GetDefaultEntity(C3.o3d_pointCS); o.hidden = True; o.Update()            # на картинках — без начала координат и эскизов
for sk in p.sketches:
    sk.hidden = True; sk.Update()
p.save(FILE)
print(f"ключ: S{S}, плечи {L_SHORT:g} и {L_LONG:g}, гиб R{RB:g} по оси → {os.path.join(PARTS_DIR, FILE)}")
