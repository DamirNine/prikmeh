# -*- coding: utf-8 -*-
"""Проверка путей сборки (шаги «Инструкции» и 3D-анимации): каждая деталь или подсборка вдвигается спереди вдоль оси z
к своему месту, рукоять — в положении φу; на каждом шаге установлены только детали предыдущих шагов. Геометрия — призмы
geom_check.py. Посадки «вал в отверстии» (кулиса на оси O, ползун, шайба, гайка на пальце) не проверяются; пластина
направляющей входит в выемку листа стойки (в призмах выемки нет — пара «направляющая — лист» не проверяется); крючки кожуха
перескакивают через зацепы стойки, отгибаясь (это защёлка — пара не проверяется).
    python path_check.py"""
import contextlib, io
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import geom_check as g

PH = g.RJ["phi_y"]
moving = {k: [(g.place(fr, poly, PH), z0, z1) for poly, z0, z1 in prisms] for k, (fr, prisms) in g.MOVING.items()}
stand = {k: v for k, v in g.FIXED.items() if k.startswith("Стойка")}
guide = {"Направляющая": g.FIXED["Направляющая"]}
cover = {k: v for k, v in g.FIXED.items() if k.startswith("Кожух")}
SKIP = g.SKIP | {frozenset(p) for p in (("Направляющая", "Стойка: лист"), ("Кожух: крючок левый", "Стойка: зацеп левый"),
                                        ("Кожух: крючок правый", "Стойка: зацеп правый"))}


def worst(movers, installed, dz_max):
    """наибольшая глубина перекрытия на пути dz = dz_max…0 (> 0,01 — удар) и где"""
    res = (-np.inf, None, None)
    for dz in np.linspace(dz_max, 0.0, int(dz_max / 0.5) + 1):
        for n1, pr1 in movers.items():
            for n2, pr2 in installed.items():
                if frozenset((n1, n2)) in SKIP:
                    continue
                for p1, a0, a1 in pr1:
                    for p2, b0, b1 in pr2:
                        if min(a1 + dz, b1) - max(a0 + dz, b0) <= 1e-9:
                            continue
                        d = g.depth(p1, p2)
                        if d > res[0]:
                            res = (d, f"{n1} — {n2}", dz)
    return res


sub = {k: moving[k] for k in ("Кулиса", "Камень", "Палец D")}
steps = [("кулиса с камнем и пальцем — на ось O", sub, dict(stand), 150),
         ("направляющая — в выемку стойки", guide, {**stand, **sub}, 150),
         ("ползун — на палец между планками", {"Ползун": moving["Ползун"]}, {**stand, **sub, **guide}, 150),
         ("шайба", {"Шайба": moving["Шайба"]}, {**stand, **sub, **guide, "Ползун": moving["Ползун"]}, 60),
         ("гайка", {"Гайка": moving["Гайка"]}, {**stand, **sub, **guide, "Ползун": moving["Ползун"], "Шайба": moving["Шайба"]}, 60),
         ("кожух", cover, {**stand, **guide, **moving}, 120)]
bad = 0
for title, mv, inst, dzm in steps:
    d, pair, dz = worst(mv, inst, dzm)
    hit = d > 0.01
    bad += hit
    print(f"  {title}: {'УДАР ' + format(d, '.2f') + ' мм — ' + pair + f' (dz = {dz:.1f})' if hit else f'свободно, наименьший зазор {-d:.2f} мм ({pair}, dz = {dz:.1f})'}")
print("Пути сборки:", "без ударов" if not bad else f"ударов: {bad}")
