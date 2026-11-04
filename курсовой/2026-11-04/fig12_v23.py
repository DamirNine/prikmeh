# -*- coding: utf-8 -*-
"""Рис. 12 (v23) = рис. 12 из fig12_v20.py с правками: разрез Б–Б — секущая плоскость рядом с пальцем D (как в v20),
обойма и полоса в плоскости разреза заштрихованы, палец D за плоскостью — без штриховки; обойма и палец — одна деталь,
поэтому одного цвета (как на виде б);
ось пальца продлена через весь разрез; крайние положения камня — тонкими
штрихпунктирными линиями с двумя точками; отверстие оси O и палец D — Ø10 (п. 12.6), ступица Ø16 за полосой — штриховой."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "..", "2026-10-24", "strength_v13.json"), encoding="utf-8"))
PR = json.load(open(os.path.join(OUT, "calc_v21.json"), encoding="utf-8"))["pairs"]
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.titlesize": 9.4, "axes.titleweight": "bold", "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, ACC = "#0b0b0b", "#52514e", "#c4372b"
STONE, STRIP = "#e8c99a", "#c9d4e3"
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
L = 500.0
r_O, r_D, r_st = PR["D_O"] / 2, PR["D_D"] / 2, PR["D_ST"] / 2


def arrow(ax, p0, p1, color=INK, lw=1.4, ms=10):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                      shrinkA=0, shrinkB=0), zorder=6)


K_ = R["kul"]; b, h = K_["b"], K_["h"]; lk = R["stone"]["lk"]; s = 4.0; r_ = h / 2
mech = R["mech"]
pos3 = [("φк", mech["lOD_min"]), ("φу", R["A"]["lOD"]), ("φн", mech["lOD_max"])]
cy = R["A"]["lOD"]
PHANTOM = (0, (7, 2, 1, 2, 1, 2))
LIP_O, LIP_T, CL = 2.2, 2.5, 0.5                            # губки: заход на ребро, толщина; зазор за полосой
AXIS = (0, (8, 2, 1, 2))


def strip(x_end):
    th = np.linspace(np.pi / 2, 3 * np.pi / 2, 50)
    return np.vstack([[[x_end, r_]], np.column_stack([r_ * np.cos(th), r_ * np.sin(th)]), [[x_end, -r_]]])


def dimh(ax, xa, xb, y, txt, ya, yb, color=INK2):
    ax.annotate("", xy=(xb, y), xytext=(xa, y), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.7, shrinkA=0, shrinkB=0,
                                                                mutation_scale=7))
    ax.plot([xa, xa], [ya, y + 1.2 * np.sign(y)], color=color, lw=0.5); ax.plot([xb, xb], [yb, y + 1.2 * np.sign(y)], color=color, lw=0.5)
    ax.text((xa + xb) / 2, y + 0.5, txt, ha="center", va="bottom", fontsize=7.2, color=INK)


fig = plt.figure(figsize=(7.9, 5.6), dpi=220)
# а) кулиса целиком
ax = fig.add_axes([0.02, 0.775, 0.96, 0.165]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-40, 530); ax.set_ylim(-34, 34)
ax.set_title(f"а) кулиса с камнем-обоймой в начале пластической деформации, φу = {fmt(R['A']['phi'], 2)}°", fontsize=9, pad=3)
ax.add_patch(Polygon(strip(L), closed=True, fc=STRIP, ec=INK, lw=0.9, zorder=2))
ax.add_patch(Circle((0, 0), r_O, fc="white", ec=INK, lw=0.8, zorder=3))
ax.add_patch(Rectangle((cy - lk / 2, -h / 2 - s), lk, h + 2 * s, fc=STONE, ec=INK, lw=0.9, zorder=4))
ax.plot([-14, L + 8], [0, 0], color=INK2, lw=0.45, ls=AXIS, zorder=1)
ax.text(0, 11.5, "O", ha="center", va="bottom", fontsize=8.5)
ax.text(L + 6, 2, "K", ha="left", va="bottom", fontsize=8.5)
ax.add_patch(Circle((17, 0), 30, fc="none", ec=INK, lw=0.6, zorder=5))
ax.plot([17 - 30 * np.cos(np.pi / 4), -22], [30 * np.sin(np.pi / 4), 29], color=INK, lw=0.6)
ax.text(-23, 29, "А", ha="right", va="center", fontsize=9)
ax.annotate("", xy=(L, -24), xytext=(0, -24), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=7))
ax.plot([0, 0], [-r_ - 1, -25.2], color=INK2, lw=0.5); ax.plot([L, L], [-r_ - 1, -25.2], color=INK2, lw=0.5)
ax.text(L / 2, -23.3, "L = 500", ha="center", va="bottom", fontsize=7.6, color=INK)
ax.text(140, r_ + 2, f"полоса {b:g} × {h:g}, Ст3сп", ha="left", va="bottom", fontsize=7.4, color=INK2)

# б) выносной элемент А
ax = fig.add_axes([0.01, 0.01, 0.6, 0.71]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-22, 52); ax.set_ylim(-35, 39)
ax.set_title("б) выносной элемент А (увеличено)", fontsize=9, pad=3)
C0, RC = (15, 2), 35
clip = Circle(C0, RC, transform=ax.transData)
ax.add_patch(Circle(C0, RC, fc="none", ec=INK, lw=0.6, zorder=8))
arts = [ax.add_patch(Polygon(strip(70), closed=True, fc=STRIP, ec=INK, lw=1.0, zorder=2)),
        ax.plot([-14, 60], [0, 0], color=INK2, lw=0.5, ls=AXIS, zorder=6)[0]]
ax.add_patch(Circle((0, 0), r_O, fc="white", ec=INK, lw=0.9, zorder=3))
ax.add_patch(Circle((0, 0), r_st, fc="none", ec=INK, lw=0.6, ls=(0, (3, 1.6)), zorder=3))     # ступица за полосой
ax.plot([0, 0], [-r_st - 2, r_st + 2], color=INK2, lw=0.5, ls=AXIS, zorder=6)
ax.text(-6.5, -9.0, "O", ha="right", va="top", fontsize=8.5, zorder=9)
for lab, x in pos3:
    main = lab == "φу"
    rect = ax.add_patch(Rectangle((x - lk / 2, -h / 2 - s), lk, h + 2 * s, fc=STONE if main else "none", ec=INK,
                                  lw=1.1 if main else 0.5, ls="-" if main else PHANTOM, alpha=0.95 if main else 1, zorder=4 if main else 5))
    arts.append(rect)
    if main:
        for sg in (1, -1):
            arts.append(ax.plot([x - lk / 2, x + lk / 2], [sg * h / 2] * 2, color=INK2, lw=0.6, ls=(0, (3, 2)), zorder=5)[0])
        ax.add_patch(Circle((x, 0), r_D, fc=STONE, ec=INK, lw=0.9, zorder=6))       # палец D — заодно с обоймой
        ax.plot([x, x], [-r_D - 2, r_D + 2], color=INK2, lw=0.5, ls=AXIS, zorder=7)
        ax.plot([x - r_D - 2, x + r_D + 2], [0, 0], color=INK2, lw=0.5, ls=AXIS, zorder=7)
        ax.text(x - 5.2, 5.5, "D", ha="right", va="bottom", fontsize=8.5, zorder=9)
    else:
        ax.plot([x - 1.5, x + 1.5], [0, 0], color=INK, lw=0.5, zorder=7); ax.plot([x, x], [-1.5, 1.5], color=INK, lw=0.5, zorder=7)
for a in arts:
    a.set_clip_path(clip)
xc = cy + 6                                                   # секущая плоскость Б–Б — рядом с пальцем D, палец в неё не попадает
for k, (lab, x) in enumerate(pos3):
    y = 17 + 5.5 * k
    dimh(ax, 0, x, y, fmt(x, 2), h / 2 + 0.5, h / 2 + s + 0.5)
    ax.text(-1.8, y, lab, ha="right", va="center", fontsize=7.6, color=INK)
a1 = pos3[0][1] - lk / 2
ax.plot([0, 0], [-r_st - 0.5, -18.4], color=INK2, lw=0.5); ax.plot([a1, a1], [-h / 2 - s - 0.5, -18.4], color=INK2, lw=0.5)
ax.plot([0, a1], [-17.2, -17.2], color=INK2, lw=0.7)
arrow(ax, (-4.5, -17.2), (0, -17.2), INK2, lw=0.7, ms=7); arrow(ax, (a1 + 4.5, -17.2), (a1, -17.2), INK2, lw=0.7, ms=7)
ax.text(a1 + 5.5, -17.2, fmt(a1, 2), ha="left", va="center", fontsize=7.2)
for sg in (1, -1):
    ax.plot([xc, xc], [sg * (h / 2 + s + 0.6), sg * (h / 2 + s + 4.4)], color=INK, lw=2.0, solid_capstyle="butt", zorder=9)
    arrow(ax, (xc, sg * 17.6), (xc - 4.2, sg * 17.6), INK, lw=1.0, ms=8)
    ax.text(xc - 2.3, sg * 19.0, "Б", ha="center", va="bottom" if sg > 0 else "top", fontsize=8.5)
ax.text(-r_st - 0.6, r_st - 0.5, f"ступица Ø{PR['D_ST']:g}", ha="right", va="bottom", fontsize=6.8, color=INK2)

# в) разрез Б–Б: обойма и полоса в секущей плоскости заштрихованы; палец D (одна деталь с обоймой) лежит за плоскостью —
#    виден без штриховки
ax = fig.add_axes([0.63, 0.01, 0.36, 0.71]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-27, 21); ax.set_ylim(-24, 22)
ax.set_title("в) разрез Б–Б", fontsize=9, pad=3)
xf = -b / 2 - s                                              # наружная грань передней стенки
xl0, xl1 = b / 2 + CL, b / 2 + CL + LIP_T                    # губки: от задней грани полосы с зазором
yt, yl = h / 2 + s, h / 2 - LIP_O                            # наружная грань стенок; кромка губок
pin_l = 11.0
body = [[xf, -yt], [xl1, -yt], [xl1, -yl], [xl0, -yl], [xl0, -h / 2], [-b / 2, -h / 2], [-b / 2, h / 2], [xl0, h / 2],
        [xl0, yl], [xl1, yl], [xl1, yt], [xf, yt]]
ax.add_patch(Polygon(body, closed=True, fc=STONE, ec=INK, lw=1.0, hatch="////", joinstyle="miter"))
ax.add_patch(Rectangle((-b / 2, -h / 2), b, h, fc=STRIP, ec=INK, lw=1.0, hatch="\\\\\\\\"))
ax.add_patch(Rectangle((xf - pin_l, -r_D), pin_l, 2 * r_D, fc=STONE, ec=INK, lw=1.0))    # палец за секущей плоскостью
ax.plot([xf - pin_l - 2.5, xl1 + 2.5], [0, 0], color=INK2, lw=0.5, ls=AXIS, zorder=5)
ax.plot([-b / 2, b / 2], [-h / 2, -h / 2], color=ACC, lw=2.6, solid_capstyle="butt", zorder=6)
ax.text(xf - pin_l / 2, r_D + 1.5, f"палец D Ø{PR['D_D']:g}\nк ползуну", ha="center", va="bottom", fontsize=7.2, color=INK2,
        linespacing=1.15)
ax.text(xl1 + 1.8, 2, f"кулиса\n{b:g} × {h:g}", ha="left", va="bottom", fontsize=7.2, color=INK2, linespacing=1.15)
ax.text((xf + xl1) / 2, yt + 1.2, f"обойма, стенка {s:g}", ha="center", va="bottom", fontsize=7.2, color=INK2)
ax.annotate(f"рабочая грань:\np = {fmt(R['stone']['p'], 1)} МПа", xy=(1.5, -h / 2 - 0.2), xytext=(0, -yt - 4.5),
            fontsize=7.2, color=ACC, ha="center", va="top", linespacing=1.15,
            arrowprops=dict(arrowstyle="-", color=ACC, lw=0.7, shrinkA=0, shrinkB=0))
fig.savefig(os.path.join(OUT, "fig12_kamen_v23.png"), facecolor="white"); plt.close(fig)
print("ok")
