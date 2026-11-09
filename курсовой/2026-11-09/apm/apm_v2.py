# -*- coding: utf-8 -*-
"""Новые (доработанные по результатам APM FEM) детали для второго расчёта — в apm/Детали, картинки «…_3_новая.png».
Деталь сборки не меняется, пока пользователь не решит её заменить.

Кулиса: по первому расчёту (SVM max 92,6 МПа при [σ] = 98) красное — кромки полосы за камнем, где ходит камень (3,6…34,7 мм от
оси O) и стоят упоры стойки — там размеры полосы менять нельзя; синее — средняя линия полосы (нейтральная ось) и конец
рукояти. Облегчение: 8 продолговатых пазов 30 × 8 (R4) по средней линии с шагом 40 мм, x = 125…435, сквозь толщину 8.
Оценка: над пазом W = 8·(18³ − 8³)/12/9 = 394 мм³ вместо 432 — при x = 125 кромка ≈ 93·375/473·432/394 ≈ 81 МПа.
    python apm_v2.py kulisa"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
from kompas_build import ST3, Part
import apm_prep as ap

SLOTS = [(125.0 + 40.0 * k, 155.0 + 40.0 * k) for k in range(8)]   # (x0, x1) пазов, ширина 8 (R4)


def slot(x0, x1, r=4.0):
    """продолговатый паз по средней линии: отрезки и дуги R4 (контур с закреплёнными точками — эскиз определён)"""
    return [(x1 - r, -r), (x1 - r, r, x1 - r, 0.0, r, 1), (x0 + r, r), (x0 + r, -r, x0 + r, 0.0, r, 1)]


def kulisa_v2():
    L, R_ = 500.0, 9.0                                     # как в kompas_build.build(): полоса 8 × 18 × 500 + ступица Ø16 × 12
    p = Part("Кулиса", "УКП.01.001", ST3, "#2d3540")
    p.box(0, L - R_, -R_, R_, 0, 8.0)
    p.extrude(p.sketch(0, lambda s: (s.circle(0, 0, R_), s.circle(L - R_, 0, R_))), 8.0)
    p.cyl(0, 0, 8.0, -12.0, 0, r_in=5.0)
    p.hole(0, 0, 5.0)
    p.extrude(p.sketch(0, lambda s: [s.contour(slot(x0, x1)) for x0, x1 in SLOTS]), 0, cut=True, both=True)   # пазы
    path = os.path.join(ap.DET, "УКП.01.001 Кулиса облегчённая (APM).m3d")
    path, mass = p.save(path)
    ap.split_kulisa(path)                                  # та же зона контакта с камнем, что у исходной копии
    ap.prettify(path)
    ap.picture(path, os.path.join(ap.PIC, "кулиса_3_новая.png"))
    print(f"  новая кулиса: масса {mass:.1f} г (было 577,6 г), {path}")


if __name__ == "__main__":
    {"kulisa": kulisa_v2}[sys.argv[1]]()
