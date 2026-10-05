# -*- coding: utf-8 -*-
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": "#8a8a86",
                     "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})
INK, INK2, GRID, S1, SHADE = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#f1f1ee"
COMMA = FuncFormatter(lambda v, p: (f"{v:g}").replace(".", ",").replace("-", "−"))
cm = lambda s: s.replace(".", ",").replace("-", "−")
def style(ax):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
z = np.load("kin_v5.npz"); t = z["t"]; tr, tu, tt = float(z["t_r"]), float(z["t_u"]), float(z["t_t"]); T = tr + tu + tt; tp = tr + tu
def zones(ax):
    ax.axvspan(tp, T, color=SHADE, lw=0); ax.axvline(tr, color=INK2, lw=0.9, ls=(0, (4, 3)))

# ---------- ω(t), ε(t)
fig, axs = plt.subplots(2, 1, figsize=(7.6, 4.8), dpi=200, sharex=True)
for ax in axs: style(ax); zones(ax)
axs[0].plot(t, z["om"], color=S1, lw=1.6); axs[0].set_ylabel("ω, рад/с"); axs[0].set_ylim(0, 1.75)
axs[0].set_title("Угловая скорость кулисы ω(t)", color=INK)
axs[0].text(tr/2, 0.15, "разгон\n(холостой ход)", ha="center", color=INK2)
axs[0].text(tp + tt/2, 0.15, "торможение\n(пластическая деформация)", ha="center", color=INK2)
axs[0].text(tr + 0.01, 1.70, "касание с крышкой", color=INK2, fontsize=8.5, va="top", ha="left")
axs[0].annotate(cm(f"ω_max = {z['om'].max():.2f}"), (tp, z["om"].max()), xytext=(10, -16), textcoords="offset points", color=INK, fontsize=9)
# вставка: площадка упругой деформации
ins = axs[0].inset_axes([0.05, 0.58, 0.27, 0.34])
m = (t > tr - 0.012) & (t < tp + 0.012)
ins.plot(t[m]*1000, z["om"][m], color=S1, lw=1.6); ins.axvspan(tr*1000, tp*1000, color="#dbe8f7", lw=0)
ins.set_title(cm(f"упругая деформация: {tu*1000:.1f} мс"), fontsize=8.5, color=INK, loc="left", fontweight="normal")
ins.tick_params(labelsize=7); ins.set_xlabel("t, мс", fontsize=7.5)
ins.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:g}")); ins.yaxis.set_major_formatter(COMMA)
for s in ("top", "right"): ins.spines[s].set_visible(False)
axs[1].step(t, z["ep"], where="post", color=S1, lw=1.6); axs[1].axhline(0, color=INK2, lw=0.8)
axs[1].set_ylabel("ε, рад/с²"); axs[1].set_ylim(-3.6, 3.6); axs[1].set_xlabel("время t, с")
axs[1].set_title("Угловое ускорение кулисы ε(t)", color=INK)
axs[1].annotate(cm(f"+{z['ep'][1]:.2f}"), (tr/2, z["ep"][1]), xytext=(0, 6), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].annotate(cm(f"{z['ep'][-1]:.2f}"), (tp + tt/2, z["ep"][-1]), xytext=(0, -14), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig_omega_v5.png", facecolor="white"); plt.close(fig)

# ---------- ползун
fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.2), dpi=200, sharex=True)
data = ((z["y"], "y, мм", "Положение ползуна y(t)"), (z["V"], "V, мм/с", "Скорость ползуна V(t), вниз — минус"),
        (z["A"], "a, мм/с²", "Ускорение ползуна a(t)"))
for ax, (yv, lab, title) in zip(axs, data):
    style(ax); zones(ax); ax.plot(t, yv, color=S1, lw=1.6); ax.set_ylabel(lab); ax.set_title(title, color=INK)
axs[1].axhline(0, color=INK2, lw=0.8); axs[2].axhline(0, color=INK2, lw=0.8); axs[1].set_ylim(-34, 3)
i = int(np.argmin(z["V"])); axs[1].plot(t[i], z["V"][i], "o", ms=6, color=S1, mec="white", mew=1.4)
axs[1].annotate(cm(f"{z['V'][i]:.1f} мм/с"), (t[i], z["V"][i]), xytext=(-10, 4), textcoords="offset points", ha="right", color=INK, fontsize=9)
axs[0].text(tp + tt/2, z["y"].max()*0.9, "пластическая деформация", ha="center", color=INK2)
axs[2].set_xlabel("время t, с"); axs[2].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig_slider_v5.png", facecolor="white"); plt.close(fig)
print("ok")
