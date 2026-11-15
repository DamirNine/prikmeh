# -*- coding: utf-8 -*-
"""Где останавливается гайка: в мини-сборке гайку «откручивают» винтовым движением (сдвиг dz вдоль оси + поворот на
360°·dz/шаг — фаза витков сохраняется) и проверяют пересечение тел пальца и гайки. Сборка не сохраняется.
    python screw_check.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "2026-11-15", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A7, app, qi
from build_m10 import ASM, P_

doc = qi(app.Documents.Open(ASM, True, False), A7.IKompasDocument3D)
top = doc.TopPart
parts = {qi(top.Parts.Part(i), A7.IPart7).Name: qi(top.Parts.Part(i), A7.IPart7) for i in range(top.Parts.Count)}
pin, nut = parts["Палец D (М10, печать)"], parts["Гайка М10 (печать)"]


def bodies(p):
    b = qi(p, A7.IFeature7).ResultBodies
    return [] if b is None else [qi(x, A7.IBody7) for x in (b if isinstance(b, tuple) else (b,))]


res = []
for dz in [i * 0.25 for i in range(0, 9)]:
    pl = nut.Placement
    pl.SetOrigin(0.0, 0.0, 0.0)
    pl.SetAxes(1, 0, 0, 0, 1, 0) if hasattr(pl, "SetAxes") else None
    nut.UpdatePlacement(False)
    pl = nut.Placement
    pl.SetOrigin(0.0, 0.0, dz)
    pl.Rotate(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 360.0 * dz / P_)   # правая резьба: откручивание — сдвиг вперёд с поворотом
    nut.UpdatePlacement(False)
    top.RebuildModel(True)
    hit = any(a.CheckIntersectionWithBody(b, False) for a in bodies(pin) for b in bodies(nut))
    res.append((dz, hit))
    print(f"  гайка на {dz:4.2f} мм дальше: {'пересекается' if hit else 'свободно'}")
doc.Close(0)
