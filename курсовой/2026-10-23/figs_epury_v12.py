# -*- coding: utf-8 -*-
"""Рис. 10, 11 — расчётная схема и эпюры N, Q, M кулисы при φу и φк на сплошной оси z = 0…500 мм."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "strength_v11.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.edgecolor": "#8a8a86", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "axes.titlesize": 9.8, "axes.titleweight": "bold", "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, GRID, S1, S3, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#2f9e6b", "#c4372b"
LIGHT = {S1: "#dbe8f7", S3: "#dcefe5", ACC: "#f6dcd9"}
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))
L = 500.0
XL = (-45, 515)

def arrow(ax, x0, y0, x1, y1, color=INK, lw=1.4):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=11,
                                                                   shrinkA=0, shrinkB=0), zorder=6)

def sign(ax, x, y):
    ax.text(x, y, "−", ha="center", va="center", fontsize=8.5, color=INK2, zorder=7,
            bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec=INK2, lw=0.7))

def epury(pos, fname):
    lOD, N, QOD, QDK, MD = pos["lOD"], pos["N"], pos["Q_OD"], pos["Q_DK"], pos["M_D"] / 1000
    fig, axs = plt.subplots(4, 1, figsize=(7.9, 6.6), dpi=220, sharex=True,
                            gridspec_kw=dict(height_ratios=[1.2, 0.75, 1, 1], hspace=0.55))
    ax = axs[0]
    ax.set_ylim(-1.45, 1.45); ax.set_yticks([])
    for s_ in ("left", "right", "top", "bottom"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(bottom=False)
    ax.plot([0, L], [0, 0], color=INK, lw=3.4, solid_capstyle="butt", zorder=3)
    ax.plot(0, 0, "o", ms=7.5, mfc="white", mec=INK, mew=1.4, zorder=6)
    ax.plot(lOD, 0, "s", ms=7, mfc="#f1f1ee", mec=INK, mew=1.2, zorder=6)
    ax.plot(L, 0, "o", ms=4.5, color=INK, zorder=6)
    ax.text(-4, -0.55, "O", fontsize=10, ha="right"); ax.text(lOD + 4, -0.55, "D", fontsize=10); ax.text(L - 6, 0.3, "K", fontsize=10, ha="right")
    arrow(ax, -42, 0, -3, 0, INK2)
    ax.text(-44, -0.2, r"$R_{10,u}$ = " + fmt(-N, 1) + " Н", fontsize=8.0, color=INK2, va="top")
    arrow(ax, 0, -0.05, 0, -1.25, INK2)
    ax.text(-4, -1.32, r"$R_{10,n}$ = " + fmt(QOD, 1) + " Н", fontsize=8.0, color=INK2, va="bottom", ha="right")
    arrow(ax, lOD, 0.08, lOD, 1.3, INK)
    ax.text(lOD + 5, 1.05, r"$R_{12}^{N}$ = " + fmt(pos["R12N"], 1) + " Н,  " + r"$l_{OD}$ = " + fmt(lOD, 2) + " мм", fontsize=8.2)
    arrow(ax, L, 1.3, L, 0.08, INK)
    ax.text(L - 7, 1.05, r"$P\cos\varphi$ = " + fmt(QDK, 1) + " Н", fontsize=8.2, ha="right")
    arrow(ax, L - 1, -0.42, L - 46, -0.42, INK2)
    ax.text(L - 50, -0.75, r"$P\sin\varphi$ = " + fmt(-N, 1) + " Н", fontsize=8.2, ha="right", color=INK2)
    ax.text(250, 0.3, "L = 500 мм", fontsize=8.4, color=INK2, ha="center")
    ax.set_title(f"Расчётная схема кулисы при φ = {fmt(pos['phi'], 2)}° (силы — по оси u и нормали n звена)", color=INK)

    def diag(ax, zs, ys, color, ylab, title, lims):
        ax.fill_between(zs, 0, ys, facecolor=LIGHT[color], edgecolor=color, hatch="||", lw=0, zorder=2)
        ax.plot(zs, ys, color=color, lw=1.6, zorder=3)
        ax.axhline(0, color=INK, lw=1.0, zorder=4)
        ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
        ax.set_ylim(*lims); ax.set_ylabel(ylab); ax.set_title(title, color=INK)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        ax.yaxis.set_major_formatter(COMMA)
    diag(axs[1], np.array([0, L]), np.array([N, N]), S3, "N, Н", "Эпюра N — продольная сила (сжатие)", (-130, 60))
    axs[1].text(250, N - 18, fmt(N, 1), ha="center", va="top", fontsize=8.6); sign(axs[1], 120, N / 2)
    diag(axs[2], np.array([0, lOD, lOD, L]), np.array([QOD, QOD, QDK, QDK]), S1, "Q, Н", "Эпюра Q — поперечная сила", (-2900, 700))
    axs[2].text(lOD + 6, QOD + 150, fmt(QOD, 1) + " (участок O–D)", ha="left", va="bottom", fontsize=8.6)
    axs[2].text(250, QDK + 90, "+" + fmt(QDK, 1), ha="center", va="bottom", fontsize=8.6)
    diag(axs[3], np.array([0, lOD, L]), np.array([0, MD, 0]), ACC, "M, Н·м", "Эпюра M — изгибающий момент", (-52, 12))
    axs[3].plot(lOD, MD, "o", ms=4.5, color=ACC, zorder=6)
    axs[3].text(lOD + 6, MD - 1.0, fmt(MD, 2) + " (под камнем, z = " + fmt(lOD, 2) + " мм)", ha="left", va="top", fontsize=8.6)
    sign(axs[3], 200, MD * 0.3)
    axs[3].set_xlim(*XL); axs[3].set_xticks(np.arange(0, 501, 50)); axs[3].xaxis.set_major_formatter(COMMA)
    axs[3].set_xlabel("z — расстояние от оси O вдоль звена, мм")
    fig.subplots_adjust(left=0.09, right=0.985, top=0.95, bottom=0.08)
    fig.savefig(os.path.join(OUT, fname), facecolor="white"); plt.close(fig)

epury(R["A"], "fig10_epury_phiy_v12.png")
epury(R["B"], "fig11_epury_phik_v12.png")
print("ok")
