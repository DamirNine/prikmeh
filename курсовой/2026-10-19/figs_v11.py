# -*- coding: utf-8 -*-
"""Рисунки раздела 12 (v11): 10, 11 — эпюры N, Q, M кулисы при φу и φк; 12 — схемы и эпюры элементов из прутка
(палец D, ось O, шток ползуна); 13 — стенка паза: схема и эпюра местного момента; 14 — эскиз кулисы с сечениями."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.ticker import FuncFormatter

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "strength_v11.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 9.8, "axes.titleweight": "bold",
                     "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, GRID, S1, S2, S3, SHADE, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#e3742a", "#2f9e6b", "#f1f1ee", "#c4372b"
LIGHT = {S1: "#dbe8f7", S3: "#dcefe5", ACC: "#f6dcd9", S2: "#fbe6d6"}
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))
L = 500.0
F_ = R["fin"]
A_, B_ = R["A"], R["B"]
b = F_["b"]; H = F_["slotsec"]["H"]; w = F_["stone"]["w"]; lk = F_["stone"]["lk"]; t = F_["slotsec"]["A"]["t"]
h = F_["handle"]["h"]; a1, a2, span = F_["slot"]["a1"], F_["slot"]["a2"], F_["slot"]["span"]
dD, dO, Dh, lh = F_["pinD"]["d"], F_["axO"]["d"], F_["axO"]["Dh"], F_["axO"]["lh"]
z1, lt = F_["kul"]["z1"], F_["kul"]["lt"]


def arrow(ax, x0, y0, x1, y1, color=INK, lw=1.4, ms=11):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                                   shrinkA=0, shrinkB=0), zorder=6)


def sign(ax, x, y, s):
    ax.text(x, y, s, ha="center", va="center", fontsize=8.5, color=INK2, zorder=7,
            bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec=INK2, lw=0.7))


# ====================================================================== рис. 10, 11 — эпюры кулисы
def epury(pos, fname):
    lOD, N, QOD, QDK, MD = pos["lOD"], pos["N"], pos["Q_OD"], pos["Q_DK"], pos["M_D"] / 1000
    phi = pos["phi"]
    fig = plt.figure(figsize=(7.9, 6.4), dpi=220)
    gs = fig.add_gridspec(4, 2, width_ratios=[1, 2.35], height_ratios=[1.15, 0.75, 1, 1], wspace=0.04, hspace=0.62)
    XL, XR = (-13.0, 42.0), (42.0, 512.0)
    rows = []
    for r in range(4):
        aL = fig.add_subplot(gs[r, 0]); aR = fig.add_subplot(gs[r, 1], sharey=aL)
        aL.set_xlim(*XL); aR.set_xlim(*XR)
        for a in (aL, aR):
            a.spines["top"].set_visible(False); a.xaxis.set_major_formatter(COMMA); a.yaxis.set_major_formatter(COMMA)
        aL.spines["right"].set_visible(False); aR.spines["left"].set_visible(False); aR.tick_params(left=False, labelleft=False)
        aL.set_xticks([0, 10, 20, 30, 40]); aR.set_xticks([100, 200, 300, 400, 500])
        rows.append((aL, aR))
    aL, aR = rows[0]
    for a in (aL, aR):
        a.set_ylim(-1.35, 1.35); a.set_yticks([]); a.spines["left"].set_visible(False); a.spines["bottom"].set_visible(False)
        a.set_xticks([])
        a.plot([0, L], [0, 0], color=INK, lw=3.4, solid_capstyle="butt", zorder=3)
    aL.plot([41, 43], [-0.22, 0.22], color="white", lw=6, zorder=4); aL.plot([40.2, 41.8], [-0.25, 0.25], color=INK, lw=0.9, zorder=5)
    aR.plot([42.2, 43.8], [-0.25, 0.25], color=INK, lw=0.9, zorder=5)
    aL.plot(0, 0, "o", ms=7.5, mfc="white", mec=INK, mew=1.4, zorder=6)
    aL.plot(lOD, 0, "s", ms=8, mfc=SHADE, mec=INK, mew=1.2, zorder=6)
    aR.plot(L, 0, "o", ms=4.5, color=INK, zorder=6)
    aL.text(-1.6, -0.62, "O", fontsize=10, ha="right"); aL.text(lOD + 1.8, -0.62, "D", fontsize=10); aR.text(L - 4, 0.30, "K", fontsize=10, ha="right")
    arrow(aL, -12.0, 0.0, -0.9, 0.0, color=INK2)
    aL.text(-6.5, 0.16, r"$R_{10,u}$", fontsize=8.2, color=INK2, ha="center", va="bottom")
    aL.text(-6.5, -0.16, fmt(-N, 1) + " Н", fontsize=8.0, color=INK2, ha="center", va="top")
    arrow(aL, 0.0, -0.05, 0.0, -1.2, color=INK2)
    aL.text(1.4, -1.22, r"$R_{10,n}$ = " + fmt(QOD, 1) + " Н", fontsize=8.2, color=INK2, va="bottom")
    arrow(aL, lOD, 0.08, lOD, 1.25, color=INK)
    aL.text(lOD + 1.6, 1.0, r"$R_{12}^{N}$ = " + fmt(pos["R12N"], 1) + " Н", fontsize=8.2)
    aL.annotate("", xy=(0, 0.55), xytext=(lOD, 0.55), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    aL.text(lOD - 0.8, 0.66, r"$l_{OD}$ = " + fmt(lOD, 2), fontsize=7.8, color=INK2, ha="right", va="bottom")
    arrow(aR, L, 1.25, L, 0.08, color=INK)
    aR.text(L - 6, 1.05, r"$P\cos\varphi$ = " + fmt(QDK, 1) + " Н", fontsize=8.2, ha="right")
    arrow(aR, L - 1, -0.38, L - 46, -0.38, color=INK2)
    aR.text(L - 50, -0.72, r"$P\sin\varphi$ = " + fmt(-N, 1) + " Н", fontsize=8.2, ha="right", color=INK2)
    aR.text(250, 0.42, "L = 500 мм", fontsize=8.4, color=INK2, ha="center")
    aL.set_title(f"Расчётная схема кулисы при φ = {fmt(phi, 2)}° (силы — по оси u и нормали n звена)", loc="left", color=INK)

    def diag(r, zs, ys, color, ylab, title, lims):
        aL_, aR_ = rows[r]
        for a in (aL_, aR_):
            a.fill_between(zs, 0, ys, facecolor=LIGHT[color], edgecolor=color, hatch="||", lw=0, zorder=2)
            a.plot(zs, ys, color=color, lw=1.6, zorder=3)
            a.axhline(0, color=INK, lw=1.0, zorder=4)
            a.grid(True, axis="y", color=GRID, lw=0.7); a.set_axisbelow(True)
        aL_.set_ylim(*lims); aL_.set_ylabel(ylab)
        aL_.set_title(title, loc="left", color=INK)
        d = 0.018
        aL_.plot((1 - d, 1 + d), (-0.04, 0.04), transform=aL_.transAxes, color=INK2, lw=0.8, clip_on=False)
        aR_.plot((-d * 0.42, d * 0.42), (-0.04, 0.04), transform=aR_.transAxes, color=INK2, lw=0.8, clip_on=False)
        return aL_, aR_

    aL_, aR_ = diag(1, np.array([0, L]), np.array([N, N]), S3, "N, Н", "Эпюра N — продольная сила (сжатие)", (-130, 60))
    aR_.text(250, N - 18, fmt(N, 1), ha="center", va="top", fontsize=8.6); sign(aR_, 120, N / 2, "−"); sign(aL_, 20, N / 2, "−")
    zq = np.array([0, lOD, lOD, L]); yq = np.array([QOD, QOD, QDK, QDK])
    aL_, aR_ = diag(2, zq, yq, S1, "Q, Н", "Эпюра Q — поперечная сила", (-2900, 600))
    aL_.text(lOD / 2, QOD - 80, fmt(QOD, 1), ha="center", va="top", fontsize=8.6)
    aL_.text(lOD + 1.5, QDK + 90, "+" + fmt(QDK, 1), ha="left", va="bottom", fontsize=8.6)
    aR_.text(250, QDK + 90, "+" + fmt(QDK, 1), ha="center", va="bottom", fontsize=8.6)
    sign(aL_, lOD / 2, QOD / 2, "−")
    zm = np.array([0, lOD, L]); ym = np.array([0, MD, 0])
    aL_, aR_ = diag(3, zm, ym, ACC, "M, Н·м", "Эпюра M — изгибающий момент", (-50, 12))
    aL_.plot(lOD, MD, "o", ms=4.5, color=ACC, zorder=6)
    aL_.text(lOD, MD - 1.6, fmt(MD, 2), ha="center", va="top", fontsize=8.6)
    sign(aR_, 150, MD * 0.35, "−")
    fig.text(0.56, 0.012, "z — расстояние от оси O вдоль звена, мм   (слева — участок у оси O в увеличенном масштабе)",
             ha="center", fontsize=8.6, color=INK2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.95, bottom=0.085)
    fig.savefig(os.path.join(OUT, fname), facecolor="white"); plt.close(fig)


epury(A_, "fig10_epury_phiy_v11.png")
epury(B_, "fig11_epury_phik_v11.png")


# ====================================================================== рис. 12 — элементы из прутка
def hatch_wall(ax, x0, x1, y0, y1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#dcdcd8", ec=INK, lw=0.9, hatch="////", zorder=1))


def epure_ax(ax, xs, ys, color, ylab, lims, xlim):
    ax.fill_between(xs, 0, ys, facecolor=LIGHT[color], edgecolor=color, hatch="||", lw=0, zorder=2)
    ax.plot(xs, ys, color=color, lw=1.6, zorder=3)
    ax.axhline(0, color=INK, lw=1.0, zorder=4)
    ax.set_ylim(*lims); ax.set_xlim(*xlim); ax.set_ylabel(ylab)
    ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)


fig = plt.figure(figsize=(7.9, 6.2), dpi=220)
gs = fig.add_gridspec(3, 3, height_ratios=[1.05, 0.8, 0.8], width_ratios=[1, 1.25, 1.1], hspace=0.55, wspace=0.42)
# --- а) палец D: заделка в ползуне, нагрузка от камня распределена по толщине камня b
pD = F_["pinD"]; g_ = 1.0; RD = pD["R"]
ax = fig.add_subplot(gs[0, 0])
ax.set_xlim(-9, 13); ax.set_ylim(-9, 13); ax.set_aspect("equal"); ax.axis("off")
hatch_wall(ax, -8, 0, -7, 7)
ax.text(-4, 7.8, "ползун", ha="center", fontsize=7.8, color=INK2)
ax.add_patch(Rectangle((0, -dD / 2), g_ + b, dD, fc="white", ec=INK, lw=1.2, zorder=3))
ax.add_patch(Rectangle((g_, -w / 2 + 2), b, w - 4, fc="none", ec=INK2, lw=0.8, ls=(0, (3, 2)), zorder=2))
ax.text(g_ + b + 0.6, -w / 2 + 2.6, "камень", ha="left", va="center", fontsize=7.6, color=INK2)
for xq in np.linspace(g_ + 0.6, g_ + b - 0.6, 5):
    arrow(ax, xq, 6.5, xq, dD / 2 + 0.1, color=INK, lw=1.0, ms=7)
ax.plot([g_ + 0.6, g_ + b - 0.6], [6.5, 6.5], color=INK, lw=1.0)
ax.text(g_ + b / 2, 7.2, r"$R_{23}$ = " + fmt(RD, 0) + " Н", ha="center", va="bottom", fontsize=7.8)
ax.annotate("", xy=(0, -6.8), xytext=(g_ + b / 2, -6.8), arrowprops=dict(arrowstyle="<->", color=ACC, lw=0.8))
ax.text((g_ + b / 2) / 2, -7.4, "a = " + fmt(pD["a"], 0), ha="center", va="top", fontsize=7.6, color=ACC)
ax.set_title(f"а) палец D Ø{dD:g} (φу)", loc="left", fontsize=9.2)
x = np.linspace(0, g_ + b, 400)
Qx = np.where(x <= g_, RD, RD * (g_ + b - x) / b)
Mx = np.where(x <= g_, RD * (g_ + b / 2 - x), RD * (g_ + b - x) ** 2 / (2 * b)) / 1000
ax = fig.add_subplot(gs[1, 0]); epure_ax(ax, x, Qx, S1, "Q, Н", (0, 3200), (-1, g_ + b + 1))
ax.text(0.3, RD + 120, fmt(RD, 0), fontsize=7.8, va="bottom"); ax.set_title("Эпюра Q", loc="left", fontsize=9)
ax = fig.add_subplot(gs[2, 0]); epure_ax(ax, x, Mx, ACC, "M, Н·м", (0, 16), (-1, g_ + b + 1))
ax.text(0.3, Mx[0] + 0.6, fmt(Mx[0], 2), fontsize=7.8, va="bottom"); ax.set_title("Эпюра M", loc="left", fontsize=9)
ax.set_xlabel("x от торца ползуна, мм")
# --- б) ось O: заделка в стойке; сила R10 приведена к середине планки (плечо a = g + l_ст + b/2)
aO = F_["axO"]; RO = aO["R"]; aa = aO["a"]
ax = fig.add_subplot(gs[0, 1])
ax.set_xlim(-10, 30); ax.set_ylim(-20, 21); ax.set_aspect("equal"); ax.axis("off")
hatch_wall(ax, -9, 0, -16, 16)
ax.text(-4.5, -16.8, "стойка", ha="center", va="top", fontsize=7.8, color=INK2)
ax.add_patch(Rectangle((g_, -Dh / 2), lh, Dh, fc="#e9eef5", ec=INK, lw=0.9, zorder=1))
ax.text(g_ + lh / 2 - 2, Dh / 2 + 0.8, f"ступица Ø{Dh:g}", ha="center", fontsize=7.6, color=INK2)
ax.add_patch(Rectangle((g_ + lh, -19), b, 38, fc="#e9eef5", ec=INK, lw=0.9, zorder=1))
ax.text(g_ + lh + b / 2, -19.6, "планка", ha="center", va="top", fontsize=7.6, color=INK2)
ax.add_patch(Rectangle((-6, -dO / 2), 6 + g_ + lh, dO, fc="white", ec=S1, lw=1.2, zorder=3))
ax.plot([0, aa], [0, 0], color=INK2, lw=0.6, ls=(0, (4, 2)), zorder=4)
arrow(ax, aa, 13.5, aa, 0.4, color=INK, lw=1.3, ms=9)
ax.text(aa + 0.8, 11.5, r"$R_{10}$ = " + fmt(RO, 0) + " Н", ha="left", fontsize=7.8,
        bbox=dict(fc="white", ec="none", pad=0.5))
ax.annotate("", xy=(0, -13.5), xytext=(aa, -13.5), arrowprops=dict(arrowstyle="<->", color=ACC, lw=0.8))
ax.text(aa / 2, -14.1, "a = " + fmt(aa, 0), ha="center", va="top", fontsize=7.6, color=ACC,
        bbox=dict(fc="white", ec="none", pad=0.3))
ax.set_title(f"б) ось O Ø{dO:g} (φу)", loc="left", fontsize=9.2)
x = np.linspace(0, aa, 300)
ax = fig.add_subplot(gs[1, 1]); epure_ax(ax, x, np.full_like(x, RO), S1, "Q, Н", (0, 3200), (-1, aa + 1))
ax.text(0.5, RO + 120, fmt(RO, 0), fontsize=7.8, va="bottom"); ax.set_title("Эпюра Q", loc="left", fontsize=9)
ax = fig.add_subplot(gs[2, 1]); epure_ax(ax, x, RO * (aa - x) / 1000, ACC, "M, Н·м", (0, 64), (-1, aa + 1))
ax.text(0.5, RO * aa / 1000 + 2, fmt(RO * aa / 1000, 2), fontsize=7.8, va="bottom"); ax.set_title("Эпюра M", loc="left", fontsize=9)
ax.set_xlabel("x от торца стойки, мм")
# --- в) шток ползуна: сжатие силой обжима (φк)
rd = F_["rod"]; Fr = rd["F"]; lr = 60.0
ax = fig.add_subplot(gs[0, 2])
ax.set_xlim(-14, 90); ax.set_ylim(-26, 26); ax.set_aspect("equal"); ax.axis("off")
hatch_wall(ax, -12, 0, -14, -8); hatch_wall(ax, -12, 0, 8, 14)
ax.text(-6, 15, "направляющая", ha="center", va="bottom", fontsize=7.6, color=INK2)
ax.add_patch(Rectangle((-12, -rd["d"] / 2), 12 + lr, rd["d"], fc="white", ec=INK, lw=1.2, zorder=3))
ax.add_patch(Polygon([[lr, -11], [lr + 8, -11], [lr + 8, 11], [lr, 11]], closed=True, fc="#e9eef5", ec=INK, lw=0.9, zorder=2))
ax.text(lr + 4, -12, "головка", ha="center", va="top", fontsize=7.6, color=INK2)
arrow(ax, lr + 22, 0, lr + 8.3, 0, color=S3, lw=1.4, ms=9)
ax.text(lr + 16, 12.5, r"$F_{ук}$ = " + fmt(Fr, 0) + " Н", ha="center", va="bottom", fontsize=7.8, color=S3)
ax.annotate("", xy=(0, -20), xytext=(lr, -20), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(lr / 2, -20.6, "l = 60", ha="center", va="top", fontsize=7.6, color=INK2)
ax.set_title(f"в) шток ползуна Ø{rd['d']:g} (φк)", loc="left", fontsize=9.2)
ax = fig.add_subplot(gs[1, 2]); x = np.array([0, lr])
epure_ax(ax, x, np.array([-Fr, -Fr]), S3, "N, Н", (-2600, 400), (-2, lr + 2))
ax.text(lr / 2, -Fr - 90, fmt(-Fr, 0), ha="center", va="top", fontsize=7.8); sign(ax, 12, -Fr / 2, "−")
ax.set_title("Эпюра N", loc="left", fontsize=9); ax.set_xlabel("x от направляющей, мм")
ax = fig.add_subplot(gs[2, 2]); ax.axis("off")
ax.text(0.0, 0.85, "Q = 0, M = 0: поперечная сила\nнаправляющей приложена\nна уровне пальца D (п. 11.3)",
        transform=ax.transAxes, fontsize=8.0, color=INK2, va="top")
fig.subplots_adjust(left=0.095, right=0.99, top=0.95, bottom=0.07)
fig.savefig(os.path.join(OUT, "fig12_bars_v11.png"), facecolor="white"); plt.close(fig)

# ====================================================================== рис. 13 — стенка паза: местный изгиб
we = R["wall_epure"]; xw = np.array(we["x"]); Mw = np.array(we["M"]) / 1000
c = A_["lOD"] - a1; R12 = A_["R12N"]
fig = plt.figure(figsize=(7.9, 4.6), dpi=220)
gs = fig.add_gridspec(2, 2, width_ratios=[0.62, 1.38], height_ratios=[1, 1], hspace=0.55, wspace=0.18)
# а) сечение А–А
ax = fig.add_subplot(gs[:, 0])
ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-16, 26); ax.set_ylim(-H / 2 - 10, H / 2 + 9)
for y0 in (-H / 2, w / 2):
    ax.add_patch(Rectangle((0, y0), b, t, fc="#e9eef5", ec=INK, lw=1.0, hatch="////", zorder=2))
ax.add_patch(Rectangle((0.6, -w / 2 + 0.3), b - 1.2, w - 0.6, fc="none", ec=INK2, lw=0.8, ls=(0, (3, 2)), zorder=2))
ax.text(b / 2, -3.3, "камень", ha="center", va="center", fontsize=6.8, color=INK2, rotation=90)
ax.annotate("", xy=(0, -H / 2 - 4), xytext=(b, -H / 2 - 4), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(b / 2, -H / 2 - 4.8, f"b = {b:g}", ha="center", va="top", fontsize=7.8, color=INK2)
ax.annotate("", xy=(-4, -H / 2), xytext=(-4, H / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(-4.8, 0, f"H = {H:g}", ha="right", va="center", fontsize=7.8, color=INK2)
ax.annotate("", xy=(b + 3, -w / 2), xytext=(b + 3, w / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(b + 3.8, 0, f"w = {w:g}", va="center", fontsize=7.8, color=INK2)
ax.text(b + 1.5, H / 2 - t / 2, f"t = {t:g}", va="center", fontsize=7.8, color=INK2)
ax.text(b + 1.5, -H / 2 + t / 2, f"t = {t:g}", va="center", fontsize=7.8, color=INK2)
arrow(ax, b / 2, 1.0, b / 2, w / 2 - 0.2, color=ACC, lw=1.2, ms=8)
ax.set_title("а) сечение А–А", loc="left", fontsize=9.2)
# б) расчётная схема стенки
ax = fig.add_subplot(gs[0, 1])
ax.set_xlim(-4, span + 4); ax.set_ylim(-5, 9); ax.axis("off")
hatch_wall(ax, -3, 0, -2.4, 2.4); hatch_wall(ax, span, span + 3, -2.4, 2.4)
ax.add_patch(Rectangle((0, -0.9), span, 1.8, fc="#e9eef5", ec=INK, lw=1.1, zorder=2))
x0, x1 = c - lk / 2, c + lk / 2
for xq in np.linspace(x0 + 0.4, x1 - 0.4, 8):
    arrow(ax, xq, -4.2, xq, -1.0, color=ACC, lw=1.0, ms=7)
ax.plot([x0 + 0.4, x1 - 0.4], [-4.2, -4.2], color=ACC, lw=1.0)
ax.text(c, -4.7, r"$q = R_{12}^{N}/l_к$ = " + fmt(R12, 0) + "/" + fmt(lk, 0) + " = " + fmt(R12 / lk, 0) + " Н/мм",
        ha="center", va="top", fontsize=7.8, color=ACC)
ax.annotate("", xy=(0, 3.4), xytext=(span, 3.4), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(span / 2, 3.9, "ℓ = a₂ − a₁ = " + fmt(span, 2) + " мм", ha="center", va="bottom", fontsize=7.8, color=INK2)
ax.annotate("", xy=(0, 1.6), xytext=(c, 1.6), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7))
ax.text(c / 2, 1.9, "c = " + fmt(c, 2), ha="center", va="bottom", fontsize=7.4, color=INK2)
ax.set_title("б) стенка паза — балка с заделанными концами (φу)", loc="left", fontsize=9.2)
# в) эпюра местного момента
ax = fig.add_subplot(gs[1, 1])
epure_ax(ax, xw, Mw, ACC, r"$M_{м}$, Н·м", (min(Mw.min() * 1.35, -1), Mw.max() * 1.45), (-1, span + 1))
i0, i1 = 0, len(Mw) - 1; im = int(np.argmax(Mw))
for i_, ha in ((i0, "left"), (i1, "right"), (im, "center")):
    yy = Mw[i_]
    ax.plot(xw[i_], yy, "o", ms=3.6, color=ACC, zorder=6)
    ax.text(xw[i_] + (0.5 if ha == "left" else (-0.5 if ha == "right" else 0)), yy + (0.35 if yy > 0 else -0.35), fmt(yy, 2),
            ha=ha, va="bottom" if yy > 0 else "top", fontsize=7.8)
ax.set_xlabel("x от конца паза a₁, мм"); ax.set_title("в) эпюра местного изгибающего момента стенки", loc="left", fontsize=9.2)
fig.subplots_adjust(left=0.03, right=0.99, top=0.94, bottom=0.11)
fig.savefig(os.path.join(OUT, "fig13_wall_v11.png"), facecolor="white"); plt.close(fig)


# ====================================================================== рис. 14 — эскиз кулисы и сечения
def outline_y(z):
    z = np.asarray(z, float)
    return np.where(z <= z1, H / 2, np.where(z <= z1 + lt, H / 2 + (h / 2 - H / 2) * (z - z1) / lt, h / 2))


def link_patch(ax, zmax=L):
    th = np.linspace(np.pi / 2, 3 * np.pi / 2, 60)
    zz = np.linspace(0, zmax, 500)
    arc = np.column_stack([np.cos(th) * H / 2, np.sin(th) * H / 2])
    ax.add_patch(Polygon(np.vstack([[[0, H / 2]], arc, [[0, -H / 2]], np.column_stack([zz, -outline_y(zz)]),
                                    np.column_stack([zz[::-1], outline_y(zz[::-1])])]),
                         closed=True, fc="#e9eef5", ec=INK, lw=1.0, zorder=1))
    ax.add_patch(Rectangle((a1, -w / 2), a2 - a1, w, fc="white", ec=INK, lw=0.9, zorder=2))


def dim_h(ax, x0, x1, y, txt, col=INK2, fs=7.8):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=col, lw=0.8))
    ax.text((x0 + x1) / 2, y + 0.6, txt, ha="center", va="bottom", fontsize=fs, color=col)


fig = plt.figure(figsize=(7.9, 4.9), dpi=220)
gs = fig.add_gridspec(2, 3, height_ratios=[0.40, 1.2], width_ratios=[1.6, 0.6, 0.6], hspace=0.10, wspace=0.08)
ax0 = fig.add_subplot(gs[0, :]); ax1 = fig.add_subplot(gs[1, 0]); ax2 = fig.add_subplot(gs[1, 1]); ax3 = fig.add_subplot(gs[1, 2])
ax = ax0; link_patch(ax)
ax.set_aspect("equal"); ax.set_xlim(-24, 512); ax.set_ylim(-34, 30); ax.axis("off")
ax.plot([-22, 508], [0, 0], color=INK2, lw=0.5, ls=(0, (10, 2, 1, 2)))
ax.add_patch(Circle((0, 0), Dh / 2, fc="none", ec=S1, lw=0.8, ls=(0, (3, 2)), zorder=3))
for zc_, lab in ((A_["lOD"], "А"), (300.0, "Б")):
    ax.plot([zc_, zc_], [-24, 24], color=INK, lw=0.8, ls=(0, (6, 2)))
    ax.text(zc_ + 2, 22, lab, fontsize=9); ax.text(zc_ + 2, -27, lab, fontsize=9)
dim_h(ax, 0, L, -31, "L = 500", fs=8.2)
ax.text(L - 2, h / 2 + 2, f"рукоять {b:g} × {h:g}", fontsize=7.8, color=INK2, ha="right")
ax.set_title(f"а) общий вид звена 1 — лист Ст3сп {b:g} мм (штриховая окружность — ступица позади планки)", loc="left", fontsize=9.2)
ax = ax1; link_patch(ax, zmax=110)
ax.set_aspect("equal"); ax.set_xlim(-22, 112); ax.set_ylim(-36, 27); ax.axis("off")
ax.plot([100, 100], [-H / 2 - 3, H / 2 + 3], color="white", lw=6, zorder=3); ax.plot([99, 101], [-H / 2 - 3, H / 2 + 3], color=INK2, lw=0.8, zorder=4)
ax.plot([-20, 98], [0, 0], color=INK2, lw=0.5, ls=(0, (10, 2, 1, 2)))
zc = A_["lOD"]
ax.add_patch(Rectangle((zc - lk / 2, -w / 2), lk, w, fc=SHADE, ec=INK, lw=1.0, hatch="////", zorder=5))
ax.add_patch(Circle((zc, 0), dD / 2, fc="white", ec=INK, lw=0.9, zorder=6))
ax.add_patch(Circle((0, 0), Dh / 2, fc="none", ec=S1, lw=0.8, ls=(0, (3, 2)), zorder=3))
ax.add_patch(Circle((0, 0), dO / 2, fc="none", ec=S1, lw=0.8, ls=(0, (3, 2)), zorder=3))
dim_h(ax, 0, a1, -H / 2 - 4, fmt(a1, 1)); dim_h(ax, 0, a2, -H / 2 - 10, fmt(a2, 1))
dim_h(ax, 0, z1, -H / 2 - 16, fmt(z1, 1))
dim_h(ax, z1, z1 + lt, -H / 2 - 16, "переход " + fmt(lt, 0))
for x_ in (a1, a2):
    ax.plot([x_, x_], [-w / 2, -H / 2 - 11], color=INK2, lw=0.5)
ax.plot([0, 0], [-H / 2, -H / 2 - 17], color=INK2, lw=0.5)
ax.plot([z1, z1], [-H / 2, -H / 2 - 17], color=INK2, lw=0.5); ax.plot([z1 + lt] * 2, [-h / 2, -H / 2 - 17], color=INK2, lw=0.5)
ax.annotate("", xy=(z1 - 3, -H / 2), xytext=(z1 - 3, H / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(z1 - 3.8, H / 2 - 4, f"H = {H:g}", ha="right", va="center", fontsize=7.8, color=INK2,
        bbox=dict(fc="#e9eef5", ec="none", pad=0.4))
ax.annotate("", xy=(z1 + lt + 6, -h / 2), xytext=(z1 + lt + 6, h / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(z1 + lt + 7, h / 2 + 1.0, f"h = {h:g}", ha="left", va="bottom", fontsize=7.8, color=INK2)
ax.text(-21, 23.5, f"камень {w:g}×{lk:g}×{b:g} при φу, палец D Ø{dD:g}; паз w = {w:g}", fontsize=7.8, color=INK2)
ax.set_title("б) зона паза (крупно)", loc="left", fontsize=9.2)


def sec(ax, title, parts, Htot):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-14, 22); ax.set_ylim(-H / 2 - 9, H / 2 + 9)
    for (y0, hh) in parts:
        ax.add_patch(Rectangle((0, y0), b, hh, fc="#e9eef5", ec=INK, lw=1.0, hatch="////", zorder=2))
    ax.annotate("", xy=(0, -Htot / 2 - 4), xytext=(b, -Htot / 2 - 4), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(b / 2, -Htot / 2 - 4.8, f"b = {b:g}", ha="center", va="top", fontsize=7.8, color=INK2)
    ax.annotate("", xy=(-4, -Htot / 2), xytext=(-4, Htot / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(-4.8, 0, f"{Htot:g}", ha="right", va="center", fontsize=7.8, color=INK2)
    ax.set_title(title, loc="left", fontsize=9.2)


sec(ax2, "в) А–А", [(-H / 2, t), (w / 2, t)], H)
ax2.annotate("", xy=(b + 3, -w / 2), xytext=(b + 3, w / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax2.text(b + 3.8, 0, f"{w:g}", va="center", fontsize=7.8, color=INK2)
ax2.text(b + 1.5, H / 2 - t / 2, f"t = {t:g}", va="center", fontsize=7.8, color=INK2)
sec(ax3, "г) Б–Б", [(-h / 2, h)], h)
fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.02)
fig.savefig(os.path.join(OUT, "fig14_kulisa_v11.png"), facecolor="white"); plt.close(fig)
print("ok")
