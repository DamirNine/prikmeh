# -*- coding: utf-8 -*-
"""Вариант 1 крепления ползуна для 3D-печати (16.11): палец D с настоящей резьбой М10 × 1,5 вместо условной М8 × 1,25,
шайба 10 и гайка М10 с настоящей внутренней резьбой; мини-сборка «палец + шайба + гайка» показывает, как они сходятся.
Рабочие детали сборки 15.11 не меняются (это отдельная копия для просмотра и печати).

Палец: Ø10 от заднего торца (в камне) до 23,5 мм — камень 0…4, зазор, ползун 5…21, шайба 21,5…23,5; дальше Ø9,7 до 32 мм
с резьбой; резьба начинается под шайбой (впадина с 23,0 мм), поэтому гайка навинчивается до шайбы. Уступа нет: резьба
не толще отверстия ползуна Ø10, поэтому ползун надевается через неё.
Резьба под печать (FDM): профиль 60°, наружный Ø пальца 9,7, впадина пальца Ø7,9; гайка — отверстие Ø8,78, впадина
Ø10,84: по диаметру зазор 0,3…0,4 мм, по виткам — 0,2 мм. Витки — вырез треугольного профиля по винтовой линии шаг 1,5
(кинематическая операция, sketchShiftType = 1); у пальца и гайки одна и та же винтовая линия (все три детали построены в
системе координат пальца: начало — задний торец, z — ось), поэтому в мини-сборке витки совпадают по фазе.
    python build_m10.py"""
import os, sys
from math import tan, radians, cos
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "2026-11-15", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
import kompas_build as kb
from kompas_build import A5, A7, C, C3, PIN_COLOR, FASTENER, Part, app, k5, qi

kb.PARTS_DIR = HERE                               # детали варианта — в эту папку
PETG = ("PETG (печать)", 1.27)
P_, T30 = 1.5, tan(radians(30))
D_PIN, D_THR = 10.0, 9.7                          # палец: гладкая часть и наружный Ø резьбы
Z_SH, Z_END = 23.5, 32.0                          # конец гладкой части (за шайбой), конец пальца
R_PIN_ROOT = 3.95                                 # впадина пальца (вершина треугольника выреза)
R_NUT_ROOT = R_PIN_ROOT + 0.866 * P_ + 0.2 / (2 * T30)   # впадина гайки: H = 0,866p + осевой зазор 0,2 → 5,42
R_NUT_HOLE = 4.39                                 # отверстие гайки Ø8,78 (D1 = 8,376 + 0,4)
Z_HELIX = Z_SH - 0.5                              # начало винтовой линии пальца (центр первой впадины) — под шайбой,
                                                  # иначе первый виток гайки встаёт на гладкую часть и гайка не доходит до шайбы
WASHER_10 = (10.5, 20.0, 2.0)                     # шайба 10 ГОСТ 11371-78: d1, d2, s
NUT_S, NUT_M = 16.0, 8.0                          # гайка М10 ГОСТ 5915-70: под ключ, высота
Z_NUT0 = Z_SH                                     # гайка 23,5…31,5 (в системе пальца)
FILES = {"pin": "УКП.02.002 Палец D М10 (печать).m3d", "washer": "Шайба 10 (печать).m3d", "nut": "Гайка М10 (печать).m3d"}
ASM = os.path.join(HERE, "Палец М10 с шайбой и гайкой.a3d")


def helix(p, z0, z1, r_path):
    """винтовая линия по оси z от z0 до z1, шаг P_, правая (как у пальца и гайки одинаково)"""
    sp = p.p.NewEntity(C3.o3d_cylindricSpiral)
    sd = sp.GetDefinition()
    sd.SetPlane(p.plane_z(z0))
    sd.SetLocation(0.0, 0.0)
    sd.buildMode = 0
    sd.diam, sd.step, sd.height, sd.turn = 2 * r_path, P_, z1 - z0, (z1 - z0) / P_
    sd.buildDir, sd.turnDir, sd.firstAngle = True, True, 0.0
    assert sp.Create(), "винтовая линия не построена"
    return sp


def thread_cut(p, tri_xz, sp):
    """вырез треугольного профиля (x, z) по винтовой линии"""
    sk = p.sketch(0, lambda s: s.poly_fixed([(x, -z) for x, z in tri_xz]), p.p.GetDefaultEntity(C3.o3d_planeXOZ))
    ce = p.p.NewEntity(C3.o3d_cutEvolution)
    cd = ce.GetDefinition()
    cd.sketchShiftType = 1
    cd.SetSketch(sk)
    cd.PathPartArray().Add(sp)
    assert ce.Create(), "резьба не вырезана"


def build_pin():
    p = Part("Палец D (М10, печать)", "УКП.02.002", PETG, PIN_COLOR)
    r, rt = D_PIN / 2, D_THR / 2
    prof = [(0, 0), (r - 0.5, 0), (r, 0.5), (r, Z_SH), (rt, Z_SH), (rt, Z_END - 1.0), (rt - 1.0, Z_END), (0, Z_END)]
    p.revolve(p.sketch_xz(lambda s: (s.contour([(x, -z) for x, z in prof]), s.axis(0, 5, 0, -Z_END - 5))))
    sp = helix(p, Z_HELIX, Z_END + P_, rt)
    hw = (rt + 0.3 - R_PIN_ROOT) * T30            # полуширина впадины на Ø9,7 + 0,6 (вне материала)
    thread_cut(p, [(R_PIN_ROOT, Z_HELIX), (rt + 0.3, Z_HELIX - hw), (rt + 0.3, Z_HELIX + hw)], sp)
    return p.save(FILES["pin"])[1]


def build_washer():
    d1, d2, s = WASHER_10
    p = Part("Шайба 10 (печать)", "", PETG, FASTENER)
    p.cyl(0, 0, d2 / 2, Z_SH - s, Z_SH, r_in=d1 / 2)              # 21,5…23,5 — между ползуном и гайкой
    return p.save(FILES["washer"])[1]


def build_nut():
    R6 = NUT_S / 2 / cos(radians(30))
    z0, z1 = Z_NUT0, Z_NUT0 + NUT_M
    p = Part("Гайка М10 (печать)", "", PETG, FASTENER)
    p.extrude(p.sketch(z0, lambda s: s.poly_fixed([(R6 * cos(radians(30 + 60 * k)), R6 * kb.sin(radians(30 + 60 * k)))
                                                   for k in range(6)])), NUT_M)
    p.hole(0, 0, R_NUT_HOLE)
    r0, r1 = 0.45 * NUT_S, R6 + 0.5                                   # фаски 30° на углах
    dz = (r1 - r0) * tan(radians(30))
    p.revolve(p.sketch_xz(lambda s: (s.contour([(r0, -z1), (r1, -z1), (r1, -(z1 - dz))]),
                                     s.contour([(r0, -z0), (r1, -(z0 + dz)), (r1, -z0)]),
                                     s.axis(0, -z0 + 2, 0, -z1 - 2))), cut=True)
    # винтовая линия того же шага, сдвинутая на полшага (впадина гайки — против выступа пальца) и начатая до торца
    # гайки; профиль — ровно в начале линии (КОМПАС при sketchShiftType = 1 переносит эскиз в начало траектории)
    zh = Z_HELIX + P_ / 2 - P_
    sp = helix(p, zh, z1 + P_, D_THR / 2)
    r_in = 4.2
    hw = (R_NUT_ROOT - r_in) * T30
    thread_cut(p, [(R_NUT_ROOT, zh), (r_in, zh - hw), (r_in, zh + hw)], sp)
    return p.save(FILES["nut"])[1]


if __name__ == "__main__":
    print("Детали варианта М10:")
    m = {"pin": build_pin(), "washer": build_washer(), "nut": build_nut()}
    # мини-сборка: все три детали в системе координат пальца, закреплены
    doc = qi(app.Documents.Add(C.ksDocumentAssembly, True), A7.IKompasDocument3D)
    top = doc.TopPart
    top.Name, top.Marking = "Палец М10 с шайбой и гайкой (печать)", ""
    for k in ("pin", "washer", "nut"):
        c = top.Parts.AddFromFile(os.path.join(HERE, FILES[k]), True, False)
        c.Fixed = True
        c.Update()
    top.RebuildModel(True)
    doc.SaveAs(ASM)
    print("сборка:", ASM, os.path.exists(ASM), "| массы, г:", {k: round(v, 2) for k, v in m.items()})
