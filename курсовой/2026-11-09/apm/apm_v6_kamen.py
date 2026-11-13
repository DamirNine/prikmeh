# -*- coding: utf-8 -*-
"""Камень закрытый 2: копия «Камень закрытый (APM)» (сила APM FEM сохраняется) +
  — фаски 0,5 × 45° на обоих краях отверстия Ø10 (заход для запрессовки пальца);
  — стенка отверстия разделена плоскостью XZ (y = 0) на верхнюю (+Y) и нижнюю половины. Полоса тянет камень вниз (−Y),
    палец держит его, опираясь на ВЕРХНЮЮ половину отверстия, — в APM закрепляется только она (раньше отверстие было
    закреплено целиком, и жёсткая нижняя половина давала ложный пик 338 МПа у нижнего края).
    python apm_v6_kamen.py"""
import os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
from kompas_build import A5, A7, C, C3, app, k5, qi
import apm_prep as ap

SRC = os.path.join(ap.DET, "УКП.02.001 Камень закрытый (APM).m3d")
DST = os.path.join(ap.DET, "УКП.02.001 Камень закрытый 2 (APM).m3d")
assert not os.path.exists(DST), "копия уже есть"
shutil.copy2(SRC, DST)
d = app.Documents.Open(DST, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart


def found(x, y, z, kind):
    return [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == kind]


# фаски на кромках отверстия. Задняя (z = −4) — операцией «Фаска»; передняя (z = 0) операцией «Фаска» не строится
# (Create возвращает True, но грани нет, элемент с ошибкой) — поэтому вырезом вращения треугольника 0,5 × 0,5
ch = p5.NewEntity(C3.o3d_chamfer)
cd = ch.GetDefinition()
cd.SetChamferParam(True, 0.5, 0.5)
arr = cd.array()
es = found(0.0, 5.0, -4.0, C3.o3d_edge)
assert len({round(qi(e, A7.IEdge).GetLength(1), 4) for e in es}) == 1, len(es)
arr.Add(A5.ksEntity(k5.TransferInterface(es[0], C.ksAPI5Auto, 0)))
assert ch.Create(), "задняя фаска не построена"
from kompas_build import Sketch2D
sk = p5.NewEntity(C3.o3d_sketch)
sd = sk.GetDefinition()
sd.SetPlane(p5.GetDefaultEntity(C3.o3d_planeXOZ))
sk.Create()
s2 = Sketch2D(sd.BeginEdit())
s2.poly_fixed([(5.0, -0.1), (5.6, -0.1), (5.6, 0.0), (5.5, 0.0), (5.0, 0.5)])   # (u, v) = (r, −z)
s2.axis(0.0, 2.0, 0.0, -2.0)
sd.EndEdit()
cut = p5.NewEntity(C3.o3d_cutRotated)
cdr = cut.GetDefinition()
cdr.directionType = C3.dtNormal
cdr.SetSideParam(True, 360)
cdr.SetSketch(sk)
assert cut.Create(), "передняя фаска не вырезана"
sk.hidden = True
sk.Update()
assert found(0.0, 5.25, -0.25, C3.o3d_face) and found(0.0, 5.25, -3.75, C3.o3d_face), "фаски не на месте"

# стенка отверстия: разделить плоскостью XZ
hole = found(0.0, 5.0, -2.0, C3.o3d_face)
assert len(hole) == 1
sl = qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Add()
sl.CutObjects = [qi(top, A7.IPart7).DefaultObject(C3.o3d_planeXOZ)]
sl.Faces = hole
assert sl.Update() and sl.Valid, "линия разъёма отверстия не построена"
sl.Name = "Отверстие: верх (+Y) — опора на палец"
sl.Update()
up, low = found(0.0, 5.0, -2.0, C3.o3d_face), found(0.0, -5.0, -2.0, C3.o3d_face)
assert len(up) == len(low) == 1 and str(up[0].Reference) != str(low[0].Reference), "половины отверстия не разделились"
p5.Update()
print(f"масса {qi(top, A7.IMassInertiaParam7).Mass:.2f} г")
d.Save()
print("сохранено:", DST, os.path.getsize(DST) // 1024, "КБ")
ap.picture(DST, os.path.join(ap.PIC, "камень_3_новый_2.png"), dpi=600)
