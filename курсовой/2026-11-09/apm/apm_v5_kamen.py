# -*- coding: utf-8 -*-
"""Камень закрытый: копия «Камень (APM)» (с закреплением и силой APM FEM) + доработки по первому расчёту
(SVM max 646 МПа во внутреннем углу нижняя стенка–перемычка: стенка 4 мм работает консолью от перемычки):
  — сплошная задняя стенка 2,5 мм за полосой (z −15,5…−13) от x = −4 до 10: стенки обоймы опираются с двух сторон.
    У оси O (x < −4) остаются только губки — там ступица кулисы (при φк задняя стенка начинается в 9,58 мм от O, ступица R8);
  — скругления R1,5 во внутренних углах перемычка–стенки и стенки–задняя стенка (до углов полосы остаётся ≈ 0,09 мм).
Грани закрепления (отверстие) и силы (внутренняя грань нижней стенки, y = −9,5, z −13…−4) не меняются.
    python apm_v5_kamen.py"""
import os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
from kompas_build import A5, A7, C, C3, Sketch2D, app, k5, qi
import apm_prep as ap

SRC = os.path.join(ap.DET, "УКП.02.001 Камень (APM).m3d")
DST = os.path.join(ap.DET, "УКП.02.001 Камень закрытый (APM).m3d")
R_FIL = 1.5
assert not os.path.exists(DST), "копия уже есть"
shutil.copy2(SRC, DST)
d = app.Documents.Open(DST, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
m0 = qi(top, A7.IMassInertiaParam7).Mass

# задняя стенка: прямоугольник x −4…10, y −6,8…6,8 (между губками) на плоскости z = −15,5, выдавливание на 2,5 к +z
pl = p5.NewEntity(C3.o3d_planeOffset)
pd = pl.GetDefinition()
pd.SetPlane(p5.GetDefaultEntity(C3.o3d_planeXOY))
pd.offset, pd.direction = 15.5, False
pl.hidden = True
pl.Create()
sk = p5.NewEntity(C3.o3d_sketch)
sd = sk.GetDefinition()
sd.SetPlane(pl)
sk.Create()
Sketch2D(sd.BeginEdit()).rect(-4.0, -6.8, 10.0, 6.8)
sd.EndEdit()
ex = p5.NewEntity(C3.o3d_bossExtrusion)
ed = ex.GetDefinition()
ed.directionType = C3.dtNormal
ed.SetSideParam(True, C3.etBlind, 2.5, 0, False)
ed.SetSketch(sk)
assert ex.Create(), "задняя стенка не построена"
sk.hidden = True
sk.Update()
front = [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(3.0, 0.0, -13.0, True) or ()))
         if o.ModelObjectType == C3.o3d_face]
assert len(front) == 1, "нет передней грани задней стенки на z = −13"


def edge_at(x, y, zz):
    objs = [qi(o, A7.IModelObject) for o in (top.FindObjectsByPoint(x, y, zz, True) or ())]
    es = [o for o in objs if o.ModelObjectType == C3.o3d_edge]
    lens = {round(qi(e, A7.IEdge).GetLength(1), 4) for e in es}
    assert es and len(lens) == 1, ((x, y, zz), len(es), lens)
    return A5.ksEntity(k5.TransferInterface(es[0], C.ksAPI5Auto, 0))


fil = p5.NewEntity(C3.o3d_fillet)
fd = fil.GetDefinition()
fd.radius, fd.tangent = R_FIL, True
arr = fd.array()
for y in (-9.5, 9.5):
    arr.Add(edge_at(0.0, y, -4.0))                        # перемычка–стенка
    arr.Add(edge_at(5.0, y, -13.0))                       # стенка–задняя стенка (губки)
assert fil.Create(), "скругления не построены"
p5.Update()
m1 = qi(top, A7.IMassInertiaParam7).Mass
print(f"масса {m1:.1f} г (было {m0:.1f} г)")
d.Save()
print("сохранено:", DST, os.path.getsize(DST) // 1024, "КБ")
ap.picture(DST, os.path.join(ap.PIC, "камень_3_новый.png"))
