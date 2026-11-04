# -*- coding: utf-8 -*-
"""Рис. 7 и 13 (v21) — расчётные схемы звеньев в изображении по ЕСКД (ГОСТ 2.770-68): звенья — линиями, камень —
прямоугольником, ползун — прямоугольником на штоке; связи отброшены, поэтому шарниры O и D, центры масс S1, S3 и точка K —
точками. Рис. 13 = рис. 7 + силы тяжести, главные векторы и главный момент сил инерции. Схема без масштаба."""
import os, sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Arc
from matplotlib.transforms import Affine2D
from math import radians, cos, sin

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 10})
INK, INK2 = "#0b0b0b", "#52514e"
REACT, ACT, CRIMP = "#7b3fa0", "#0b0b0b", "#16908c"
GRAV, INERT, ANG = "#2a78d6", "#d9631e", "#b0306a"
LINK = 2.6                                                    # толщина линии звена


def draw(refined, fname):
    fig, ax = plt.subplots(figsize=(8.4, 6.6 if refined else 6.2), dpi=320)
    ax.set_aspect("equal"); ax.axis("off")

    def arrow(p0, p1, color, lw=1.8, ms=13, z=6):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, zorder=z,
                                     shrinkA=0, shrinkB=0))

    def label(xy, s, color, ha="center", va="center", fs=11):
        ax.text(xy[0], xy[1], s, color=color, ha=ha, va=va, fontsize=fs, zorder=9)

    def point(p, ms=5.5):
        ax.plot(*p, "o", ms=ms, color=INK, zorder=8)

    def moment(c, r, a0, a1, color, txt, txy):
        th = np.radians(np.linspace(a0, a1, 40))
        xs, ys = c[0] + r * np.cos(th), c[1] + r * np.sin(th)
        ax.plot(xs[:-3], ys[:-3], color=color, lw=1.5, zorder=6)
        arrow((xs[-4], ys[-4]), (xs[-1], ys[-1]), color, lw=1.5, ms=11)
        label(txy, txt, color)

    phi = radians(40.0)
    u = np.array([cos(phi), sin(phi)]); n = np.array([-sin(phi), cos(phi)])

    # ---------------- звено 1: кулиса с рукоятью — отрезок O–K
    O = np.array([0.0, 0.0]); lOD, LK = 3.3, 9.6
    D1 = O + lOD * u; K = O + LK * u
    ax.plot([O[0], K[0]], [O[1], K[1]], color=INK, lw=LINK, zorder=4, solid_capstyle="round")
    for p in (O, D1, K):
        point(p)
    label(D1 + np.array([-0.7, 0.15]), "D", INK, fs=10)
    label(O + np.array([-0.35, -0.35]), "O", INK, fs=10)
    label(K + np.array([-0.45, 0.35]), "K", INK, fs=10)
    ax.annotate("", xy=(-1.6, -0.75), xytext=(-1.6, -2.15), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.0))
    ax.annotate("", xy=(-0.3, -2.1), xytext=(-1.7, -2.1), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.0))
    label((-1.85, -0.85), "y", INK2, fs=9.5); label((-0.3, -2.35), "x", INK2, fs=9.5)
    ax.plot([0, 2.0], [0, 0], color=INK2, lw=0.8, ls=(0, (3, 2)), zorder=2)
    ax.add_patch(Arc(O, 2.4, 2.4, theta1=0, theta2=40, color=INK2, lw=1.0, zorder=4))
    label((1.45, 0.45), "φ", INK2, fs=11)
    arrow(O, O + np.array([1.5, 0]), REACT); label(O + np.array([2.0, -0.4]), r"$R_{10}^{x}$", REACT)
    arrow(O, O + np.array([0, 1.5]), REACT); label(O + np.array([-0.8, 1.15]), r"$R_{10}^{y}$", REACT)
    arrow(D1, D1 + 1.7 * n, REACT); label(D1 + 1.95 * n + np.array([0.1, 0.15]), r"$R_{12}^{N}$", REACT)
    moment(D1, 0.62, 250, 395, REACT, r"$M_{12}$", D1 + np.array([1.05, -0.95]))
    ax.plot([D1[0], D1[0] + 1.5], [D1[1], D1[1]], color=INK2, lw=0.8, ls=(0, (3, 2)), zorder=2)
    ax.add_patch(Arc(D1, 2.3, 2.3, theta1=0, theta2=130, color=ANG, lw=1.2, zorder=5))
    label(D1 + np.array([0.6, 1.6]), r"$\varphi + 90°$", ANG, fs=10)
    arrow(K + np.array([0, 1.7]), K + np.array([0, 0.25]), ACT, lw=2.0); label(K + np.array([0.35, 1.45]), "P", ACT, fs=12)
    off = -1.8 * n; pa, pb = O + off, K + off
    ax.annotate("", xy=pb, xytext=pa, arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.8, shrinkA=0, shrinkB=0))
    for p_ in (O, K):
        ax.plot([p_[0] - 0.25 * n[0], p_[0] + off[0] - 0.2 * n[0]], [p_[1] - 0.25 * n[1], p_[1] + off[1] - 0.2 * n[1]],
                color=INK2, lw=0.6)
    mid = (pa + pb) / 2 - 0.35 * n
    ax.text(mid[0], mid[1], "L", color=INK2, fontsize=10.5, rotation=40, ha="center", va="center")
    mid2 = O + 0.5 * lOD * u + 0.45 * n
    ax.text(mid2[0], mid2[1], r"$l_{OD}$", color=INK2, fontsize=10, rotation=40, ha="center", va="center")
    label((4.4, -2.9), "Звено 1 — кулиса с рукоятью", INK, fs=10.5)
    if refined:
        S1 = O + 6.8 * u
        point(S1); label(S1 + np.array([-1.0, -0.42]), r"$S_{1}$", INK, fs=10)
        arrow(S1, S1 + np.array([0, -1.45]), GRAV); label(S1 + np.array([0.42, -1.25]), r"$G_{1}$", GRAV)
        arrow(S1, S1 + 1.45 * n, INERT); label(S1 + 1.45 * n + np.array([-0.15, 0.32]), r"$\Phi_{1}^{\tau}$", INERT)
        arrow(S1, S1 + 1.45 * u, INERT); label(S1 + 1.45 * u + np.array([0.15, 0.42]), r"$\Phi_{1}^{n}$", INERT)
        moment(S1, 0.78, -70, 15, INERT, r"$M_{\Phi 1}$", S1 + np.array([1.35, -0.62]))

    # ---------------- точка приведения моментов M
    Mp = np.array([-2.9, 8.7])
    ax.plot(*Mp, "o", ms=8, color=INK, zorder=9); label(Mp + np.array([-0.35, 0.35]), "M", INK, fs=13)
    ax.plot([0, 0], [0.3, Mp[1] + 0.25], color=INK2, lw=0.7, ls=(0, (4, 3)), zorder=1)
    ax.plot([-0.3, Mp[0] - 0.25], [0, 0], color=INK2, lw=0.7, ls=(0, (4, 3)), zorder=1)
    ax.annotate("", xy=(0, Mp[1]), xytext=tuple(Mp), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3, shrinkA=4, shrinkB=0))
    ax.annotate("", xy=(Mp[0], 0), xytext=tuple(Mp), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3, shrinkA=4, shrinkB=0))
    label(((Mp[0] + 0) / 2, Mp[1] + 0.38), r"$x_{M}$", INK, fs=12)
    label((Mp[0] - 0.45, Mp[1] / 2), r"$y_{M}$", INK, fs=12)

    # ---------------- звено 2: камень — прямоугольник с осью кулисы (ЕСКД), точка D
    D2 = np.array([12.2, 5.4])
    rect = Rectangle((-0.62, -0.3), 1.24, 0.6, fc="white", ec=INK, lw=1.6, zorder=3)
    rect.set_transform(Affine2D().rotate(phi).translate(*D2) + ax.transData); ax.add_patch(rect)
    ax.plot(*np.array([D2 - 1.05 * u, D2 + 1.05 * u]).T, color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)), zorder=2)
    point(D2); label(D2 + np.array([-0.7, 0.55]), "D", INK, fs=10)
    arrow(D2, D2 - 1.7 * n, REACT); label(D2 - 1.95 * n + np.array([0.25, -0.1]), r"$R_{21}^{N}$", REACT)
    arrow(D2, D2 + np.array([1.6, 0]), REACT); label(D2 + np.array([1.95, -0.05]), r"$R_{23}^{x}$", REACT)
    arrow(D2, D2 + np.array([0, 1.6]), REACT); label(D2 + np.array([0.0, 1.9]), r"$R_{23}^{y}$", REACT)
    moment(D2, 1.15, 195, 290, REACT, r"$M_{21}$", D2 + np.array([-1.85, -0.85]))
    ax.add_patch(Arc(D2, 2.2, 2.2, theta1=-50, theta2=0, color=ANG, lw=1.2, zorder=5))
    label(D2 + np.array([2.2, -0.95]), r"$\varphi - 90°$", ANG, fs=10)
    label((D2[0] + 0.3, 2.55), "Звено 2 — камень", INK, fs=10.5)

    # ---------------- звено 3: ползун — шток линией, направляемая часть прямоугольником, головка — поперечная линия
    D3 = np.array([12.2, 0.0]); yG, yH = -1.6, (-5.6 if refined else -4.6)
    ax.plot([D3[0], D3[0]], [D3[1], yH], color=INK, lw=LINK, zorder=4, solid_capstyle="butt")
    ax.plot([D3[0] - 0.75, D3[0] + 0.75], [yH, yH], color=INK, lw=LINK, zorder=4, solid_capstyle="butt")
    ax.add_patch(Rectangle((D3[0] - 0.36, yG - 0.55), 0.72, 1.1, fc="white", ec=INK, lw=1.6, zorder=5))
    point(D3); label(D3 + np.array([-0.62, 0.15]), "D", INK, fs=10)
    arrow(D3, D3 + np.array([1.6, 0]), REACT); label(D3 + np.array([1.95, -0.05]), r"$R_{32}^{x}$", REACT)
    arrow(D3, D3 + np.array([0, 1.5]), REACT); label(D3 + np.array([0.0, 1.8]), r"$R_{32}^{y}$", REACT)
    G = np.array([D3[0] + 0.36, yG])
    arrow(G, G + np.array([1.4, 0]), REACT); label(G + np.array([1.8, 0.0]), r"$R_{30}^{N}$", REACT)
    moment(np.array([D3[0], yG]), 0.95, 200, 340, REACT, r"$M_{30}$", np.array([D3[0] - 1.45, yG - 0.75]))
    if refined:
        S3 = np.array([D3[0], -3.9])
        point(S3); label(S3 + np.array([-0.62, 0.0]), r"$S_{3}$", INK, fs=10)
        arrow(S3, S3 + np.array([0, -1.25]), GRAV); label(S3 + np.array([0.62, -0.95]), r"$G_{3}$", GRAV)
        arrow(S3, S3 + np.array([0, 1.1]), INERT); label(S3 + np.array([0.62, 0.85]), r"$\Phi_{3}$", INERT)
    arrow(np.array([D3[0], yH - 1.6]), np.array([D3[0], yH - 0.05]), CRIMP, lw=2.2, ms=14)
    label(np.array([D3[0] + 0.55, yH - 1.15]), r"$F_{\mathrm{ук}}$", CRIMP, fs=12)
    label((D3[0] + 0.3, yH - 2.25), "Звено 3 — ползун", INK, fs=10.5)

    if refined:
        leg = [(r"$\Phi_{1} = \Phi_{1}^{\tau} + \Phi_{1}^{n}$ — главный вектор сил инерции кулисы", INERT),
               (r"$M_{\Phi 1}$ — главный момент сил инерции кулисы", INERT),
               (r"$\Phi_{3}$ — главный вектор сил инерции ползуна", INERT),
               (r"$G_{1},\ G_{3}$ — силы тяжести", GRAV)]
        for k, (t, c) in enumerate(leg):
            ax.text(-3.7, -4.6 - 0.62 * k, t, color=c, fontsize=9.6, ha="left", va="center")
    ax.set_xlim(-3.9, 15.4); ax.set_ylim(yH - 2.6, 9.6)
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), fname), facecolor="white", bbox_inches="tight",
                pad_inches=0.06)
    plt.close(fig)


draw(False, "fig7_fbd_v21.png")
draw(True, "fig13_fbd_v21.png")
print("ok")
