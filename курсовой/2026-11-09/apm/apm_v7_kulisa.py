# -*- coding: utf-8 -*-
"""Кулиса облегчённая 3: копия «Кулиса облегчённая 2 (APM)» (с нагрузками APM FEM) + фаски 0,5 × 45° на четырёх длинных
кромках полосы 8 × 18 — чтобы острые кромки не задевали скругления R1,5 во внутренних углах окна камня (зазор у углов был
0,09 мм, с фасками ≈ 0,44 мм). Нижние кромки разделены линией разъёма зоны контакта с камнем на три участка — берутся все.
Как построено на самом деле (13.11): операция «Фаска» дала скос только на передних кромках (z = 8); на задних (z = 0)
нижняя кромка — по трём кускам линии разъёма отдельными фасками, верхняя — вырезом треугольника 0,5 × 0,5 вдоль x
(эскиз на YOZ, выдавливание «в обе стороны»: прямое 491, обратное 0,01) — операция «Фаска» на ней не строится.
Скрипт целиком не перезапускался: после сбоя КОМПАСа задние кромки доделаны вручную через API.
    python apm_v7_kulisa.py"""
import os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
from kompas_build import A5, A7, C, C3, app, k5, qi
import apm_prep as ap

SRC = os.path.join(ap.DET, "УКП.01.001 Кулиса облегчённая 2 (APM).m3d")
DST = os.path.join(ap.DET, "УКП.01.001 Кулиса облегчённая 3 (APM).m3d")
assert not os.path.exists(DST), "копия уже есть"
shutil.copy2(SRC, DST)
d = app.Documents.Open(DST, True, False)
d.Active = True
p5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0)).GetPart(C3.pTop_Part)
top = qi(d, A7.IKompasDocument3D).TopPart
m0 = qi(top, A7.IMassInertiaParam7).Mass

# на каждой из четырёх длинных кромок — самое длинное ребро (во всю длину полосы, 491 мм); у нижних кромок рядом лежат ещё
# короткие куски от линии разъёма зоны контакта — их не берём
ch = p5.NewEntity(C3.o3d_chamfer)
cd = ch.GetDefinition()
cd.SetChamferParam(True, 0.5, 0.5)
arr = cd.array()
seen = set()
L = lambda o: round(qi(o, A7.IEdge).GetLength(1), 3)
for y in (-9.0, 9.0):
    for z in (0.0, 8.0):
        found = {}
        for x in (3.0, 16.76, 200.0):
            for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())):
                if o.ModelObjectType == C3.o3d_edge:
                    found.setdefault(L(o), o)
        full = [k for k in found if k > 480]
        take = full[:1] if full else sorted(found)             # ребро во всю длину или все куски кромки
        assert full or abs(sum(take) - 491.0) < 0.1, ((y, z), sorted(found))
        for k in take:
            seen.add((y, z, k))
            arr.Add(A5.ksEntity(k5.TransferInterface(found[k], C.ksAPI5Auto, 0)))
print("рёбер под фаску:", len(seen))
assert ch.Create(), "фаски не построены"
qi(d, A7.IKompasDocument3D).RebuildDocument()
feats = [qi(f, A7.IFeature7) for f in (qi(top, A7.IFeature7).SubFeatures(1, False, False) or ())]
bad = [f.Name for f in feats if not f.Valid]
assert not bad, bad
fc = lambda x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
for x in (3.0, 16.76, 200.0):                               # точка на скосе фаски нижней кромки: (y, z) = (−8,75; 0,25)
    assert fc(x, -8.75, 0.25) and fc(x, -8.75, 7.75), ("нет фаски на нижних кромках", x)
assert fc(200.0, 8.75, 0.25) and fc(200.0, 8.75, 7.75), "нет фаски на верхних кромках"
m1 = qi(top, A7.IMassInertiaParam7).Mass
print(f"масса {m1:.1f} г (было {m0:.1f} г)")
d.Save()
print("сохранено:", DST, os.path.getsize(DST) // 1024, "КБ")
ap.picture(DST, os.path.join(ap.PIC, "кулиса_3_новая_3.png"))
