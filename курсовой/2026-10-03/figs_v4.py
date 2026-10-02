# -*- coding: utf-8 -*-
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": "#8a8a86",
                     "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})
INK, INK2, GRID, S1, HL, SHADE = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#eb6834", "#f1f1ee"

from matplotlib.ticker import FuncFormatter
COMMA = FuncFormatter(lambda v, p: (f"{v:g}").replace(".", ",").replace("-", "−"))
def style(ax):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

# ---------- 1. граница оптимизации: A(ψ) и L(ψ) — две панели, без двойной оси
d = json.load(open("frontier.json", encoding="utf-8"))["rows"]
psi = np.array([r["psi"] for r in d]); A = np.array([r["A"] for r in d]); L = np.array([r["L"] for r in d])
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.4), dpi=200)
for ax, yv, title, ylab in ((axs[0], A, "Наименьшая площадь треугольника O–Bн–Bк", "A, мм²"),
                            (axs[1], L, "Длина рукояти для этого варианта", "L, мм")):
    style(ax); ax.plot(psi, yv, color=S1, lw=1.6)
    k = int(np.argmin(np.abs(psi - 40.0)))
    ax.plot(psi[k], yv[k], "o", ms=7, color=HL, mec="white", mew=1.6, zorder=5)
    ax.annotate((f"ψ = 40°: {yv[k]:.1f}" if ax is axs[0] else f"ψ = 40°: {yv[k]:.0f}").replace(".", ","), (psi[k], yv[k]),
                xytext=(10, 10), textcoords="offset points", color=INK, fontsize=9)
    ax.set_title(title, color=INK); ax.set_xlabel("угловой ход кулисы ψ, град"); ax.set_ylabel(ylab)
    ax.set_xlim(29, 60)
axs[0].set_ylim(0, 240); axs[1].set_ylim(0, 550)
fig.tight_layout(); fig.savefig("fig_frontier.png", facecolor="white"); plt.close(fig)

# ---------- 2. ω(t) и ε(t)
z = np.load("kin40.npz"); t = z["t"]; tr, tu, tt = float(z["t_r"]), float(z["t_u"]), float(z["t_t"]); T = tr + tu + tt
fig, axs = plt.subplots(2, 1, figsize=(7.6, 4.6), dpi=200, sharex=True)
for ax in axs:
    style(ax); ax.axvspan(tr + tu, T, color=SHADE, lw=0); ax.axvline(tr + tu, color=INK2, lw=0.9, ls=(0, (4, 3)))
axs[0].plot(t, z["om"], color=S1, lw=1.6); axs[0].set_ylabel("ω, рад/с"); axs[0].set_ylim(0, 1.6)
axs[0].set_title("Угловая скорость кулисы ω(t)", color=INK)
axs[0].text(tr/2, 0.2, "разгон", ha="center", color=INK2); axs[0].text(tr + tu + tt/2, 0.2, "торможение\n(обжим)", ha="center", color=INK2)
axs[0].annotate(f"ω_max = {z['om'].max():.2f}".replace(".", ","), (tr + tu, z["om"].max()), xytext=(10, 2), textcoords="offset points", color=INK, fontsize=9)
axs[0].text(tr + tu - 0.01, 1.55, "начало деформации", color=INK2, fontsize=8.5, va="top", ha="right")
axs[1].step(t, z["ep"], where="post", color=S1, lw=1.6); axs[1].axhline(0, color=INK2, lw=0.8)
axs[1].set_ylabel("ε, рад/с²"); axs[1].set_ylim(-3.5, 3.5); axs[1].set_xlabel("время t, с")
axs[1].set_title("Угловое ускорение кулисы ε(t)", color=INK)
axs[1].annotate(f"+{z['ep'][1]:.2f}".replace(".", ","), (tr/2, z["ep"][1]), xytext=(0, 6), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].annotate(f"{z['ep'][-1]:.2f}".replace(".", ",").replace("-", "−"), (tr + tu + tt/2, z["ep"][-1]), xytext=(0, -14), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig_omega.png", facecolor="white"); plt.close(fig)

# ---------- 3. ползун: y(t), V(t), a(t)
fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.2), dpi=200, sharex=True)
data = ((z["y"], "y, мм", "Положение ползуна y(t)"), (z["V"], "V, мм/с", "Скорость ползуна V(t), вниз — минус"),
        (z["A"], "a, мм/с²", "Ускорение ползуна a(t)"))
for ax, (yv, lab, title) in zip(axs, data):
    style(ax); ax.axvspan(tr + tu, T, color=SHADE, lw=0); ax.axvline(tr + tu, color=INK2, lw=0.9, ls=(0, (4, 3)))
    ax.plot(t, yv, color=S1, lw=1.6); ax.set_ylabel(lab); ax.set_title(title, color=INK)
axs[1].axhline(0, color=INK2, lw=0.8); axs[2].axhline(0, color=INK2, lw=0.8)
i = int(np.argmin(z["V"])); axs[1].plot(t[i], z["V"][i], "o", ms=6, color=S1, mec="white", mew=1.4)
axs[1].annotate(f"{z['V'][i]:.1f} мм/с".replace(".", ",").replace("-", "−"), (t[i], z["V"][i]), xytext=(-10, 4), textcoords="offset points", ha="right", color=INK, fontsize=9)
axs[1].set_ylim(-34, 3)
axs[0].text(tr + tu + tt/2, z["y"].max()*0.9, "обжим", ha="center", color=INK2)
axs[2].set_xlabel("время t, с"); axs[2].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig_slider.png", facecolor="white"); plt.close(fig)
print("ok")
