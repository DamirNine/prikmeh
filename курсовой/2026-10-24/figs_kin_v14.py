# -*- coding: utf-8 -*-
"""Рис. 4 и 5 (v14) — код figs_v8.py (2026-10-10): подписи «касание с крышкой», ω_max и экстремума скорости ползуна
разнесены с кривыми и друг с другом. Данные — kin_v8.npz, его пишет calc_v8.py (2026-10-10) в текущую папку;
запуск: python figs_kin_v14.py <папка с kin_v8.npz>."""
import os, sys
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
OUT = os.path.dirname(os.path.abspath(__file__))

def style(ax):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# ===================================================== кинематика (L = 500)
kz = np.load(os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "kin_v8.npz"))
t, om, ep, yD, VDy, aDy = kz["t"], kz["om"], kz["ep"], kz["y"], kz["V"], kz["A"]
t_r, t_u, t_t = float(kz["t_r"]), float(kz["t_u"]), float(kz["t_t"]); T = t_r + t_u + t_t; tp = t_r + t_u
w = float(om.max()); eps_r, eps_t = float(ep[0]), float(ep[-1])
def zones(ax):
    ax.axvspan(tp, T, color=SHADE, lw=0); ax.axvline(t_r, color=INK2, lw=0.9, ls=(0, (4, 3)))

fig, axs = plt.subplots(2, 1, figsize=(7.6, 4.8), dpi=200, sharex=True)
for ax in axs:
    style(ax); zones(ax)
axs[0].plot(t, om, color=S1, lw=1.6); axs[0].set_ylabel("ω, рад/с"); axs[0].set_ylim(0, 2.05)
axs[0].set_title("Угловая скорость кулисы ω(t)", color=INK)
axs[0].text(t_r / 2, 0.15, "разгон\n(холостой ход)", ha="center", color=INK2)
axs[0].text(tp + t_t / 2, 0.15, "торможение\n(пластическая деформация)", ha="center", color=INK2)
axs[0].text(t_r + 0.01, 2.0, "касание с крышкой", color=INK2, fontsize=8.5, va="top", ha="left")
axs[0].annotate(cm(f"ω_max = {w:.2f} рад/с").replace("ω_max", r"$\omega_{\max}$"), (tp, w), xytext=(14, 6), textcoords="offset points",
                color=INK, fontsize=9, va="bottom")
ins = axs[0].inset_axes([0.05, 0.5, 0.27, 0.3])
m = (t > t_r - 0.012) & (t < tp + 0.012)
ins.plot(t[m] * 1000, om[m], color=S1, lw=1.6); ins.axvspan(t_r * 1000, tp * 1000, color="#dbe8f7", lw=0)
ins.set_title(cm(f"упругая деформация: {t_u*1000:.1f} мс"), fontsize=8.5, color=INK, loc="left", fontweight="normal")
ins.tick_params(labelsize=7); ins.set_xlabel("t, мс", fontsize=7.5)
ins.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:g}")); ins.yaxis.set_major_formatter(COMMA)
for s in ("top", "right"):
    ins.spines[s].set_visible(False)
axs[1].step(t, ep, where="post", color=S1, lw=1.6); axs[1].axhline(0, color=INK2, lw=0.8)
axs[1].set_ylabel("ε, рад/с²"); axs[1].set_ylim(-3.9, 3.9); axs[1].set_xlabel("время t, с")
axs[1].set_title("Угловое ускорение кулисы ε(t)", color=INK)
axs[1].annotate(cm(f"+{eps_r:.2f}"), (t_r / 2, eps_r), xytext=(0, 6), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].annotate(cm(f"{eps_t:.2f}"), (tp + t_t / 2, eps_t), xytext=(0, -14), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].set_xlim(0, T)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_omega_v14.png"), facecolor="white"); plt.close(fig)

fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.6), dpi=200, sharex=True)
data = ((yD, r"$y_D$, мм", r"Координата ползуна $y_D(t)$  ($x_D = e$ = const)"),
        (VDy, r"$V_{Dy}$, мм/с", r"Проекция скорости ползуна на ось y ДСК: $V_{Dy}(t)$;  $V_{Dx}$ = 0"),
        (aDy, r"$a_{Dy}$, мм/с²", r"Проекция ускорения ползуна на ось y ДСК: $a_{Dy}(t)$;  $a_{Dx}$ = 0"))
for ax, (yv, lab, title) in zip(axs, data):
    style(ax); zones(ax); ax.plot(t, yv, color=S1, lw=1.6); ax.set_ylabel(lab); ax.set_title(title, color=INK)
axs[1].axhline(0, color=INK2, lw=0.8); axs[2].axhline(0, color=INK2, lw=0.8); axs[1].set_ylim(-36, 4)
i = int(np.argmin(VDy)); axs[1].plot(t[i], VDy[i], "o", ms=6, color=S1, mec="white", mew=1.4)
axs[1].annotate(cm(f"{VDy[i]:.1f} мм/с"), (t[i], VDy[i]), xytext=(-4, 8), textcoords="offset points", ha="right", va="bottom",
                color=INK, fontsize=9)
axs[1].text(T * 0.985, -33.5, r"$V_{Dy}<0$ — ползун движется против оси y", color=INK2, fontsize=8.6, ha="right", va="center")
axs[0].text(tp + t_t / 2, yD.max() * 0.9, "пластическая деформация", ha="center", color=INK2)
axs[0].text(t_r - 0.008, yD.max() * 0.9, "касание с крышкой", ha="right", color=INK2, fontsize=8.5)
axs[2].set_xlabel("время t, с"); axs[2].set_xlim(0, T)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig5_slider_proj_v14.png"), facecolor="white"); plt.close(fig)
print("ok")
