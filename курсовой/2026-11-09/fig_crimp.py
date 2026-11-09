# -*- coding: utf-8 -*-
"""Рисунок к п. 3.3: обжим кронен-крышки конической горловиной головки и разложение давления на элементе юбки.
а) половина осевого сечения (ось слева); б) элемент юбки на образующей конуса.
Стиль — как у рисунков расчёта: DejaVu Sans, штриховка сечений, размерные линии серые, сила обжима — бирюзовая.
Размеры, мм: юбка Dk = 32,10 → Dобж = 28,6, ход обжима Sоб = 6, tg α = 1,75 / 6 (α = 16,3°), головка Ø40;
горлышко — венчик 26 H 180 (как в 3D-модели бутылки). Положение — головка прошла 1,5 мм после касания: юбка прижата к
конусу там, где её исходный радиус больше радиуса горловины (полоса контакта 3,5 мм, вся на конусе).
    python fig_crimp.py  →  fig_crimp.png"""
import os
from math import atan, cos, degrees, radians, sin
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fig_crimp.png")
matplotlib.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "hatch.linewidth": 0.6})

BLACK, GRAY, TEAL, RED, CRIMSON = "#0b0b0b", "#52514e", "#16908c", "#c4372b", "#b0306a"
STEEL, STEEL_H, GLASS, GLASS_H, LINER, SHEET = "#c9d4e3", "#7c8796", "#e3edf3", "#8fa9bb", "#f8ddd2", "#2b2b2b"
DK, DOBZH, S_OB = 32.10, 28.6, 6.0
RK, RO = DK / 2, DOBZH / 2
TA = (RK - RO) / S_OB
ALPHA = degrees(atan(TA))                               # 16,3°
CA, SA = cos(radians(ALPHA)), sin(radians(ALPHA))
S = 1.5                                                 # головка прошла после касания, мм
Y_CT = 0.6 - S                                          # верх конуса (r = RO); при касании он на 0,6
Y_CB = Y_CT - S_OB                                      # низ конуса (r = RK)
Y_CH = Y_CB - 1.25                                      # низ заходной фаски
CEIL = 0.94 + 8.0 - S                                   # потолок полости над крышкой
Y_BRK = CEIL + 3.5                                      # обрыв головки
Y_SK0, Y_SKB, R_SK0 = -0.6, -5.4, 14.05                 # юбка: начало у плеча и нижняя кромка; радиус у плеча
Y_NECK = -11.0                                          # обрыв горлышка


def r_skirt0(y):
    """юбка до обжима: прямая от плеча (14,05; −0,6) до нижней кромки (16,05; −5,4)"""
    return R_SK0 + (Y_SK0 - y) * (RK - R_SK0) / (Y_SK0 - Y_SKB)


def r_tool(y):
    return RO if y >= Y_CT else RO + (Y_CT - y) * TA


def section(ax, pts, fill, hatch, hc, lw=1.4):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor=hc, hatch=hatch, lw=0))
    ax.add_patch(Polygon(pts, closed=True, facecolor="none", edgecolor=BLACK, lw=lw))


def arrow(ax, p0, p1, color, lw=1.6, ms=11, ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, linestyle=ls,
                                 shrinkA=0, shrinkB=0))


def wavy(ax, x0, x1, y, amp=0.35):
    xs = [x0 + (x1 - x0) * k / 60 for k in range(61)]
    ax.plot(xs, [y + amp * sin(6.2832 * 2.5 * (x - x0) / (x1 - x0)) for x in xs], color=BLACK, lw=0.8)


def dim_dia(ax, r, y, text, ext_from=None, left=False):
    """диаметр на половине сечения: размерная линия заходит за ось, стрелка — у поверхности; left — подпись слева от оси"""
    ax.plot([-1.6, r], [y, y], color=GRAY, lw=0.9)
    arrow(ax, (r - 2.0, y), (r, y), GRAY, lw=0.9, ms=8)
    if ext_from is not None:
        ax.plot([r, r], [ext_from - 0.3, y - 0.7], color=GRAY, lw=0.6)
    if left:
        ax.text(-2.0, y, text, ha="right", va="center", fontsize=10, color=BLACK)
    else:
        ax.text(r / 2 - 0.6, y + 0.3, text, ha="center", va="bottom", fontsize=10, color=BLACK)


fig, ax = plt.subplots(figsize=(6.8, 4.3))
ax.set_aspect("equal")
ax.axis("off")

# ---------------- а) половина осевого сечения
neck = [(8.7, 0.0), (12.0, 0.0), (13.3, -1.5), (13.3, -6.9), (13.0, -8.3), (13.0, Y_NECK), (8.7, Y_NECK)]
ax.add_patch(Polygon(neck, closed=True, facecolor=GLASS, edgecolor=GLASS_H, hatch="\\\\\\", lw=0))
ax.plot(*zip(*neck[-1:] + neck[:-1]), color=BLACK, lw=1.2)
wavy(ax, 8.7, 13.0, Y_NECK, 0.25)
ax.add_patch(Polygon([(0.0, 0.0), (12.4, 0.0), (12.4, 0.72), (0.0, 0.72)], closed=True, facecolor=LINER, edgecolor=BLACK, lw=0.8))
ys = [Y_SK0 - k * (Y_SK0 - Y_SKB) / 60 for k in range(61)]
cap = [(0.0, 0.94), (12.6, 0.94), (13.5, 0.7), (13.95, 0.1), (R_SK0, Y_SK0)] + [(min(r_skirt0(y), r_tool(y)), y) for y in ys]
head = [(0.0, CEIL), (RO, CEIL), (RO, Y_CT), (RK, Y_CB), (17.3, Y_CH), (20.0, Y_CH), (20.0, Y_BRK), (0.0, Y_BRK)]
ax.add_patch(Polygon(head, closed=True, facecolor=STEEL, edgecolor=STEEL_H, hatch="///", lw=0))
ax.plot(*zip(*head[:-1]), color=BLACK, lw=1.4)
ax.plot([0, 0], [Y_BRK, CEIL], color=BLACK, lw=1.4)
wavy(ax, 0.0, 20.0, Y_BRK)
ax.plot([x for x, _ in cap], [y for _, y in cap], color=SHEET, lw=2.6, solid_capstyle="butt", zorder=3)   # поверх головки
ax.plot([0, 0], [Y_NECK - 1.5, Y_BRK + 8.5], color=GRAY, lw=0.8, ls=(0, (9, 2.5, 1.5, 2.5)))   # ось

# давление q по нормали к образующей конуса в полосе контакта
y_top = next(y for y in [Y_CT - 0.01 * k for k in range(700)] if r_skirt0(y) > r_tool(y))      # верх полосы контакта
L_Q = 4.2
for k in range(4):
    y = y_top - 0.3 - k * (y_top - Y_SKB - 0.6) / 3
    x = r_tool(y)
    arrow(ax, (x + L_Q * CA, y + L_Q * SA), (x, y), RED, lw=1.6, ms=10)
ax.text(r_tool(y_top) + L_Q * CA + 0.4, y_top + L_Q * SA + 0.2, "q", color=RED, fontsize=13, style="italic", ha="left",
        va="bottom")
# ход обжима Sоб — длина конуса по оси (справа снаружи головки)
xs = 23.0
ax.plot([RO + 0.3, xs + 0.8], [Y_CT, Y_CT], color=GRAY, lw=0.6)
ax.plot([RK + 0.3, xs + 0.8], [Y_CB, Y_CB], color=GRAY, lw=0.6)
arrow(ax, (xs, (Y_CT + Y_CB) / 2), (xs, Y_CT), GRAY, lw=0.9, ms=8)
arrow(ax, (xs, (Y_CT + Y_CB) / 2), (xs, Y_CB), GRAY, lw=0.9, ms=8)
ax.text(xs + 0.6, (Y_CT + Y_CB) / 2, "$S_{об}$ = 6", rotation=90, ha="left", va="center", fontsize=10)
# диаметры: вход конуса = юбка до обжима, цилиндрический участок = юбка после обжима
dim_dia(ax, RO, CEIL - 2.6, "Ø28,6 ($D_{обж}$)")
dim_dia(ax, RK, Y_NECK - 1.4, "Ø32,10 ($D_k$)", ext_from=Y_CB, left=True)
# сила обжима — осевая равнодействующая давления, передаётся на ползун
arrow(ax, (0, Y_BRK + 1.0), (0, Y_BRK + 6.5), TEAL, lw=2.6, ms=16)
ax.text(0.9, Y_BRK + 4.6, "$F_{ук}$ = Σ q·sin α·ΔA", color=TEAL, fontsize=11, ha="left", va="center")


def leader(xy, xytext, text, ha="right"):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=9.5, color=GRAY, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.6, shrinkA=2, shrinkB=0))


leader((5.0, CEIL + 1.8), (-2.2, CEIL + 1.8), "головка ползуна")
leader((5.0, 0.94), (-2.2, 2.6), "крышка")
leader((5.0, 0.36), (-2.2, 0.0), "уплотнитель")
leader((10.5, -7.0), (-2.2, -7.0), "горлышко")
leader((r_tool(Y_CB + 0.7) + 0.3, Y_CB + 0.7), (21.0, Y_CH - 1.6), "горловина — конус, α = 16,3°", ha="left")
ax.text(-12.5, Y_BRK + 11.0, "а) половина осевого сечения", fontsize=10.5, weight="bold", ha="left", va="top")

# ---------------- б) давление на элемент юбки и его составляющие
cx, cy, h = 40.0, 1.5, 6.0                             # точка приложения на образующей
n, t = (CA, SA), (-SA, CA)                               # нормаль к головке; вдоль образующей вверх
p0, p1 = (cx - h * t[0], cy - h * t[1]), (cx + h * t[0], cy + h * t[1])
strip = [p0, p1, (p1[0] + 2.4 * n[0], p1[1] + 2.4 * n[1]), (p0[0] + 2.4 * n[0], p0[1] + 2.4 * n[1])]
ax.add_patch(Polygon(strip, closed=True, facecolor=STEEL, edgecolor=STEEL_H, hatch="///", lw=0))
ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=BLACK, lw=1.4)
ax.plot([p0[0] - 0.8 * n[0], p1[0] - 0.8 * n[0]], [p0[1] - 0.8 * n[1], p1[1] - 0.8 * n[1]], color=SHEET, lw=2.6)
ax.text(p0[0] - 1.0, p0[1] + 0.3, "юбка", fontsize=9.5, color=GRAY, ha="right", va="bottom")
ax.text(p1[0] + 2.8, p1[1] + 0.2, "головка", fontsize=9.5, color=GRAY, ha="left", va="bottom")
Q = 13.0
tail = (cx + Q * n[0], cy + Q * n[1])
ax.plot([tail[0], tail[0]], [tail[1], cy], color=GRAY, lw=0.6, ls=(0, (2, 2)))
ax.plot([tail[0], cx], [tail[1], tail[1]], color=GRAY, lw=0.6, ls=(0, (2, 2)))
arrow(ax, tail, (cx, cy), RED, lw=2.0, ms=13)
ax.text(tail[0] + 0.5, tail[1] + 0.2, "q", color=RED, fontsize=13, style="italic", ha="left", va="bottom")
arrow(ax, (tail[0], cy), (cx, cy), RED, lw=1.3, ms=9, ls=(0, (4, 2)))                 # радиальная составляющая
arrow(ax, (cx, tail[1]), (cx, cy), RED, lw=1.3, ms=9, ls=(0, (4, 2)))                 # осевая составляющая
ax.text(cx + 1.5, cy - 0.6, "q·cos α — обжим юбки", color=RED, fontsize=9.5, ha="left", va="top")
ax.text(cx + 0.4, tail[1] + 0.3, "q·sin α", color=RED, fontsize=9.5, ha="left", va="bottom")
ax.add_patch(Arc((cx, cy), 15.0, 15.0, theta1=0, theta2=ALPHA, color=CRIMSON, lw=1.1))
ax.text(cx + 7.9, cy + 1.1, "α", color=CRIMSON, fontsize=11, ha="left", va="center")
ax.text(31.0, Y_BRK + 11.0, "б) элемент юбки на образующей конуса", fontsize=10.5, weight="bold", ha="left", va="top")

ax.set_xlim(-13.0, 63.0)
ax.set_ylim(Y_NECK - 3.0, Y_BRK + 11.5)
fig.savefig(OUT, dpi=320, bbox_inches="tight", pad_inches=0.05, facecolor="white")
print(OUT, f"α = {ALPHA:.1f}°, полоса контакта y {y_top:.2f}…{Y_SKB:.2f} ({y_top - Y_SKB:.2f} мм)")
