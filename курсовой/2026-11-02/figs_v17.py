# -*- coding: utf-8 -*-
"""Рис. 14 (v17): а) сила руки P(φ) — первичный и уточнённый расчёты, вставка — холостой ход;
б) поправки уточнённого расчёта к силе руки и реакциям. Данные — calc_v17.npz (calc_v17.py)."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.5,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 10.5, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})
INK, INK2, GRID, S1, S2, S3, SHADE, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#e3742a", "#2f9e6b", "#f1f1ee", "#c4372b"
cm = lambda s: s.replace(".", ",").replace("-", "−")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))
HERE = os.path.dirname(os.path.abspath(__file__))


def style(ax):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


d = np.load(os.path.join(HERE, "calc_v17.npz"))
phs, X0, X1 = d["phs"], d["X0"], d["X1"]
PH_N, PH_K, PH_OB, PH_Y = float(d["phi_n"]), float(d["phi_k"]), float(d["phi_ob"]), float(d["phi_y"])
import json
RJ = json.load(open(os.path.join(HERE, "calc_v17.json"), encoding="utf-8"))
P1, P0 = RJ["P1max"], RJ["P0max"]

fig, axs = plt.subplots(2, 1, figsize=(7.6, 5.7), dpi=220, sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
for ax in axs:
    style(ax); ax.axvspan(PH_Y, PH_K, color=SHADE, lw=0); ax.axhline(0, color=INK2, lw=0.7)
    ax.axvline(PH_OB, color=INK2, lw=0.9, ls=(0, (4, 3)))
    ax.set_xlim(PH_N + 1, PH_K - 1)

a = axs[0]
a.plot(phs, X0[:, 8], color=INK2, lw=1.4, ls=(0, (5, 3)), label="первичный расчёт (раздел 11)")
a.plot(phs, X1[:, 8], color="#8e44ad", lw=1.7, label="уточнённый: силы тяжести и инерции")
a.axhline(120, color=ACC, lw=0.9, ls=(0, (4, 3)))
a.text(PH_N, 122, r"$P_{\mathrm{доп}}$ = 120 Н", fontsize=8, color=ACC, va="bottom")
a.plot(PH_Y, P1, "o", ms=4, color="#8e44ad", zorder=6)
a.annotate(cm(f"{P1:.1f} Н (было {P0:.1f})"), (PH_Y, P1), xytext=(33.5, 107), textcoords="data", fontsize=8, color="#8e44ad",
           va="center", arrowprops=dict(arrowstyle="-", color="#8e44ad", lw=0.7, shrinkA=2, shrinkB=3))
a.text(PH_OB + 0.4, 85, "касание\nс крышкой", fontsize=8, color=INK2, ha="right", va="center")
a.set_ylim(-12, 140); a.set_ylabel("сила руки P, Н")
a.set_title("а) Сила руки P(φ)", color=INK)
a.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86), fontsize=8, frameon=False)
ins = a.inset_axes([0.07, 0.17, 0.36, 0.29])
m = phs >= PH_OB - 0.6
ins.plot(phs[m], X0[m, 8], color=INK2, lw=1.2, ls=(0, (5, 3)))
ins.plot(phs[m], X1[m, 8], color="#8e44ad", lw=1.5)
ins.axhline(0, color=INK2, lw=0.6); ins.set_xlim(PH_N + 0.5, PH_OB - 0.6); ins.set_ylim(-4, 1.5); ins.set_yticks([-3, -2, -1, 0, 1])
ins.xaxis.set_major_formatter(COMMA); ins.yaxis.set_major_formatter(COMMA); ins.tick_params(labelsize=7)
ins.set_title("холостой ход, Н", fontsize=7.5, loc="left", fontweight="normal", color=INK2)
ins.set_facecolor("white")

b = axs[1]
lines = [(8, "ΔP", "#8e44ad"), (2, r"$\Delta R_{12}^{N}$", S1), (0, r"$\Delta R_{10}^{x}$", ACC), (1, r"$\Delta R_{10}^{y}$", S3),
         (6, r"$\Delta R_{30}^{N}$", S2)]
for k, lab, col in lines:
    b.plot(phs, X1[:, k] - X0[:, k], color=col, lw=1.5, label=lab)
b.set_ylim(-7, 7.5); b.set_ylabel("уточнённый − первичный, Н")
b.set_title("б) Поправки к силе руки и реакциям", color=INK)
b.legend(ncol=5, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.0))
b.set_xlabel("угол кулисы φ, град")
fig.text(0.5, 0.004, "L = 500 мм; рабочий ход — слева направо; штриховая вертикаль — касание с крышкой; серым — пластическая деформация",
         ha="center", fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.02, 1, 1)); fig.savefig(os.path.join(HERE, "fig14_refined_v17.png"), facecolor="white"); plt.close(fig)
print("ok")
