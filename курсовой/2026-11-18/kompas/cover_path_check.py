# -*- coding: utf-8 -*-
"""Проверка пересечений кожуха с остальными деталями на всём пути надевания (сдвиг 0…120 мм через 5 мм) при трёх углах
кулисы φк, середина, φн (IBody7.CheckIntersectionWithBody). Сборка закрывается без сохранения.
Язычки защёлок в конце хода отгибаются (упруго наезжают на зацепы) — модель их не гнёт, поэтому пересечение язычка с зацепом
на последних мм хода ожидаемо и выводится отдельно.
    python cover_path_check.py"""
import os
from kompas_build import A7, C3, PH_K, PH_N, app, qi

ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "УКП.00.000 Укупориватель.a3d")
doc = qi(app.Documents.Open(ASM, True, False), A7.IKompasDocument3D)
top = doc.TopPart
parts = [qi(top.Parts.Part(i), A7.IPart7) for i in range(top.Parts.Count)]
bodies = lambda p: [qi(x, A7.IBody7) for x in (lambda b: () if b is None else (b if isinstance(b, tuple) else (b,)))(qi(p, A7.IFeature7).ResultBodies)]
mates = top.MateConstraints
ms = [qi(mates.MateConstraint3D(i), A7.IMateConstraint3D) for i in range(mates.Count)]
ang = next(m for m in ms if m.ConstraintType == C3.mc_Angle)
cov = next(m for m in ms if m.ConstraintType == C3.mc_Distance and qi(m, A7.IMateInterval).UseInterval and qi(m, A7.IMateInterval).MaxValue > 100)
for m in (ang, cov):
    qi(m, A7.IMateInterval).UseInterval = False
cover = next(p for p in parts if p.Name.startswith("Кожух"))
found = {}
for ph in (PH_K, (PH_K + PH_N) / 2, PH_N):
    ang.ParamValue = ph; ang.Update()
    for dz in range(0, 125, 5):
        cov.ParamValue = float(dz); cov.Update(); top.RebuildModel(True)
        for p in parts:
            if p is cover:
                continue
            if any(a.CheckIntersectionWithBody(b, False) for a in bodies(cover) for b in bodies(p)):
                found.setdefault(p.Name, []).append((round(ph, 1), dz))
    print(f"φ = {ph:5.2f}°: сдвиг 0…120 проверен")
print("Пересечения кожуха:", found or "нет")
doc.Close(0)
