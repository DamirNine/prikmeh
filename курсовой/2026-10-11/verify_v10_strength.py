# -*- coding: utf-8 -*-
"""Независимая проверка раздела 12: местный изгиб стенки паза — МКЭ (балочные элементы Эрмита), прочие величины — формулами
вручную; сверка со strength_v10.json и с текстом docx."""
import json, sys, re
import numpy as np
from math import pi, cos, sin, radians as rad
from docx import Document

S = json.load(open(sys.argv[1], encoding="utf-8"))
doc = Document(sys.argv[2])
norm = lambda t: re.sub(r"\s+", " ", t.replace(" ", " ")).strip()
FULL = " ¦ ".join([norm(p.text) for p in doc.paragraphs] + [norm(c.text) for t in doc.tables for r in t.rows for c in r.cells])
f = lambda x, d=1: f"{x:.{d}f}".replace(".", ",").replace("-", "−")
bad = []
def chk(name, got, exp, tol):
    ok = abs(got - exp) <= tol
    print(f"{'OK ' if ok else 'ERR'} {name}: расчёт {got:.4g}, независимо {exp:.4g}")
    if not ok: bad.append(name)
def has(s):
    if norm(s) not in FULL:
        bad.append("нет в тексте: " + s); print("ERR нет в тексте:", s)

# --- МКЭ: балка с заделками, равномерная нагрузка на участке
def fe_fixed(span, x0, x1, P, n=400):
    EI = 1.0; le = span / n; K = np.zeros((2 * n + 2,) * 2); F = np.zeros(2 * n + 2)
    k = EI / le ** 3 * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le ** 2, -6 * le, 2 * le ** 2],
                                 [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le ** 2, -6 * le, 4 * le ** 2]])
    q = P / (x1 - x0)
    for e in range(n):
        a, b_ = e * le, (e + 1) * le
        ov = max(0.0, min(b_, x1) - max(a, x0))                  # перекрытие нагрузки с элементом
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
        if ov > 0:                                                # эквивалентные узловые силы (частичная нагрузка — точно через квадратуру)
            xs = np.linspace(max(a, x0), min(b_, x1), 41); xi = (xs - a) / le
            N1 = 1 - 3 * xi ** 2 + 2 * xi ** 3; N2 = le * (xi - 2 * xi ** 2 + xi ** 3); N3 = 3 * xi ** 2 - 2 * xi ** 3; N4 = le * (-xi ** 2 + xi ** 3)
            for j, Nj in zip(idx, (N1, N2, N3, N4)):
                F[j] -= q * np.trapezoid(Nj, xs)
    free = np.arange(2, 2 * n)                                    # заделки: v = θ = 0 на обоих концах
    u = np.zeros(2 * n + 2); u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    Ms = []
    for e in range(n):                                            # момент на концах элементов
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]; ue = u[idx]
        for xi in (0.0, 1.0):
            B = EI / le ** 2 * np.array([-6 + 12 * xi, le * (-4 + 6 * xi), 6 - 12 * xi, le * (-2 + 6 * xi)])
            Ms.append(B @ ue)
    return float(np.max(np.abs(Ms)))

lay, A, B = S["lay"], S["A"], S["B"]; span = S["span"]; ls = S["stone"]["ls"]
for nm, pos, sec in (("φу", A, S["secA"]), ("φк", B, S["secB"])):
    c = pos["lOD"] - lay["a1"]
    chk(f"M_мест {nm}, Н·мм", sec["Mloc"], fe_fixed(span, c - ls / 2, c + ls / 2, pos["R12N"]), 15.0)
# --- остальное — формулами
e, L = 12.53, 500.0; b, w, H = S["b"], S["w"], S["H"]
for nm, pos in (("φу", A), ("φк", B)):
    p = rad(pos["phi"])
    chk(f"|M_D| {nm}, Н·м", abs(pos["M_D"]) / 1000, pos["P"] * (L * cos(p) - e) / 1000, 1e-3)
    chk(f"|Q_OD| {nm}, Н", abs(pos["Q_OD"]), pos["F"] / cos(p) - pos["P"] * cos(p), 1e-6)
W = b * (H ** 3 - w ** 3) / (6 * H); Ar = b * (H - w)
chk("W(А–А), мм³", S["secA"]["W"], W, 1e-6)
chk("σ при φу, МПа", S["secA"]["sig"], abs(A["N"]) / Ar + abs(A["M_D"]) / W + 6 * S["secA"]["Mloc"] / (b * ((H - w) / 2) ** 2), 1e-6)
chk("σ пальца D, МПа", S["pinD"]["sig"], A["R23"] * 6 / (0.1 * 12 ** 3), 1e-6)
chk("σ оси O, МПа", S["axO"]["sig2"], A["R10"] * 22 / (0.1 * 16 ** 3), 1e-6)
area = pi * 18 ** 2 / 2 + 36 * lay["a2"] - span * w + (36 + 16) / 2 * 100 + (L - lay["a2"] - 100) * 16
chk("m планки, кг (по формулам площадей)", S["mass"]["m_plate"], 7850e-9 * 10 * area, 0.003)
zt = lay["a2"] + 100
J = (16 * (L ** 3 - zt ** 3) / 3 + 16 ** 3 / 12 * (L - zt)
     + (lambda c0, c1: c0 * (zt ** 3 - lay["a2"] ** 3) / 3 - c1 * (zt ** 4 - lay["a2"] ** 4) / 4)(36 + 0.2 * lay["a2"], 0.2))
chk("J_O планки (рукоять + переход), кг·м² (нижняя оценка)", S["mass"]["JO1"], 7850e-9 * 10 * J * 1e-6, 0.0006)
chk("компоновка: e_треб, мм", lay["e_req1"], (9 + 1 + 9) * cos(rad(22.7205)), 0.01)
# --- числа в тексте
has("σ = 91,6 МПа при φу и 73,8 МПа при φк"); has("H = 32 мм (Ra10) не проходит — 144,7 МПа > [σ]")
has("палец D Ø12 мм (ряд Ra10)"); has("dO ≥ 15,6 мм → 16 мм (Ra5), ступица Ø32 × 16 мм")
has("перекрывает бобышку на 4,4 мм"); has("e ≥ 19·cos 22,72° = 17,5 мм")
print("\nИТОГ:", "ошибок нет" if not bad else bad)
