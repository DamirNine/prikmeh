# -*- coding: utf-8 -*-
"""Проверка соударений деталей сборки УКП.00.000 по их геометрии (те же размеры и положения, что в kompas_build.py и
kompas_assembly.py) на всём рабочем ходе
φк…φн: каждая деталь — набор выпуклых призм (контур в плоскости xy × интервал по z); две призмы соударяются, если пересекаются
интервалы z и контуры перекрываются глубже 0,01 мм (теорема о разделяющей оси). Посадки «вал в отверстии» (ось O в кулисе,
палец D в ползуне) не проверяются. Касание упоров в крайних положениях — глубина 0."""
import json, os
from math import radians, tan, cos, sin, pi
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RJ = json.load(open(os.path.join(HERE, "..", "calc_v21.json"), encoding="utf-8"))
E, PH_N, PH_K = 12.53, RJ["phi_n"], RJ["phi_k"]
yD = lambda ph: E * tan(radians(ph))
box = lambda x0, x1, y0, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
circ = lambda xc, yc, r, n=48: [(xc + r * cos(2 * pi * k / n), yc + r * sin(2 * pi * k / n)) for k in range(n)]


def stadium(x0, x1, r, n=24):
    th = np.linspace(-pi / 2, pi / 2, n)
    right = [(x1 + r * cos(t), r * sin(t)) for t in th]
    left = [(x0 - r * cos(t), -r * sin(t)) for t in th]
    return right + left


lo_y = lambda x: (x * sin(radians(PH_K)) - 9) / cos(radians(PH_K))      # нижнее ребро кулисы при φк
hi_y = lambda x: (x * sin(radians(PH_N)) + 9) / cos(radians(PH_N))      # верхнее ребро кулисы при φн
Y_BOT, Y_TOP = yD(PH_K) - 55, yD(PH_N) + 26
FIXED = {     # элементы детали «Стойка» в координатах сборки (начало — ось O)
    "Стойка: основание": [(box(-67.5, 132.5, -345.25, -325.25), -56, 104)],
    "Стойка: лист": [(box(-49.5, 42.5, -325.25, 64.75), -46, -34)],
    "Стойка: ось O": [(circ(0, 0, 5), -34, -13.5)],
    "Стойка: направляющая": [(box(E - 18.5, E - 12.5, Y_BOT, Y_TOP), -8, 8), (box(E + 12.5, E + 18.5, Y_BOT, Y_TOP), -8, 8),
                     (box(E - 18.5, E - 12.5, Y_BOT, Y_BOT + 12), -34, -8), (box(E + 12.5, E + 18.5, Y_BOT, Y_BOT + 12), -34, -8)],
    "Стойка: упор нижний": [([(31, -5), (42, -5), (42, lo_y(42)), (31, lo_y(31))], -34, -13.5)],
    "Стойка: упор верхний": [([(15, hi_y(15)), (21, hi_y(21)), (21, 60), (15, 60)], -34, -13.5)],
}
MOVING = {   # (рамка, призмы в локальных координатах)
    "Кулиса": ("O", [(stadium(0, 491, 9), -21.5, -13.5), (circ(0, 0, 8), -33.5, -21.5)]),
    "Камень с пальцем D": ("D", [(box(-10, 10, 9.5, 13.5), -24.5, -9), (box(-10, 10, -13.5, -9.5), -24.5, -9),
                                 (box(-10, 10, -9.5, 9.5), -13, -9), (box(-7, 10, 6.8, 9.5), -24.5, -22),
                                 (box(-7, 10, -9.5, -6.8), -24.5, -22), (circ(0, 0, 5), -9, 8)]),
    "Ползун": ("P", [(box(-12, 12, -20, 20), -8, 8), (box(-4, 4, -80, -20), -4, 4), (box(-20, 20, -104, -80), -20, 20)]),
}
SKIP = {frozenset(p) for p in (("Стойка: ось O", "Кулиса"), ("Камень с пальцем D", "Ползун"))}


def place(frame, poly, ph):
    c, s = cos(radians(ph)), sin(radians(ph))
    if frame == "O":
        return [(x * c - y * s, x * s + y * c) for x, y in poly]
    if frame == "D":
        return [(E + x * c - y * s, yD(ph) + x * s + y * c) for x, y in poly]
    return [(E + x, yD(ph) + y) for x, y in poly]


def depth(p, q):
    """глубина перекрытия выпуклых многоугольников (≤ 0 — не пересекаются)"""
    best = np.inf
    for poly in (p, q):
        P = np.array(poly)
        for i in range(len(P)):
            e = P[(i + 1) % len(P)] - P[i]
            ax = np.array([-e[1], e[0]]); ax /= np.hypot(*ax)
            pa, pb = np.array(p) @ ax, np.array(q) @ ax
            best = min(best, min(pa.max(), pb.max()) - max(pa.min(), pb.min()))
    return best


worst = {}
for ph in np.linspace(PH_K, PH_N, 241):
    bodies = {k: v for k, v in FIXED.items()}
    bodies.update({k: [(place(fr, poly, ph), z0, z1) for poly, z0, z1 in prisms] for k, (fr, prisms) in MOVING.items()})
    names = list(bodies)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            if (n1 in FIXED and n2 in FIXED) or frozenset((n1, n2)) in SKIP:
                continue
            for p1, a0, a1 in bodies[n1]:
                for p2, b0, b1 in bodies[n2]:
                    if min(a1, b1) - max(a0, b0) <= 1e-9:
                        continue
                    d = depth(p1, p2)
                    key = f"{n1} — {n2}"
                    if d > worst.get(key, (-np.inf,))[0]:
                        worst[key] = (d, ph)
hits = {k: v for k, v in worst.items() if v[0] > 0.01}
touch = {k: v for k, v in worst.items() if -0.01 <= v[0] <= 0.01}
print("Проверено положений:", 241, "| пар с общим слоем по z:", len(worst))
print("Соударения:", {k: (round(v[0], 3), round(v[1], 2)) for k, v in hits.items()} or "нет")
print("Касания (|глубина| ≤ 0,01 мм):", {k: round(v[1], 2) for k, v in touch.items()} or "нет")
gaps = sorted(((-v[0], k, v[1]) for k, v in worst.items() if v[0] < -0.01))[:8]
print("Наименьшие зазоры:")
for g, k, ph in gaps:
    print(f"  {k}: {g:.2f} мм при φ = {ph:.2f}°")
json.dump(dict(hits=hits, touch=touch, gaps=gaps), open(os.path.join(HERE, "geom_check.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
