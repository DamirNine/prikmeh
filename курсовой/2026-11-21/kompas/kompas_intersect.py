# -*- coding: utf-8 -*-
"""Проверка пересечений тел компонентов сборки средствами КОМПАСа (IBody7.CheckIntersectionWithBody) в нескольких
положениях кулисы — весь ход φк…φн через 1°. Посадки «вал в отверстии» и запрессовки (ось O — кулиса, палец — камень/ползун/шайба/гайка,
пластина направляющей — выемка стойки) дают касание, поэтому касания не считаются; ищутся только пересечения объёмов.
Сборка открывается и закрывается без сохранения.
    python kompas_intersect.py"""
import os
from itertools import combinations
from kompas_build import A7, C3, PH_K, PH_N, PH_Y, app, qi

ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "УКП.00.000-01 Укупориватель (направляющая без планок).a3d"
                   if os.environ.get("UKP_VAR") == "B" else "УКП.00.000 Укупориватель.a3d")      # 21.11: вариант B
doc = qi(app.Documents.Open(ASM, True, False), A7.IKompasDocument3D)
top = doc.TopPart
parts = [qi(top.Parts.Part(i), A7.IPart7) for i in range(top.Parts.Count)]


def bodies(p):
    b = qi(p, A7.IFeature7).ResultBodies
    if b is None:
        return []
    return [qi(x, A7.IBody7) for x in (b if isinstance(b, tuple) else (b,))]


mates = top.MateConstraints
ang = next(qi(mates.MateConstraint3D(i), A7.IMateConstraint3D) for i in range(mates.Count)
           if qi(mates.MateConstraint3D(i), A7.IMateConstraint3D).ConstraintType == C3.mc_Angle)
itv = qi(ang, A7.IMateInterval)
itv.UseInterval = False
found = {}
PHS = sorted({PH_K, PH_Y, PH_N, *range(23, 60)})   # весь ход через 1° + φк, φу, φн (точно: на округлённом 22,72 кулиса на 0,0005° заходит в упор)
for ph in PHS:
    ang.ParamValue = ph; ang.Update(); top.RebuildModel(True)
    B = {p.Name: bodies(p) for p in parts}
    for a, b in combinations(B, 2):
        for ba in B[a]:
            for bb in B[b]:
                if ba.CheckIntersectionWithBody(bb, False):
                    found.setdefault(f"{a} — {b}", []).append(ph)
    print(f"φ = {ph:6.2f}°: пересечений {sum(1 for v in found.values() if ph in v)}")
print("компоненты:", ", ".join(p.Name for p in parts))
print("Пересечения:", found or "нет")
doc.Close(0)                                      # без сохранения
