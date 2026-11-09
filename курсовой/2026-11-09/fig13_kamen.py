# -*- coding: utf-8 -*-
"""Рис. 13 расчёта «Камень и кулиса» — палец D отдельной деталью (замечание преподавателя: камень — деталь с отверстием +
палец, нужна фиксация по оси). Основа — fig12_v23.py (2026-11-04): а) кулиса целиком, б) выносной элемент А, в) разрез Б–Б
(секущая плоскость рядом с пальцем, палец за ней — без штриховки) — без изменений, кроме пальца: в обойме он запрессован
(внутри стенки — штриховыми), к ползуну — обрыв. Новый г) разрез В–В — плоскость через ось пальца D, параллельно Б–Б: кулиса,
обойма, палец, ползун, шайба, гайка М8; палец, шайба и гайка в продольном разрезе — нерассечёнными (ГОСТ 2.305).
Размеры узла — как в 3D-модели (kompas/kompas_build.py): стенка обоймы 4, зазор до ползуна 1, ползун 16, уступ пальца в 0,5
перед ползуном, шайба 1,6, гайка 6,5; палец Ø10 × 21,5 + М8 × 10,5, длина 32; срез — в одной плоскости, между обоймой и ползуном.
    python fig13_kamen.py  →  fig13_kamen.png"""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "..", "2026-10-24", "strength_v13.json"), encoding="utf-8"))
PR = json.load(open(os.path.join(OUT, "..", "2026-11-04", "calc_v21.json"), encoding="utf-8"))["pairs"]
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.titlesize": 9.4, "axes.titleweight": "bold", "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, ACC = "#0b0b0b", "#52514e", "#c4372b"
STONE, STRIP, SLIDER, FAST = "#e8c99a", "#c9d4e3", "#b9bec6", "#dfe3e8"
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
L = 500.0
r_O, r_D, r_st = PR["D_O"] / 2, PR["D_D"] / 2, PR["D_ST"] / 2

K_ = R["kul"]; b, h = K_["b"], K_["h"]; lk = R["stone"]["lk"]; s = 4.0; r_ = h / 2
mech = R["mech"]
pos3 = [("φк", mech["lOD_min"]), ("φу", R["A"]["lOD"]), ("φн", mech["lOD_max"])]
cy = R["A"]["lOD"]
PHANTOM = (0, (7, 2, 1, 2, 1, 2))
LIP_O, LIP_T, CL = 2.2, 2.5, 0.5                            # губки: заход на ребро, толщина; зазор за полосой
AXIS = (0, (8, 2, 1, 2))
HID = (0, (3, 1.6))


def arrow(ax, p0, p1, color=INK, lw=1.4, ms=10):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                      shrinkA=0, shrinkB=0), zorder=6)


def strip(x_end):
    th = np.linspace(np.pi / 2, 3 * np.pi / 2, 50)
    return np.vstack([[[x_end, r_]], np.column_stack([r_ * np.cos(th), r_ * np.sin(th)]), [[x_end, -r_]]])


def dimh(ax, xa, xb, y, txt, ya, yb, color=INK2):
    ax.annotate("", xy=(xb, y), xytext=(xa, y), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.7, shrinkA=0, shrinkB=0,
                                                                mutation_scale=7))
    ax.plot([xa, xa], [ya, y + 1.2 * np.sign(y)], color=color, lw=0.5); ax.plot([xb, xb], [yb, y + 1.2 * np.sign(y)], color=color, lw=0.5)
    ax.text((xa + xb) / 2, y + 0.5, txt, ha="center", va="bottom", fontsize=7.2, color=INK)


def wavy_v(ax, x, y0, y1, amp=0.6, color=INK):
    ys = np.linspace(y0, y1, 40)
    ax.plot(x + amp * np.sin((ys - y0) / (y1 - y0) * 2 * np.pi * 1.5), ys, color=color, lw=0.7, zorder=7)


def cut_marks(ax, x, label, top, bot):
    """след секущей плоскости: толстые штрихи сверху (top = (y_in, y_out)) и снизу (bot), стрелки взгляда — к оси O (влево)"""
    for sg, (y_in, y_out) in ((1, top), (-1, bot)):
        ax.plot([x, x], [sg * y_in, sg * y_out], color=INK, lw=2.0, solid_capstyle="butt", zorder=9)
        arrow(ax, (x, sg * (y_out - 0.6)), (x - 4.2, sg * (y_out - 0.6)), INK, lw=1.0, ms=8)
        ax.text(x - 2.3, sg * (y_out + 0.3), label, ha="center", va="bottom" if sg > 0 else "top", fontsize=8.5)


fig = plt.figure(figsize=(7.9, 8.9), dpi=220)
# ---------------- а) кулиса целиком
ax = fig.add_axes([0.02, 0.865, 0.96, 0.105]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
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

# ---------------- б) выносной элемент А
ax = fig.add_axes([0.01, 0.38, 0.6, 0.47]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-22, 52); ax.set_ylim(-35, 39)
ax.set_title("б) выносной элемент А (увеличено)", fontsize=9, pad=3)
C0, RC = (15, 2), 35
clip = Circle(C0, RC, transform=ax.transData)
ax.add_patch(Circle(C0, RC, fc="none", ec=INK, lw=0.6, zorder=8))
arts = [ax.add_patch(Polygon(strip(70), closed=True, fc=STRIP, ec=INK, lw=1.0, zorder=2)),
        ax.plot([-14, 60], [0, 0], color=INK2, lw=0.5, ls=AXIS, zorder=6)[0]]
ax.add_patch(Circle((0, 0), r_O, fc="white", ec=INK, lw=0.9, zorder=3))
ax.add_patch(Circle((0, 0), r_st, fc="none", ec=INK, lw=0.6, ls=HID, zorder=3))     # ступица за полосой
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
        ax.add_patch(Circle((x, 0), r_D, fc=STONE, ec=INK, lw=0.9, zorder=6))       # торец пальца D, запрессованного в обойму
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
cut_marks(ax, xc, "Б", (h / 2 + s + 0.6, h / 2 + s + 4.4), (h / 2 + s + 0.6, h / 2 + s + 4.4))
cut_marks(ax, cy, "В", (30.0, 33.6), (h / 2 + s + 6.0, h / 2 + s + 9.6))      # В–В — через ось пальца; сверху — над размерами
ax.text(-r_st - 0.6, r_st - 0.5, f"ступица Ø{PR['D_ST']:g}", ha="right", va="bottom", fontsize=6.8, color=INK2)

# ---------------- в) разрез Б–Б: обойма и полоса в секущей плоскости заштрихованы; палец D — отдельная деталь за плоскостью:
#                  в стенке обоймы (запрессован) — штриховыми, наружу к ползуну — без штриховки, с обрывом
ax = fig.add_axes([0.63, 0.38, 0.36, 0.47]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-29, 21); ax.set_ylim(-24, 22)
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
wavy_v(ax, xf - pin_l, -r_D - 0.6, r_D + 0.6)
for sg in (1, -1):                                           # палец внутри стенки обоймы (запрессован) — невидимый контур
    ax.plot([xf, -b / 2], [sg * r_D, sg * r_D], color=INK, lw=0.7, ls=HID, zorder=6)
ax.plot([xf - pin_l - 2.5, xl1 + 2.5], [0, 0], color=INK2, lw=0.5, ls=AXIS, zorder=5)
ax.plot([-b / 2, b / 2], [-h / 2, -h / 2], color=ACC, lw=2.6, solid_capstyle="butt", zorder=6)
ax.text(xf - pin_l / 2 - 1.0, r_D + 1.5, f"палец D Ø{PR['D_D']:g},\nзапрессован;\nк ползуну —\nсм. В–В", ha="center",
        va="bottom", fontsize=7.0, color=INK2, linespacing=1.15)
ax.text(xl1 + 1.8, 2, f"кулиса\n{b:g} × {h:g}", ha="left", va="bottom", fontsize=7.2, color=INK2, linespacing=1.15)
ax.text((xf + xl1) / 2, yt + 1.2, f"обойма, стенка {s:g}", ha="center", va="bottom", fontsize=7.2, color=INK2)
ax.annotate(f"рабочая грань:\np = {fmt(R['stone']['p'], 1)} МПа", xy=(1.5, -h / 2 - 0.2), xytext=(0, -yt - 4.5),
            fontsize=7.2, color=ACC, ha="center", va="top", linespacing=1.15,
            arrowprops=dict(arrowstyle="-", color=ACC, lw=0.7, shrinkA=0, shrinkB=0))

# ---------------- г) разрез В–В через ось пальца D (параллельно Б–Б, взгляд к оси O): x — вдоль оси пальца (влево — к ползуну,
#                  x = −(z + 17,5), z — координата сборки), y — поперёк полосы. Размеры — как в 3D-модели
X = lambda z: -(z + 17.5)
ax = fig.add_axes([0.02, 0.005, 0.96, 0.355]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-92, 62); ax.set_ylim(-27, 27)
ax.set_title("г) разрез В–В — соединение камня с ползуном", fontsize=9, pad=3)
WEB0, WEB1 = -13.0, -9.0                                       # стенка обоймы с отверстием под палец
WALL0, LIP0, LIP1 = -24.5, -24.5, -22.0                        # обойма: задняя кромка стенок; губки за полосой
ST0, ST1 = -21.5, -13.5                                        # полоса кулисы
SL0, SL1, SL_H = -8.0, 8.0, 12.0 / np.sin(np.radians(R["A"]["phi"]))   # ползун 24 × 40 × 16: след плоскости В–В при φу
P0, P1, PL = -13.0, 8.5, 19.0                                  # палец: задний торец, уступ, конец резьбы
W1, N1 = P1 + 1.6, P1 + 1.6 + 6.5                              # шайба, гайка
RW, RN = 8.0, 13.0 / 2 / np.cos(np.radians(30))                # шайба Ø16; гайка — по углам (вид вдоль полосы)
YT3 = 13.5                                                     # наружная грань стенок обоймы
obo = [[X(WEB1), -YT3], [X(LIP0), -YT3], [X(LIP0), -6.8], [X(LIP1), -6.8], [X(LIP1), -9.5], [X(WEB0), -9.5], [X(WEB0), 9.5],
       [X(LIP1), 9.5], [X(LIP1), 6.8], [X(LIP0), 6.8], [X(LIP0), YT3], [X(WEB1), YT3]]
ax.add_patch(Polygon(obo, closed=True, fc=STONE, ec=INK, lw=1.0, hatch="////", joinstyle="miter"))
ax.add_patch(Rectangle((X(ST1), -h / 2), X(ST0) - X(ST1), h, fc=STRIP, ec=INK, lw=1.0, hatch="\\\\\\\\"))
ax.add_patch(Rectangle((X(SL1), -SL_H), SL1 - SL0, 2 * SL_H, fc=SLIDER, ec=INK, lw=1.0, hatch="\\\\\\\\"))
# палец: Ø10 от заднего торца до уступа, резьба Ø8 с фаской 1; сквозь стенку обоймы и ползун — целиком (не рассекается)
pin = [[X(P0), -r_D + 0.5], [X(P0 + 0.5), -r_D], [X(P1), -r_D], [X(P1), -4.0], [X(PL - 1), -4.0], [X(PL), -3.0], [X(PL), 3.0],
       [X(PL - 1), 4.0], [X(P1), 4.0], [X(P1), r_D], [X(P0 + 0.5), r_D], [X(P0), r_D - 0.5]]
ax.add_patch(Polygon(pin, closed=True, fc=STONE, ec=INK, lw=1.1, zorder=4))
for sg in (1, -1):                                             # резьба: тонкая линия по внутреннему диаметру М8
    ax.plot([X(P1), X(PL - 1)], [sg * 3.32, sg * 3.32], color=INK, lw=0.5, zorder=5)
ax.plot([X(P1), X(P1)], [-4.0, 4.0], color=INK, lw=0.8, zorder=5)
ax.add_patch(Rectangle((X(W1), -RW), W1 - P1, 2 * RW, fc=FAST, ec=INK, lw=1.0, zorder=6))
ax.add_patch(Rectangle((X(N1), -RN), N1 - W1, 2 * RN, fc=FAST, ec=INK, lw=1.0, zorder=6))
for yy in (-RN * 0.5, RN * 0.5):                               # рёбра шестигранника, видимые вдоль полосы
    ax.plot([X(W1), X(N1)], [yy, yy], color=INK, lw=0.7, zorder=7)
for x0, x1 in ((X(W1), X(W1) - 0.9), (X(N1), X(N1) + 0.9)):    # фаски 30° на углах гайки
    for sg in (1, -1):
        ax.plot([x0, x1], [sg * (RN - 0.9), sg * RN], color=INK, lw=0.7, zorder=7)
ax.plot([X(PL) - 3, X(WALL0) + 3], [0, 0], color=INK2, lw=0.5, ls=AXIS, zorder=8)
# плоскость среза — одна, в зазоре между обоймой и ползуном
xs = X((WEB1 + SL0) / 2)
ax.plot([xs, xs], [-r_D - 3.5, r_D + 3.5], color=ACC, lw=1.4, ls=(0, (4, 2)), zorder=9)
ax.annotate("плоскость среза —\nодна", xy=(xs, -r_D - 3.5), xytext=(xs + 7, -24.5), fontsize=7.2, color=ACC,
            ha="left", va="center", linespacing=1.15, arrowprops=dict(arrowstyle="-", color=ACC, lw=0.7, shrinkA=0, shrinkB=0))


def lead(xy, xytext, text, ha="left", color=INK2):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=7.2, color=color, ha=ha, va="center", linespacing=1.15,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.6, shrinkA=1, shrinkB=0))


lead((X(-17.5), 6.0), (12.0, 22.0), f"кулиса {b:g} × {h:g}")
lead((X(-23.5), 11.5), (12.0, 15.0), "обойма камня: стенка 4,\nпалец запрессован (H7/r6)")
lead((X(-11.0), 2.5), (12.0, 5.5), "палец D Ø10 × 32, сталь 45")
lead((X(0.0), SL_H - 3.0), (-44.0, 22.5), "ползун 24 × 40 × 16 —\nповорачивается на пальце", ha="right")
lead((X((P1 + W1) / 2), RW - 1.0), (-44.0, 13.5), "шайба 8 ГОСТ 11371-78", ha="right")
lead((X((W1 + N1) / 2), RN - 1.0), (-44.0, 8.0), "гайка М8 ГОСТ 5915-70", ha="right")
lead((X(17.8), -3.6), (-44.0, -3.0), "резьба М8 × 1,25", ha="right")
lead((X((SL1 + P1) / 2), -r_D - 0.3), (-44.0, -13.5), "уступ пальца — в 0,5 мм\nперед ползуном: гайка\nзатянута до упора шайбы\n"
     "в уступ, ползун не зажат\nи не сдвигается вдоль оси", ha="right")
# длина пальца
ax.plot([X(P0), X(P0)], [-r_D - 0.5, -21.5], color=INK2, lw=0.5); ax.plot([X(PL), X(PL)], [-3.5, -21.5], color=INK2, lw=0.5)
ax.annotate("", xy=(X(PL), -20.5), xytext=(X(P0), -20.5), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.7, shrinkA=0,
                                                                          shrinkB=0, mutation_scale=7))
ax.text((X(P0) + X(PL)) / 2, -20.0, "32", ha="center", va="bottom", fontsize=7.2)
fig.savefig(os.path.join(OUT, "fig13_kamen.png"), facecolor="white"); plt.close(fig)
print("ok")
