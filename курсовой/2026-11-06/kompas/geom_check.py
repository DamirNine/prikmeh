# -*- coding: utf-8 -*-
"""Проверка соударений деталей сборки УКП.00.000 по их геометрии (те же размеры и положения, что в kompas_build.py и
kompas_assembly.py) на всём рабочем ходе
φк…φн: каждая деталь — набор выпуклых призм (контур в плоскости xy × интервал по z); две призмы соударяются, если пересекаются
интервалы z и контуры перекрываются глубже 0,01 мм (теорема о разделяющей оси). Посадки «вал в отверстии» (ось O в кулисе,
палец D в ползуне) не проверяются. Касание упоров в крайних положениях — глубина 0. Кожух — в закрытом положении."""
import json, os
from math import radians, tan, cos, sin, pi
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RJ = json.load(open(os.path.join(HERE, "..", "..", "2026-11-04", "calc_v21.json"), encoding="utf-8"))
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
    "Стойка: основание": [(box(-49.75, 78.25, -345.25, -325.25), -46, 46)],
    "Стойка: лист": [(box(-31.75, 60.25, -325.25, 64.75), -46, -34)],
    "Стойка: ось O": [(circ(0, 0, 5), -34, -13.5)],
    "Стойка: направляющая": [(box(E - 18.5, E - 12.5, Y_BOT, Y_TOP), -8, 8), (box(E + 12.5, E + 18.5, Y_BOT, Y_TOP), -8, 8),
                     (box(E - 18.5, E - 12.5, Y_BOT, Y_BOT + 12), -34, -8), (box(E + 12.5, E + 18.5, Y_BOT, Y_BOT + 12), -34, -8)],
    "Стойка: упор нижний": [([(31, -5), (42, -5), (42, lo_y(42)), (31, lo_y(31))], -34, -13.5)],
    "Стойка: упор верхний": [([(15, hi_y(15)), (21, hi_y(21)), (21, 60), (15, 60)], -34, -13.5)],
}


def clip(poly, a, b):
    """часть выпуклого многоугольника, где a·P ≤ b"""
    out = []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        fp, fq = a[0] * p[0] + a[1] * p[1] - b, a[0] * q[0] + a[1] * q[1] - b
        if fp <= 0:
            out.append(p)
        if fp * fq < 0:
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


# кожух в закрытом положении: стенки 2 мм, задняя кромка на стойке (z = −34), передняя стенка z 10…12; паз под кулису —
# между нижним ребром кулисы при φк и верхним при φн с зазором 1 мм, z −34…−12,5; паз под шток в дне — x e ± 6, z −34…6
nk, nn = (-sin(radians(PH_K)), cos(radians(PH_K))), (-sin(radians(PH_N)), cos(radians(PH_N)))
CX0, CX1, CY0, CY1 = -17.0, 45.5, -53.0, 64.0
outside_slot = lambda r: [q for q in (clip(r, nk, -10.0), clip(r, (-nn[0], -nn[1]), -10.0)) if len(q) >= 3]
r_right, r_top = box(CX1 - 2, CX1, CY0, CY1), box(CX0, CX1, CY1 - 2, CY1)
FIXED.update({
    "Кожух: передняя стенка": [(box(CX0, CX1, CY0, CY1), 10, 12)],
    "Кожух: левая стенка": [(box(CX0, CX0 + 2, CY0, CY1), -34, 12)],
    "Кожух: правая стенка": [(r_right, -12.5, 12)] + [(q, -34, -12.5) for q in outside_slot(r_right)],
    "Кожух: верхняя стенка": [(r_top, -12.5, 12)] + [(q, -34, -12.5) for q in outside_slot(r_top)],
    "Кожух: дно": [(box(CX0, E - 6, CY0, CY0 + 2), -34, 12), (box(E + 6, CX1, CY0, CY0 + 2), -34, 12),
                   (box(E - 6, E + 6, CY0, CY0 + 2), 6, 12)],
    # бутылка: корпус с плечом — призма по диаметру (с запасом), шейка с венчиком до верха 226,5 над основанием
    "Бутылка": [(box(E - 30.2, E + 30.2, -325.25, -157.25), -30.2, 30.2), (box(E - 13.3, E + 13.3, -157.25, -98.75), -13.3, 13.3)],
})
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
