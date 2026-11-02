# -*- coding: utf-8 -*-
"""Рис. 14 (v19): 9 неизвестных системы уточнённого силового расчёта (только он), оформление как на рис. 9.
Данные — calc_v17.npz/json (calc_v17.py)."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.0,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 9.6, "axes.titleweight": "bold", "axes.titlelocation": "left"})
INK, INK2, GRID, S1, S3, SHADE, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#2f9e6b", "#f1f1ee", "#c4372b"
cm = lambda s: s.replace(".", ",").replace("-", "−")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))
HERE = os.path.dirname(os.path.abspath(__file__))

d = np.load(os.path.join(HERE, "calc_v17.npz"))
RJ = json.load(open(os.path.join(HERE, "calc_v17.json"), encoding="utf-8"))
phs, X1 = d["phs"], d["X1"]
PH_N, PH_K, PH_Y = float(d["phi_n"]), float(d["phi_k"]), float(d["phi_y"])
ry = next(r for r in RJ["rows"] if r["name"] == "начало пластической деформации (до)")

titles = [(r"$R_{10}^{x}$, Н", 0, ACC), (r"$R_{10}^{y}$, Н", 1, S1), (r"$R_{12}^{N}$, Н", 2, S1),
          (r"$M_{12}$, Н·мм", 3, INK), (r"$R_{23}^{x}$, Н", 4, ACC), (r"$R_{23}^{y}$, Н", 5, S1),
          (r"$R_{30}^{N}$, Н", 6, S3), (r"$M_{30}$, Н·мм", 7, INK), (r"сила руки $P$, Н", 8, "#8e44ad")]
fig, axs = plt.subplots(3, 3, figsize=(8.4, 7.0), dpi=220, sharex=True)
for ax, (tt, k, col) in zip(axs.ravel(), titles):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.axvspan(PH_Y, PH_K, color=SHADE, lw=0); ax.axhline(0, color=INK2, lw=0.7)
    ax.set_title(tt, fontsize=9.6); ax.set_xlim(PH_N + 1, PH_K - 1)
    if k in (3, 7):
        ax.set_ylim(-1, 1); ax.text(0.5, 0.62, "≡ 0", transform=ax.transAxes, ha="center", fontsize=11, color=INK2)
        continue
    ax.plot(phs, X1[:, k], color=col, lw=1.6)
    ax.plot(PH_Y, ry["X1"][k], "o", ms=4, color=ACC, zorder=6)
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.annotate(cm(f"{ry['X1'][k]:.1f}" if k == 8 else f"{ry['X1'][k]:.0f}"), (PH_Y, ry["X1"][k]),
                xytext=(-36, -3) if k == 8 else (7, 5), textcoords="offset points", fontsize=7.8, color=ACC)
axp = axs[2, 2]
axp.axhline(120, color=ACC, lw=0.9, ls=(0, (4, 3))); axp.set_ylim(-8, 135)
axp.text(PH_N, 122, r"$P_{\mathrm{доп}}$ = 120 Н", fontsize=7.8, color=ACC, va="bottom")
for ax in axs[2]:
    ax.set_xlabel("угол кулисы φ, град")
fig.text(0.5, 0.004, cm(f"L = 500 мм; рабочий ход — слева направо; серым — пластическая деформация; точки — φу = {PH_Y:.2f}°"),
         ha="center", fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(os.path.join(HERE, "fig14_unknowns_v19.png"), facecolor="white"); plt.close(fig)
print("ok")
