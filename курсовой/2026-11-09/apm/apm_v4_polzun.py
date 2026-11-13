# -*- coding: utf-8 -*-
"""Ползун облегчённый: копия «Ползун (APM)» (с закреплением и силами APM FEM) + доработки по первому расчёту
(SVM: шток ≈ 37 МПа как в ручном расчёте, пик 95,9 МПа — острый угол шток–головка; головка и блок почти без напряжений):
  — головка-колокол: Ø40 остаётся до y = −97 (≈5,5 мм над потолком полости −102,56), выше — конус от Ø40 к штоку Ø8 у y = −80;
  — скругления R3 в переходах шток–головка и шток–блок.
Грани закрепления (отверстие под палец) и сил (конус горловины, боковая грань блока) не меняются — остаётся сетка и расчёт.
    python apm_v4_polzun.py"""
import os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
from kompas_build import A5, A7, C, C3, Sketch2D, app, k5, qi
import apm_prep as ap

SRC = os.path.join(ap.DET, "УКП.03.001 Ползун (APM).m3d")
DST = os.path.join(ap.DET, "УКП.03.001 Ползун облегчённый (APM).m3d")
Y_TOP, Y_BELL, R_HEAD, R_ROD, R_FIL = -80.0, -97.0, 20.0, 4.0, 3.0
assert not os.path.exists(DST), "копия уже есть"
shutil.copy2(SRC, DST)
d = app.Documents.Open(DST, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
m0 = qi(top, A7.IMassInertiaParam7).Mass

# 1) колокол: вырез вращением вокруг оси y — кольцевой клин между конусом (Ø40 при y −97 → Ø8 при y −80) и прежней головкой
sk = p5.NewEntity(C3.o3d_sketch)
sd = sk.GetDefinition()
sd.SetPlane(p5.GetDefaultEntity(C3.o3d_planeXOY))
sk.Create()
s2 = Sketch2D(sd.BeginEdit())
s2.poly_fixed([(R_ROD, Y_TOP), (R_HEAD + 1.0, Y_TOP), (R_HEAD + 1.0, Y_BELL), (R_HEAD, Y_BELL)])
s2.axis(0.0, Y_TOP + 5.0, 0.0, Y_BELL - 5.0)
sd.EndEdit()
cut = p5.NewEntity(C3.o3d_cutRotated)
cd = cut.GetDefinition()
cd.directionType = C3.dtNormal
cd.SetSideParam(True, 360)
cd.SetSketch(sk)
assert cut.Create(), "колокол не вырезан"
sk.hidden = True
sk.Update()


# 2) скругления R3: рёбра шток–головка (y −80) и шток–блок (y −20), точки на ребре вне плоскости эскиза (z = 4)
def edge_at(x, y, z):
    objs = [qi(o, A7.IModelObject) for o in (top.FindObjectsByPoint(x, y, z, True) or ())]
    es = [o for o in objs if o.ModelObjectType == C3.o3d_edge]
    assert len(es) == 1, ((x, y, z), len(es))
    return A5.ksEntity(k5.TransferInterface(es[0], C.ksAPI5Auto, 0))


fil = p5.NewEntity(C3.o3d_fillet)
fd = fil.GetDefinition()
fd.radius = R_FIL
fd.tangent = True
arr = fd.array()
for y in (Y_TOP, -20.0):
    arr.Add(edge_at(0.0, y, R_ROD))
assert fil.Create(), "скругления не построены"
p5.Update()
m1 = qi(top, A7.IMassInertiaParam7).Mass
print(f"масса {m1:.1f} г (было {m0:.1f} г)")
d.Save()
print("сохранено:", DST, os.path.getsize(DST) // 1024, "КБ")
ap.picture(DST, os.path.join(ap.PIC, "ползун_3_новый.png"), ap.VIEW["polzun"])
