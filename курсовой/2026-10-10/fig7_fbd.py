# -*- coding: utf-8 -*-
"""Рис. 7 — расчётные схемы звеньев (силы и реакции), схема без масштаба."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, Arc, Polygon
from matplotlib.transforms import Affine2D
from math import radians, cos, sin

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 10})
INK, INK2 = "#0b0b0b", "#52514e"
REACT, ACT, CRIMP = "#7b3fa0", "#0b0b0b", "#16908c"
BODY, BODY_E = "#e9eef5", "#3b4a5c"

fig, ax = plt.subplots(figsize=(8.4, 5.6), dpi=320)
ax.set_aspect("equal"); ax.axis("off")

def arrow(p0, p1, color, lw=1.8, ms=13, z=6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, zorder=z,
                                 shrinkA=0, shrinkB=0))
def label(xy, s, color, ha="center", va="center", fs=11):
    ax.text(xy[0], xy[1], s, color=color, ha=ha, va=va, fontsize=fs, zorder=9)
def moment(c, r, a0, a1, color, txt, txy, ccw=True):
    """дуговая стрелка момента"""
    th = np.radians(np.linspace(a0, a1, 40))
    xs, ys = c[0] + r*np.cos(th), c[1] + r*np.sin(th)
    ax.plot(xs[:-3], ys[:-3], color=color, lw=1.5, zorder=6)
    arrow((xs[-4], ys[-4]), (xs[-1], ys[-1]), color, lw=1.5, ms=11)
    label(txy, txt, color)

phi = radians(40.0)
u = np.array([cos(phi), sin(phi)]); n = np.array([-sin(phi), cos(phi)])

# ---------------- Звено 1: кулиса с рукоятью
O = np.array([0.0, 0.0]); lOD, LK = 3.3, 9.6
D1 = O + lOD*u; K = O + LK*u
w = 0.22
bar = Polygon([O + w*n, K + w*n, K - w*n, O - w*n], closed=True, fc=BODY, ec=BODY_E, lw=1.2, zorder=3)
ax.add_patch(bar)
# паз
s0, s1 = O + 2.3*u, O + 4.6*u
ax.add_patch(Polygon([s0 + 0.09*n, s1 + 0.09*n, s1 - 0.09*n, s0 - 0.09*n], closed=True, fc="white", ec=BODY_E, lw=0.9, zorder=4))
ax.add_patch(Circle(O, 0.24, fc="white", ec=BODY_E, lw=1.3, zorder=5))
ax.plot(*D1, "o", ms=4.5, color=INK, zorder=7); label(D1 + 0.42*u - 0.36*n, "D", INK, fs=10)
label(O + np.array([-0.35, -0.35]), "O", INK, fs=10)
ax.plot(*K, "o", ms=4.5, color=INK, zorder=7); label(K + np.array([0.35, -0.25]), "K", INK, fs=10)
# оси
ax.annotate("", xy=(-1.5, 1.3), xytext=(-1.5, -0.1), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.0))
ax.annotate("", xy=(-0.2, -1.4), xytext=(-1.6, -1.4), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.0))
label((-1.75, 1.25), "y", INK2, fs=9.5); label((-0.2, -1.65), "x", INK2, fs=9.5)
# угол φ
ax.add_patch(Arc(O, 2.4, 2.4, theta1=0, theta2=40, color=INK2, lw=1.0, zorder=4))
label((1.45, 0.45), "φ", INK2, fs=11)
# реакции в O
arrow(O, O + np.array([1.5, 0]) - np.array([0, 0.0]), REACT)
label(O + np.array([1.55, -0.33]), r"$R_{10}^{x}$", REACT)
arrow(O, O + np.array([0, 1.5]), REACT)
label(O + np.array([-0.45, 1.55]), r"$R_{10}^{y}$", REACT)
# реакция камня на кулису
arrow(D1, D1 + 1.7*n, REACT)
label(D1 + 1.95*n + np.array([0.1, 0.15]), r"$R_{12}^{N}$", REACT)
moment(D1, 0.62, 250, 395, REACT, r"$M_{12}$", D1 + np.array([1.05, -0.95]))
# сила руки
arrow(K + np.array([0, 1.7]), K + np.array([0, 0.25]), ACT, lw=2.0)
label(K + np.array([0.35, 1.45]), "P", ACT, fs=12)
# размеры вдоль кулисы
off = -1.8*n
pa, pb = O + off, K + off
ax.annotate("", xy=pb, xytext=pa, arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.8, shrinkA=0, shrinkB=0))
for p_ in (O, K):
    ax.plot([p_[0] - 0.25*n[0], p_[0] + off[0] - 0.2*n[0]], [p_[1] - 0.25*n[1], p_[1] + off[1] - 0.2*n[1]], color=INK2, lw=0.6)
mid = (pa + pb)/2 - 0.35*n
ax.text(mid[0], mid[1], "L", color=INK2, fontsize=10.5, rotation=40, ha="center", va="center")
mid2 = O + 0.5*lOD*u + 0.62*n
ax.text(mid2[0], mid2[1], r"$l_{OD}$", color=INK2, fontsize=10, rotation=40, ha="center", va="center")
label((4.4, -2.9), "Звено 1 — кулиса с рукоятью", INK, fs=10.5)

# ---------------- Звено 2: камень
D2 = np.array([12.2, 5.4])
rect = Rectangle((-0.8, -0.32), 1.6, 0.64, fc=BODY, ec=BODY_E, lw=1.2, zorder=3)
rect.set_transform(Affine2D().rotate(phi).translate(*D2) + ax.transData); ax.add_patch(rect)
ax.add_patch(Circle(D2, 0.15, fc="white", ec=BODY_E, lw=1.2, zorder=5)); label(D2 + np.array([-0.45, 0.5]), "D", INK, fs=10)
arrow(D2, D2 - 1.7*n, REACT)
label(D2 - 1.95*n + np.array([0.25, -0.1]), r"$R_{21}^{N}$", REACT)
arrow(D2, D2 + np.array([1.6, 0]), REACT); label(D2 + np.array([1.95, -0.05]), r"$R_{23}^{x}$", REACT)
arrow(D2, D2 + np.array([0, 1.6]), REACT); label(D2 + np.array([0.0, 1.9]), r"$R_{23}^{y}$", REACT)
moment(D2, 0.9, 200, 310, REACT, r"$M_{21}$", D2 + np.array([-1.35, -0.75]))
label((D2[0] + 0.3, 2.55), "Звено 2 — камень", INK, fs=10.5)

# ---------------- Звено 3: ползун
D3 = np.array([12.2, 0.0])
ax.add_patch(Rectangle((D3[0] - 0.33, -4.4), 0.66, 4.75, fc=BODY, ec=BODY_E, lw=1.2, zorder=3))       # шток
ax.add_patch(Rectangle((D3[0] - 0.85, -5.0), 1.7, 0.62, fc=BODY, ec=BODY_E, lw=1.2, zorder=3))        # головка
ax.add_patch(Circle(D3, 0.15, fc="white", ec=BODY_E, lw=1.2, zorder=5)); label(D3 + np.array([-0.62, 0.15]), "D", INK, fs=10)
arrow(D3, D3 + np.array([1.6, 0]), REACT); label(D3 + np.array([1.95, -0.05]), r"$R_{32}^{x}$", REACT)
arrow(D3, D3 + np.array([0, 1.5]), REACT); label(D3 + np.array([0.0, 1.8]), r"$R_{32}^{y}$", REACT)
G = np.array([D3[0] + 0.33, -2.0])
arrow(G, G + np.array([1.5, 0]), REACT); label(G + np.array([1.9, 0.0]), r"$R_{30}^{N}$", REACT)
moment(np.array([D3[0], -2.0]), 1.0, 200, 340, REACT, r"$M_{30}$", np.array([D3[0] - 1.45, -2.75]))
arrow(np.array([D3[0], -6.6]), np.array([D3[0], -5.0]), CRIMP, lw=2.2, ms=14)
label(np.array([D3[0] + 0.55, -6.15]), r"$F_{\mathrm{ук}}$", CRIMP, fs=12)
label((D3[0] + 0.3, -7.25), "Звено 3 — ползун", INK, fs=10.5)

ax.set_xlim(-2.2, 15.4); ax.set_ylim(-7.7, 9.0)
fig.savefig("fig7_fbd_v6.png", facecolor="white", bbox_inches="tight", pad_inches=0.06)
print("ok")
