# -*- coding: utf-8 -*-
"""Рабочая направляющая УКП.00.002: грань под закрепление для APM FEM (просьба пользователя 16.11 — «ещё одну грань снизу
для теста с закреплением»). Нижняя грань пластины (y = Y_BOT, z −6…0 — ею направляющая стоит на нижней грани выемки
стойки) лежит в одной плоскости с низом кронштейнов (z 0…26) и сливалась с ним в одну грань; линия разъёма по плоскости
z = 0 отделяет её. Сборка и направляющая в КОМПАСе должны быть закрыты; после — пересобрать или проверить сборку.
    python guide_fix_zone.py"""
import os
from kompas_build import A5, A7, C, C3, E, FILES, GD_CH, GD_PL_T, GD_X0, GD_X1, PARTS_DIR, Y_BOT, app, k5, qi

PATH = os.path.join(PARTS_DIR, FILES["guide"])
NAME = "Пластина: нижняя грань (закрепление)"
for i in range(app.Documents.Count):
    x = app.Documents.Item(i)
    assert x is None or os.path.normcase(qi(x, A7.IKompasDocument).PathName) != os.path.normcase(PATH), "направляющая открыта — закройте"
d = app.Documents.Open(PATH, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
sls = qi(top, A7.IAuxiliaryGeomContainer).SplitLines
assert NAME not in [sls.Item(i).Name for i in range(sls.Count)], "грань под закрепление уже отделена"
m0 = qi(top, A7.IMassInertiaParam7).Mass


def face_at(x, y, z):
    fs = [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
    assert len(fs) == 1, ((x, y, z), len(fs))
    return fs[0]


area = lambda f: qi(f, A7.IFace).GetArea(1)
a_before = area(face_at(E, Y_BOT, -GD_PL_T / 2))
sl = sls.Add()
sl.CutObjects = [qi(k5.TransferInterface(p5.GetDefaultEntity(C3.o3d_planeXOY), C.ksAPI7Dual, 0), A7.IModelObject)]
sl.Faces = [face_at(E, Y_BOT, -GD_PL_T / 2)]
assert sl.Update() and sl.Valid, "линия разъёма не построена"
sl.Name = NAME
sl.Update()
plate, brackets = face_at(E, Y_BOT, -GD_PL_T / 2), face_at(GD_X0 + 3, Y_BOT, 10.0)
assert str(plate.Reference) != str(brackets.Reference), "грань не разделилась"
a0 = (GD_X1 - GD_X0 - 2 * GD_CH) * GD_PL_T       # 41 × 6: по краям — фаски углов пластины
a = area(plate)
assert abs(a - a0) < 0.5, (a, a0)
bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
assert not bad, bad
assert abs(qi(top, A7.IMassInertiaParam7).Mass - m0) < 0.01
print(f"грань под закрепление: {a:.1f} мм² ({GD_X1 - GD_X0 - 2 * GD_CH:g} × {GD_PL_T:g}); была общая грань {a_before:.1f} мм²; "
      f"масса {m0:.1f} г без изменений")
d5.SaveAs(PATH)
d.Close(0)
print("сохранено:", PATH)
