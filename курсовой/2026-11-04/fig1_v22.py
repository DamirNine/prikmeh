# -*- coding: utf-8 -*-
"""Рис. 1 (v22) — расчётная (кинематическая) схема по ЕСКД (ГОСТ 2.770-68, ГОСТ 2.703-2011): звенья — линиями, шарниры —
кружками, камень — прямоугольником на кулисе, ползун (звено 3) — линией в неподвижной направляющей, стойка у оси O —
вертикальной стойкой на основании под прямым углом; крайние положения
механизма (φн, φк) — тонкими штрихпунктирными линиями с двумя точками (ГОСТ 2.303-68); схема без масштаба."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Arc
from matplotlib.transforms import Affine2D
from math import radians, tan, cos, sin

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 11})
INK, INK2, TRI, TRI_E, RED, BLUE = "#0b0b0b", "#52514e", "#f8ddd2", "#e2703a", "#c4372b", "#2a5fa8"
PHANTOM = (0, (9, 2.5, 1.2, 2.5, 1.2, 2.5))                 # штрихпунктирная с двумя точками
MAIN, THIN = 2.4, 0.9

PH_N, PH_K, PH_OB, PH = 59.47, 22.72, 41.91, 48.0
e, L, HK = 2.2, 7.6, 5.0                                     # без масштаба: e увеличено относительно L
O = np.zeros(2)
yD = lambda ph: e * tan(radians(ph))
Kp = lambda ph: L * np.array([cos(radians(ph)), sin(radians(ph))])

fig, ax = plt.subplots(figsize=(7.2, 7.6), dpi=260)
ax.set_aspect("equal"); ax.axis("off")


def arrow(p0, p1, color, lw=1.6, ms=13):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                      shrinkA=0, shrinkB=0), zorder=8)


def dim(p0, p1, txt, off_txt, rot=0):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.7, mutation_scale=9,
                                                      shrinkA=0, shrinkB=0), zorder=3)
    m = (np.array(p0) + np.array(p1)) / 2 + np.array(off_txt)
    ax.text(*m, txt, ha="center", va="center", fontsize=11, color=INK, rotation=rot, zorder=9)


def stone(ph, main):
    """камень — прямоугольник на кулисе с шарниром D (ЕСКД)"""
    r = Rectangle((-0.34, -0.19), 0.68, 0.38, fc="white", ec=INK, lw=1.4 if main else THIN, ls="-" if main else PHANTOM,
                  zorder=6 if main else 4)
    r.set_transform(Affine2D().rotate_deg(ph).translate(e, yD(ph)) + ax.transData); ax.add_patch(r)
    ax.add_patch(Circle((e, yD(ph)), 0.085, fc="white", ec=INK, lw=1.2 if main else THIN, ls="-" if main else PHANTOM,
                        zorder=7 if main else 5))


# треугольник O–Bн–Bк (критерий выбора окна)
Bn, Bk = np.array([e, yD(PH_N)]), np.array([e, yD(PH_K)])
ax.add_patch(Polygon([O, Bn, Bk], closed=True, fc=TRI, ec="none", zorder=1))
# оси ДСК
arrow((-0.9, 0), (8.6, 0), INK, lw=1.0, ms=11); ax.text(8.55, -0.35, "x", fontsize=12, ha="center", va="top")
arrow((0, -0.62), (0, 7.7), INK, lw=1.0, ms=11); ax.text(-0.3, 7.6, "y", fontsize=12, ha="right", va="center")

# стойка: вертикальная стойка под шарниром O на основании (угол 90°)
ax.add_patch(Circle(O, 0.13, fc="white", ec=INK, lw=1.4, zorder=7))
ax.plot([0, 0], [-0.13, -0.62], color=INK, lw=2.0, zorder=6)
ax.plot([-0.5, 0.5], [-0.62, -0.62], color=INK, lw=1.4, zorder=6)
for xh in np.linspace(-0.43, 0.5, 7):
    ax.plot([xh, xh - 0.17], [-0.62, -0.8], color=INK, lw=0.8, zorder=6)

# кулиса 1: рабочее положение и крайние положения
for ph in (PH_N, PH_K):
    K_ = Kp(ph); ax.plot([0, K_[0]], [0, K_[1]], color=INK, lw=THIN, ls=PHANTOM, zorder=2)
    stone(ph, False)
K = Kp(PH)
ax.plot([0, K[0]], [0, K[1]], color=INK, lw=MAIN, zorder=5, solid_capstyle="round")
ax.plot(*K, "o", ms=5, color=INK, zorder=8)
stone(PH, True)

# ползун 3 — линия в неподвижной направляющей
yh = lambda ph: yD(ph) - HK
ax.plot([e, e], [yD(PH) - 0.085, yh(PH)], color=INK, lw=MAIN, zorder=5, solid_capstyle="butt")
ax.plot([e, e], [yD(PH) + 0.1, yD(PH_N) - 0.1], color=INK, lw=THIN, ls=PHANTOM, zorder=3)     # шток в положении φн
ax.plot([e, e], [yh(PH), yh(PH_K)], color=INK, lw=THIN, ls=PHANTOM, zorder=3)                  # шток в положении φк
gy0, gy1 = -1.0, -0.2                                       # направляющая между Bк и головкой в положении φн
for sg in (-1, 1):
    xg = e + sg * 0.2
    ax.plot([xg, xg], [gy0, gy1], color=INK, lw=1.3, zorder=6)
    for yy in np.linspace(gy0 + 0.08, gy1, 5):
        ax.plot([xg, xg + sg * 0.17], [yy, yy - 0.17], color=INK, lw=0.8, zorder=6)

# участок обжима — от касания головки с крышкой до конца хода
ax.plot([e + 0.17, e + 0.17], [yD(PH_OB), Bk[1]], color=RED, lw=4.0, solid_capstyle="butt", zorder=4)
ax.text(e + 0.35, yD(PH_OB) - 0.22, "обжим", color=RED, fontsize=11, ha="left", va="center")

# силы
arrow(K + np.array([0, 1.5]), K + np.array([0, 0.12]), BLUE, lw=2.0, ms=15)
ax.text(K[0] + 0.15, K[1] + 1.2, "P", color=BLUE, fontsize=14, ha="left", va="center")
arrow((e, yh(PH) - 0.06), (e, yh(PH) - 0.62), RED, lw=2.0, ms=13)
ax.text(e - 0.5, yh(PH) - 0.35, r"$F_{ук}$", color=RED, fontsize=14, ha="right", va="center")

# обозначения
ax.text(-0.25, 0.25, "O", fontsize=13, ha="right", va="bottom")
ax.text(e - 0.4, yD(PH) + 0.3, "D", fontsize=13, ha="right", va="bottom")
ax.text(K[0] + 0.12, K[1] - 0.2, "K", fontsize=13, ha="left", va="top")
ax.text(*(0.9 * K - 0.35 * np.array([-sin(radians(PH)), cos(radians(PH))])), "1", fontsize=13, ha="center", va="center")
ax.text(e + 0.45, yD(PH) + 0.1, "2", fontsize=13, ha="left", va="bottom")
ax.text(e + 0.3, yh(PH) + 0.42, "3", fontsize=13, ha="left", va="center")
ax.text(Bn[0] + 0.28, Bn[1] + 0.05, r"$B_{н}$", color=TRI_E, fontsize=12, ha="left", va="center")
ax.text(Bk[0] + 0.3, Bk[1] - 0.32, r"$B_{к}$", color=TRI_E, fontsize=12, ha="left", va="center")
for ph, lab in ((PH_N, r"$\varphi_{н}$"), (PH_K, r"$\varphi_{к}$")):
    K_ = Kp(ph); ax.text(*(K_ + 0.38 * np.array([cos(radians(ph)), sin(radians(ph))])), lab, fontsize=12, color=INK2,
                         ha="center", va="center")
ax.add_patch(Arc(O, 2.6, 2.6, theta1=0, theta2=PH, color=INK, lw=0.9, zorder=4))
ax.text(1.55 * cos(radians(PH / 2)), 1.55 * sin(radians(PH / 2)), "φ", fontsize=13, ha="center", va="center")
ax.text(*(0.78 * K + 0.36 * np.array([-sin(radians(PH)), cos(radians(PH))])), "L = OK", fontsize=12, rotation=PH,
        ha="center", va="center", rotation_mode="anchor")

# размеры
xs = e + 2.0
for p in (Bn, Bk):
    ax.plot([p[0] + 0.1, xs + 0.15], [p[1], p[1]], color=INK2, lw=0.6, zorder=2)
dim((xs, Bn[1]), (xs, Bk[1]), "S", (0.25, 0.25))
ax.plot([K[0], K[0]], [K[1] - 0.1, -1.75], color=INK2, lw=0.6, ls=(0, (4, 3)), zorder=2)
dim((0, -1.6), (K[0], -1.6), "L·cos φ", (1.1, 0.25))
ax.plot([e, e], [yh(PH_K) - 0.1, -5.15], color=INK2, lw=0.6, zorder=2)
ax.plot([0, 0], [-1.0, -5.15], color=INK2, lw=0.6, zorder=2)
dim((0, -5.0), (e, -5.0), "e", (0, 0.25))

ax.set_xlim(-1.1, 8.9); ax.set_ylim(-5.4, 7.9)
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig1_scheme_v22.png"), facecolor="white",
            bbox_inches="tight", pad_inches=0.05)
print("ok")
