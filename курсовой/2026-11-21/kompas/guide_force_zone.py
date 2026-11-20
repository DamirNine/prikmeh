# -*- coding: utf-8 -*-
"""Рабочая направляющая УКП.00.002: разметка под силу для APM FEM (просьба пользователя 16.11 — «просто добавь разметку
под силу, под закрепление не надо»). На внутренней грани правой планки (x = e + 12,5) линиями разъёма отделена зона
контакта с бруском ползуна при φу: y = yD(φу) ± 20, z 26…42 (брусок 40 × 16) — на неё ставится сила R30N = 1671 Н (+x).
Те же три линии, что в apm/«Направляющая 2 (APM)» 15.11; грани пластины под закрепление не делятся.
Сборка должна быть закрыта; после — открыть сборку и проверить сопряжения.
    python guide_force_zone.py"""
import os
from kompas_build import A5, A7, C, C3, E, FILES, GD_Z0, PARTS_DIR, PH_Y, app, k5, qi, yD

PATH = os.path.join(PARTS_DIR, FILES["guide"])
for i in range(app.Documents.Count):
    x = app.Documents.Item(i)
    assert x is None or os.path.normcase(qi(x, A7.IKompasDocument).PathName) != os.path.normcase(PATH), "направляющая открыта — закройте"
X_IN = E + 12.5                                   # внутренняя грань правой планки (к ползуну)
Y0, Y1, Z1 = yD(PH_Y) - 20, yD(PH_Y) + 20, GD_Z0 + 16
ZC = (X_IN, (Y0 + Y1) / 2, (GD_Z0 + Z1) / 2)      # середина зоны контакта

d = app.Documents.Open(PATH, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
assert qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Count == 0, "линии разъёма уже есть"
m0 = qi(top, A7.IMassInertiaParam7).Mass


def face_at(x, y, z):
    fs = [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
    assert len(fs) == 1, ((x, y, z), len(fs))
    return fs[0]


def plane(base, offset):
    pl = p5.NewEntity(C3.o3d_planeOffset)
    pd = pl.GetDefinition()
    pd.SetPlane(p5.GetDefaultEntity(base))
    pd.offset, pd.direction = abs(offset), offset > 0
    pl.hidden = True
    pl.Create()
    return qi(k5.TransferInterface(pl, C.ksAPI7Dual, 0), A7.IModelObject)


for name, cut in (("Зона ползуна: низ", plane(C3.o3d_planeXOZ, Y0)), ("Зона ползуна: верх", plane(C3.o3d_planeXOZ, Y1)),
                  ("Зона ползуна: перед", plane(C3.o3d_planeXOY, Z1))):
    sl = qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Add()
    sl.CutObjects = [cut]
    sl.Faces = [face_at(*ZC)]
    assert sl.Update() and sl.Valid, ("линия разъёма не построена", name)
    sl.Name = name
    sl.Update()
a = qi(face_at(*ZC), A7.IFace).GetArea(1)
assert abs(a - 40 * 16) < 0.5, a              # площадь КОМПАС считает с погрешностью ~0,1 мм²
bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
assert not bad, bad
m1 = qi(top, A7.IMassInertiaParam7).Mass
assert abs(m1 - m0) < 0.01, (m0, m1)
print(f"зона под силу: {a:.1f} мм² (40 × 16) на x = {X_IN:.2f}, y {Y0:.2f}…{Y1:.2f}, z {GD_Z0:g}…{Z1:g}; масса {m1:.1f} г (без изменений)")
d5.SaveAs(PATH)                                   # IKompasDocument.Save() у открытой детали иногда молча не сохраняет
d.Close(0)
print("сохранено:", PATH)
