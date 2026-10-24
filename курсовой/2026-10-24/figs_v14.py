# -*- coding: utf-8 -*-
"""Рисунки раздела 12 (v14): 10, 11 — схема и эпюры N, Q, M на истинном (наклонном) положении кулисы при φу и φк;
12 — камень-обойма: кулиса целиком, выносной элемент А, сечение Б–Б; 13 — шток ползуна: схема, эпюра N, σкр(λ)."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.ticker import FuncFormatter

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "strength_v13.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.titlesize": 9.4, "axes.titleweight": "bold", "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, GRID, S1, S3, ACC, VIO = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#2f9e6b", "#c4372b", "#7b3fa0"
LIGHT = {S1: "#dbe8f7", S3: "#dcefe5", ACC: "#f6dcd9"}
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
L = 500.0
FS = 7.8


def arrow(ax, p0, p1, color=INK, lw=1.4, ms=10):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                      shrinkA=0, shrinkB=0), zorder=6)


# ====================================================================== рис. 10, 11 — эпюры на наклонной кулисе
def epury(pos, fname):
    phd = pos["phi"]; phi = np.radians(phd)
    u = np.array([np.cos(phi), np.sin(phi)]); n = np.array([-np.sin(phi), np.cos(phi)])
    lOD = pos["lOD"]; O = np.zeros(2); D = lOD * u; K = L * u
    N, QOD, QDK, MD = pos["N"], pos["Q_OD"], pos["Q_DK"], pos["M_D"] / 1000
    oN, oQ, oQ2, oM = 36 * np.sign(N), 70 * np.sign(QOD), 16 * np.sign(QDK), 80 * np.sign(MD)   # ординаты на рисунке
    x0, x1, y1 = -95, K[0] + 45, K[1] + 85
    y0 = min(-80, (D + (oM + 8 * np.sign(oM)) * n)[1] - 24)
    W, H = x1 - x0, y1 - y0
    pw = 3.75; ph = pw * H / W; tt = 0.3
    fw, fh = 2 * pw + 0.25, 2 * (ph + tt) + 0.05
    fig = plt.figure(figsize=(fw, fh), dpi=220)
    axs = [fig.add_axes([(0.05 + c * (pw + 0.15)) / fw, (fh - (r + 1) * (ph + tt)) / fh, pw / fw, ph / fh])
           for r in range(2) for c in range(2)]
    bis = np.array([np.cos(phi + np.pi / 4), np.sin(phi + np.pi / 4)])
    titles = [f"а) расчётная схема, φ = {fmt(phd, 2)}°", "б) эпюра N, Н", "в) эпюра Q, Н (ординаты без масштаба)", "г) эпюра M, Н·м"]
    for ax, t in zip(axs, titles):
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(t, fontsize=9, pad=3)
        ax.plot([-45, K[0] + 25], [0, 0], color=INK2, lw=0.6, ls=(0, (6, 3)), zorder=1)
        ax.plot([O[0], K[0]], [O[1], K[1]], color=INK, lw=2.4, zorder=4, solid_capstyle="round")
        ax.plot(*O, "o", ms=5.5, mfc="white", mec=INK, mew=1.2, zorder=7)
        ax.plot(*D, "s", ms=4.2, color=INK, zorder=7)
        ax.plot(*K, "o", ms=3.6, color=INK, zorder=7)
        ax.text(-12, -12, "O", fontsize=9, ha="right", va="top")
        ax.text(*(K + 12 * u), "K", fontsize=9, ha="left", va="center")

    def ordinate(z, zs, ords):
        for k in range(len(zs) - 1):
            if zs[k] <= z <= zs[k + 1] and zs[k + 1] > zs[k]:
                return ords[k] + (z - zs[k]) / (zs[k + 1] - zs[k]) * (ords[k + 1] - ords[k])
        return ords[-1]

    def epure(ax, zs, ords, color):
        base = [z * u for z in zs]; top = [z * u + o * n for z, o in zip(zs, ords)]
        ax.add_patch(Polygon(np.vstack([base, top[::-1]]), closed=True, fc=LIGHT[color], ec="none", zorder=2))
        ax.plot(*np.array(top).T, color=color, lw=1.4, zorder=3)
        for p0, p1 in ((base[0], top[0]), (base[-1], top[-1])):
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=1.4, zorder=3)
        for z in np.r_[np.linspace(0, lOD, 4)[1:-1], np.linspace(lOD, L, 33)[1:-1]]:
            p0 = z * u; p1 = p0 + ordinate(z, zs, ords) * n
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=0.45, zorder=2)

    # подпись D — со стороны, свободной от эпюры: у эпюры Q полоса D–K лежит по +n, участок O–D — по −n
    for k, ax in enumerate(axs):
        ax.text(*(D + (20 * n - 15 * u if k == 2 else 26 * bis)), "D", fontsize=9, ha="center", va="center")
    # а) схема: силы в истинных направлениях
    ax = axs[0]
    tip = D + 85 * n; arrow(ax, tuple(D), tuple(tip), VIO)
    ax.text(tip[0] + 5, tip[1] + 3, r"$R_{12}^{N}$ = " + fmt(pos["R12N"], 0) + " Н", fontsize=FS, color=VIO, ha="left", va="bottom")
    arrow(ax, (0, 0), (60, 0), VIO)
    ax.text(64, -5, r"$R_{10}^{x}$ = " + fmt(pos["R10x"], 0) + " Н", fontsize=FS, color=VIO, ha="left", va="top")
    sy = np.sign(pos["R10y"]); arrow(ax, (0, 0), (0, 62 * sy), VIO)
    ax.text(7, 62 * sy, r"$|R_{10}^{y}|$ = " + fmt(abs(pos["R10y"]), 0) + " Н", fontsize=FS, color=VIO, ha="left", va="center")
    arrow(ax, (K[0], K[1] + 75), (K[0], K[1] + 4), INK, lw=1.8)
    ax.text(K[0] - 7, K[1] + 52, "P = " + fmt(pos["P"], 1) + " Н", fontsize=FS, ha="right", va="center")
    ax.text(*(0.55 * K - 22 * n), "L = 500 мм", fontsize=FS, color=INK2, rotation=phd, ha="center", va="center", rotation_mode="anchor")
    th = np.linspace(0, phi, 30); ax.plot(80 * np.cos(th), 80 * np.sin(th), color=INK2, lw=0.8)
    ax.text(92 * np.cos(phi / 2), 92 * np.sin(phi / 2), "φ", fontsize=9, color=INK2, ha="center", va="center")
    # б) N
    ax = axs[1]
    epure(ax, [0, L], [oN, oN], S3)
    p = 0.45 * L * u + (oN + 8 * np.sign(oN)) * n
    ax.text(*p, f"N = {fmt(N, 1)} Н (сжатие)", fontsize=FS, ha="left", va="top")
    # в) Q: участок O–D и участок D–K показаны каждый своим масштабом
    ax = axs[2]
    epure(ax, [0, lOD, lOD, L], [oQ, oQ, oQ2, oQ2], S1)
    p = 0.5 * lOD * u + (oQ + 10 * np.sign(oQ)) * n
    ax.text(*p, f"{fmt(QOD, 1)} (участок O–D)", fontsize=FS, ha="left", va="top")
    p = 0.5 * L * u + (oQ2 + 8 * np.sign(oQ2)) * n
    ax.text(*p, ("+" if QDK > 0 else "") + f"{fmt(QDK, 1)} (участок D–K)", fontsize=FS, ha="right", va="bottom")
    # г) M
    ax = axs[3]
    epure(ax, [0, lOD, L], [0, oM, 0], ACC)
    p = D + (oM + 8 * np.sign(oM)) * n
    ax.text(*p, r"$M_{D}$ = " + f"{fmt(MD, 2)} Н·м (под камнем)", fontsize=FS, ha="left", va="top")
    fig.savefig(os.path.join(OUT, fname), facecolor="white"); plt.close(fig)


epury(R["A"], "fig10_epury_phiy_v14.png")
epury(R["B"], "fig11_epury_phik_v14.png")


# ====================================================================== рис. 12 — камень-обойма
K_ = R["kul"]; b, h = K_["b"], K_["h"]; lk = R["stone"]["lk"]; s = 4.0; r_ = h / 2
mech = R["mech"]
pos3 = [("φк", mech["lOD_min"]), ("φу", R["A"]["lOD"]), ("φн", mech["lOD_max"])]
cy = R["A"]["lOD"]
PHANTOM = (0, (7, 2, 1, 2, 1, 2))                          # штрихпунктирная с двумя точками — крайние положения


def strip(x_end):
    th = np.linspace(np.pi / 2, 3 * np.pi / 2, 50)
    return np.vstack([[[x_end, r_]], np.column_stack([r_ * np.cos(th), r_ * np.sin(th)]), [[x_end, -r_]]])


def dimh(ax, xa, xb, y, txt, ya, yb, color=INK2):
    ax.annotate("", xy=(xb, y), xytext=(xa, y), arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.7, shrinkA=0, shrinkB=0,
                                                                mutation_scale=7))
    ax.plot([xa, xa], [ya, y + 1.2 * np.sign(y)], color=color, lw=0.5); ax.plot([xb, xb], [yb, y + 1.2 * np.sign(y)], color=color, lw=0.5)
    ax.text((xa + xb) / 2, y + 0.5, txt, ha="center", va="bottom", fontsize=7.2, color=INK)


fig = plt.figure(figsize=(7.9, 5.5), dpi=220)
# а) кулиса целиком
ax = fig.add_axes([0.02, 0.775, 0.96, 0.165]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-40, 530); ax.set_ylim(-34, 34)
ax.set_title(f"а) кулиса с камнем-обоймой в начале пластической деформации, φу = {fmt(R['A']['phi'], 2)}°", fontsize=9, pad=3)
ax.add_patch(Polygon(strip(L), closed=True, fc="#e9eef5", ec=INK, lw=0.9, zorder=2))
ax.add_patch(Circle((0, 0), 2.6, fc="white", ec=INK, lw=0.8, zorder=3))
ax.add_patch(Rectangle((cy - lk / 2, -h / 2 - s), lk, h + 2 * s, fc="#f3ece2", ec=INK, lw=0.9, zorder=4))
ax.plot([-14, L + 8], [0, 0], color=INK2, lw=0.45, ls=(0, (8, 2, 1, 2)), zorder=1)
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
arts = [ax.add_patch(Polygon(strip(70), closed=True, fc="#e9eef5", ec=INK, lw=1.0, zorder=2)),
        ax.plot([-14, 60], [0, 0], color=INK2, lw=0.5, ls=(0, (10, 2, 1, 2)), zorder=6)[0]]
ax.add_patch(Circle((0, 0), 3, fc="white", ec=INK, lw=0.9, zorder=3)); ax.plot([0, 0], [-6, 6], color=INK2, lw=0.5, ls=(0, (6, 2, 1, 2)), zorder=6)
ax.text(-3.5, -3.5, "O", ha="right", va="top", fontsize=8.5, zorder=9)
for lab, x in pos3:
    main = lab == "φу"
    rect = ax.add_patch(Rectangle((x - lk / 2, -h / 2 - s), lk, h + 2 * s, fc="#f3ece2" if main else "none", ec=INK if main else INK2,
                                  lw=1.1 if main else 0.8, ls="-" if main else PHANTOM, alpha=0.95 if main else 1, zorder=4 if main else 5))
    arts.append(rect)
    if main:
        for sg in (1, -1):
            arts.append(ax.plot([x - lk / 2, x + lk / 2], [sg * h / 2] * 2, color=INK2, lw=0.6, ls=(0, (3, 2)), zorder=5)[0])
        ax.add_patch(Circle((x, 0), 4, fc="white", ec=INK, lw=0.9, zorder=6))
        ax.plot([x, x], [-6, 6], color=INK2, lw=0.5, ls=(0, (6, 2, 1, 2)), zorder=7)
        ax.text(x - 5.2, 4.5, "D", ha="right", va="bottom", fontsize=8.5, zorder=9)
    else:
        ax.plot([x - 1.5, x + 1.5], [0, 0], color=INK2, lw=0.8, zorder=7); ax.plot([x, x], [-1.5, 1.5], color=INK2, lw=0.8, zorder=7)
for a in arts:
    a.set_clip_path(clip)
for k, (lab, x) in enumerate(pos3):
    y = 17 + 5.5 * k
    dimh(ax, 0, x, y, fmt(x, 2), h / 2 + 0.5, h / 2 + s + 0.5)
    ax.text(-1.8, y, lab, ha="right", va="center", fontsize=7.6, color=INK)
a1 = pos3[0][1] - lk / 2                                    # от оси O до края обоймы в конце хода
ax.plot([0, 0], [-h / 2 - 0.5, -18.4], color=INK2, lw=0.5); ax.plot([a1, a1], [-h / 2 - s - 0.5, -18.4], color=INK2, lw=0.5)
ax.plot([0, a1], [-17.2, -17.2], color=INK2, lw=0.7)
arrow(ax, (-4.5, -17.2), (0, -17.2), INK2, lw=0.7, ms=7); arrow(ax, (a1 + 4.5, -17.2), (a1, -17.2), INK2, lw=0.7, ms=7)
ax.text(a1 + 5.5, -17.2, fmt(a1, 2), ha="left", va="center", fontsize=7.2)
xc = cy + 6                                                 # секущая плоскость Б–Б, взгляд к оси O
for sg in (1, -1):
    ax.plot([xc, xc], [sg * (h / 2 + s + 0.6), sg * (h / 2 + s + 4.4)], color=INK, lw=2.0, solid_capstyle="butt", zorder=9)
    arrow(ax, (xc, sg * 17.6), (xc - 4.2, sg * 17.6), INK, lw=1.0, ms=8)
    ax.text(xc - 2.3, sg * 19.0, "Б", ha="center", va="bottom" if sg > 0 else "top", fontsize=8.5)

# в) сечение Б–Б: слева — передняя стенка обоймы и палец D, справа — открытая сторона к стойке
ax = fig.add_axes([0.63, 0.01, 0.36, 0.71]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
ax.set_xlim(-27, 21); ax.set_ylim(-24, 22)
ax.set_title("в) сечение Б–Б", fontsize=9, pad=3)
xb0 = -b / 2 - s
ax.add_patch(Polygon([[xb0, -h / 2 - s], [b / 2 + 0.5, -h / 2 - s], [b / 2 + 0.5, -h / 2], [-b / 2, -h / 2], [-b / 2, h / 2],
                      [b / 2 + 0.5, h / 2], [b / 2 + 0.5, h / 2 + s], [xb0, h / 2 + s]], closed=True, fc="#f3ece2", ec=INK, lw=1.0, hatch="////"))
ax.add_patch(Rectangle((-b / 2, -h / 2), b, h, fc="#e9eef5", ec=INK, lw=1.0, hatch="\\\\\\\\"))
ax.add_patch(Rectangle((xb0 - 11, -4), 11, 8, fc="white", ec=INK, lw=1.0))
ax.plot([xb0 - 13, xb0 + 2], [0, 0], color=INK2, lw=0.5, ls=(0, (6, 2, 1, 2)))
ax.plot([-b / 2, b / 2], [-h / 2, -h / 2], color=ACC, lw=2.6, solid_capstyle="butt", zorder=6)
ax.text(xb0 - 5.5, 5.5, "палец D\nк ползуну", ha="center", va="bottom", fontsize=7.2, color=INK2, linespacing=1.15)
ax.text(b / 2 + 2.2, 2, f"кулиса\n{b:g} × {h:g}", ha="left", va="bottom", fontsize=7.2, color=INK2, linespacing=1.15)
ax.text((xb0 + b / 2) / 2, h / 2 + s + 1.2, f"обойма, стенка {s:g}", ha="center", va="bottom", fontsize=7.2, color=INK2)
ax.annotate(f"рабочая грань:\np = {fmt(R['stone']['p'], 1)} МПа", xy=(1.5, -h / 2 - 0.2), xytext=(0, -h / 2 - s - 4.5),
            fontsize=7.2, color=ACC, ha="center", va="top", linespacing=1.15,
            arrowprops=dict(arrowstyle="-", color=ACC, lw=0.7, shrinkA=0, shrinkB=0))
fig.savefig(os.path.join(OUT, "fig12_kamen_v14.png"), facecolor="white"); plt.close(fig)


# ====================================================================== рис. 13 — шток
rd, rp, it = R["rod"], R["rod_par"], R["rod_iter"]
E = 2.1e5
fig = plt.figure(figsize=(7.9, 4.4), dpi=220)
gs = fig.add_gridspec(1, 3, width_ratios=[0.8, 0.62, 1.9], wspace=0.42, left=0.02, right=0.98, top=0.9, bottom=0.14)
ax = fig.add_subplot(gs[0]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off"); ax.set_xlim(-32, 32); ax.set_ylim(-97, 24)
ax.add_patch(Rectangle((-22, 0), 44, 12, fc="#dcdcd8", ec=INK, hatch="////", lw=0.9))
ax.text(0, 15, "направляющая\n(заделка)", ha="center", va="bottom", fontsize=7.2, color=INK2, linespacing=1.1)
d = rd["d"]; ax.add_patch(Rectangle((-d / 2, -60), d, 60, fc="white", ec=INK, lw=1.2))
ax.add_patch(Rectangle((-14, -68), 28, 8, fc="#e9eef5", ec=INK, lw=0.9)); ax.text(16, -64, "головка", fontsize=7.2, color=INK2, va="center")
arrow(ax, (0, -94), (0, -68.5), S3, lw=1.6); ax.text(3, -84, r"$F_{ук}$ = " + fmt(rp["F"], 0) + " Н", fontsize=7.4, color=S3, va="center")
ax.annotate("", xy=(-24, 0), xytext=(-24, -60), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.7, mutation_scale=7, shrinkA=0, shrinkB=0))
ax.text(-26, -30, "l = 60", rotation=90, ha="right", va="center", fontsize=7.4, color=INK2)
ax.set_title(f"а) шток Ø{d:g}, μ = 2", fontsize=9)
ax = fig.add_subplot(gs[1])
ax.fill_betweenx([-60, 0], 0, -rp["F"], facecolor=LIGHT[S3], edgecolor=S3, hatch="--", lw=0)
ax.plot([-rp["F"], -rp["F"]], [-60, 0], color=S3, lw=1.6); ax.axvline(0, color=INK, lw=1)
ax.set_xlim(-2600, 300); ax.set_ylim(-70, 8); ax.set_yticks([0, -20, -40, -60]); ax.set_xticks([-2000, 0])
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:g}"))); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:g}")))
ax.text(-rp["F"] / 2, -30, fmt(-rp["F"], 0), ha="center", va="center", fontsize=7.8, bbox=dict(fc="white", ec="none", pad=0.6))
ax.set_xlabel("N, Н"); ax.set_ylabel("мм от направляющей"); ax.set_title("б) эпюра N", fontsize=9)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
ax = fig.add_subplot(gs[2])
lam_pr, a_J, b_J, sT = rp["lam_pr"], rp["a"], rp["b"], rp["sT"]
l1 = np.linspace(20, lam_pr, 300); l2 = np.linspace(lam_pr, 160, 300)
ax.plot(l1, np.minimum(a_J - b_J * l1, sT), color=INK, lw=1.6)
ax.plot(l2, np.pi ** 2 * E / l2 ** 2, color=INK, lw=1.6)
lE = np.linspace(np.pi * np.sqrt(E / 280), lam_pr, 60)
ax.plot(lE, np.pi ** 2 * E / lE ** 2, color=INK2, lw=0.8, ls="--")
ax.axvline(lam_pr, color=INK2, lw=0.6, ls=":")
ax.set_xlim(20, 160); ax.set_ylim(0, 300); ax.grid(True, color=GRID, lw=0.7); ax.set_axisbelow(True)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:g}")))
ax.set_xlabel(r"гибкость $\lambda = \mu l / i$"); ax.set_ylabel(r"$\sigma_{кр}$, МПа"); ax.set_title("в) критическое напряжение, сталь Ст3", fontsize=9)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
ax.text(23, sT + 6, r"$\sigma_{кр} = \sigma_{т}$", fontsize=7.6, color=INK2, va="bottom")
ax.text(128, np.pi ** 2 * E / 128 ** 2 + 12, "Эйлер", fontsize=7.6, color=INK2, va="bottom")
ax.annotate("формула Эйлера\nпри λ < 100 неприменима", xy=(92, np.pi ** 2 * E / 92 ** 2), xytext=(103, 283), fontsize=6.9, color=INK2,
            ha="left", va="center", linespacing=1.1, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.5, shrinkA=1, shrinkB=2))
ax.text(lam_pr + 1.5, 12, r"$\lambda_{пред}$ = 100", fontsize=7.2, color=INK2)
fig.canvas.draw()
pa, pb = ax.transData.transform([(64, a_J - b_J * 64), (76, a_J - b_J * 76)])
ax.text(70, a_J - b_J * 70 + 11, "Ясинский", fontsize=7.6, color=INK2, ha="center", va="bottom", rotation_mode="anchor",
        rotation=np.degrees(np.arctan2(pb[1] - pa[1], pb[0] - pa[0])))
lab = {6: (24, 140), rd["d"]: (24, 195)}
for r in it:
    if r["d"] in lab:
        main = r["d"] == rd["d"]
        ax.plot(r["lam"], r["sk"], "o", ms=5.5, color=ACC if main else S1, mec="white", mew=1.0, zorder=5)
        ax.annotate(f"Ø{r['d']:g}" + (" — принят" if main else "") + f"\nλ = {r['lam']:.0f}, " + r"$n_{у}$" + f" = {fmt(r['ny'], 2)}",
                    xy=(r["lam"], r["sk"]), xytext=lab[r["d"]], fontsize=7.4, ha="left", va="center", linespacing=1.2,
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6, shrinkA=2, shrinkB=4, relpos=(1, 0.5)))
fig.savefig(os.path.join(OUT, "fig13_rod_v14.png"), facecolor="white"); plt.close(fig)
print("ok")
