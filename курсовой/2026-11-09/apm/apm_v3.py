# -*- coding: utf-8 -*-
"""Кулиса облегчённая 2: копия файла «Кулиса облегчённая (APM)» (вместе с закреплением и силами APM FEM, привязанными к граням)
+ ещё один паз 30 × 8 (R4) ближе к рукояти, x = 445…475 (перемычка 10 мм, до скруглённого торца 16 мм) — по второму расчёту
конец рукояти почти не нагружен. Грани закрепления (отверстие ступицы) и сил (зона контакта с камнем, торец рукояти) не
меняются — пользователю остаётся перестроить сетку и пересчитать.
    python apm_v3.py"""
import os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
from kompas_build import A5, A7, C, C3, Sketch2D, app, k5, qi
import apm_prep as ap
from apm_v2 import slot

SRC = os.path.join(ap.DET, "УКП.01.001 Кулиса облегчённая (APM).m3d")
DST = os.path.join(ap.DET, "УКП.01.001 Кулиса облегчённая 2 (APM).m3d")
assert not os.path.exists(DST), "копия уже есть"
shutil.copy2(SRC, DST)
d = app.Documents.Open(DST, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
sk = p5.NewEntity(C3.o3d_sketch)
sd = sk.GetDefinition()
sd.SetPlane(p5.GetDefaultEntity(C3.o3d_planeXOY))
sk.Create()
s2 = Sketch2D(sd.BeginEdit())
s2.contour(slot(445.0, 475.0))
sd.EndEdit()
ex = p5.NewEntity(C3.o3d_cutExtrusion)
ed = ex.GetDefinition()
ed.directionType = C3.dtBoth
ed.SetSideParam(True, C3.etThroughAll, 0, 0, False)
ed.SetSideParam(False, C3.etThroughAll, 0, 0, False)
ed.SetSketch(sk)
assert ex.Create(), "паз не вырезан"
sk.hidden = True
sk.Update()
p5.Update()
mi = qi(qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart, A7.IMassInertiaParam7)
print(f"масса {mi.Mass:.1f} г (было 463,9 г)")
d.Save()
print("сохранено:", DST, os.path.getsize(DST) // 1024, "КБ")
ap.picture(DST, os.path.join(ap.PIC, "кулиса_3_новая_2.png"))
