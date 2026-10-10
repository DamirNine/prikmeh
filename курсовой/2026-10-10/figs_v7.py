# -*- coding: utf-8 -*-
"""Рисунки v7 (L = 450 мм): рис. 4 ω(t), ε(t); рис. 5 проекции ползуна; рис. 8 L_треб(φ); рис. 9 — 9 неизвестных системы от φ."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from math import radians, degrees, tan, atan

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.5,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 10.5, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})
INK, INK2, GRID, S1, S2, S3, SHADE, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#e3742a", "#2f9e6b", "#f1f1ee", "#c4372b"
cm = lambda s: s.replace(".", ",").replace("-", "−")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))

def style(ax):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# ===================================================== кинематика, L = 450 мм
e, L = 12.0, 450.0
phi_k, S, S_OB = 19.29, 16.0, 6.0
sig_t, E, Dk, Dobzh = 415.0, 2.1e5, 32.10, 28.6
v_max = 700.0
eps_y = sig_t / E; d_y = (eps_y * Dk / 2) / (((Dk - Dobzh) / 2) / S_OB)
tk = tan(radians(phi_k))
phi_n = degrees(atan(tk + S / e)); phi_ob = degrees(atan(tk + S_OB / e)); phi_y = degrees(atan(tk + (S_OB - d_y) / e))
psi_xx = radians(phi_n - phi_ob); psi_u = radians(phi_ob - phi_y); psi_pl = radians(phi_y - phi_k)
w = v_max / L
t_r, t_u, t_t = 2 * psi_xx / w, psi_u / w, 2 * psi_pl / w
eps_r, eps_t = w / t_r, -w / t_t
T = t_r + t_u + t_t; tp = t_r + t_u
t = np.linspace(0, T, 8001)
om = np.where(t < t_r, eps_r * t, np.where(t < tp, w, w + eps_t * (t - tp)))
ep = np.where(t < t_r, eps_r, np.where(t < tp, 0.0, eps_t))
q = np.where(t < t_r, 0.5 * eps_r * t ** 2, np.where(t < tp, 0.5 * eps_r * t_r ** 2 + w * (t - t_r),
             0.5 * eps_r * t_r ** 2 + w * t_u + w * (t - tp) + 0.5 * eps_t * (t - tp) ** 2))
phi = radians(phi_n) - q
VqDy = -e / np.cos(phi) ** 2; aqDy = 2 * e * np.sin(phi) / np.cos(phi) ** 3
yD = e * np.tan(phi); VDy = om * VqDy; aDy = om ** 2 * aqDy + ep * VqDy

def zones(ax):
    ax.axvspan(tp, T, color=SHADE, lw=0); ax.axvline(t_r, color=INK2, lw=0.9, ls=(0, (4, 3)))

# ---------- рис. 4: ω(t), ε(t)
fig, axs = plt.subplots(2, 1, figsize=(7.6, 4.8), dpi=200, sharex=True)
for ax in axs:
    style(ax); zones(ax)
axs[0].plot(t, om, color=S1, lw=1.6); axs[0].set_ylabel("ω, рад/с"); axs[0].set_ylim(0, 1.95)
axs[0].set_title("Угловая скорость кулисы ω(t)", color=INK)
axs[0].text(t_r / 2, 0.15, "разгон\n(холостой ход)", ha="center", color=INK2)
axs[0].text(tp + t_t / 2, 0.15, "торможение\n(пластическая деформация)", ha="center", color=INK2)
axs[0].text(t_r + 0.01, 1.90, "касание с крышкой", color=INK2, fontsize=8.5, va="top", ha="left")
axs[0].annotate(cm(f"ω_max = {w:.2f} рад/с").replace("ω_max", r"$\omega_{\max}$"), (tp, w), xytext=(14, 10),
                textcoords="offset points", color=INK, fontsize=9)
ins = axs[0].inset_axes([0.05, 0.58, 0.27, 0.34])
m = (t > t_r - 0.012) & (t < tp + 0.012)
ins.plot(t[m] * 1000, om[m], color=S1, lw=1.6); ins.axvspan(t_r * 1000, tp * 1000, color="#dbe8f7", lw=0)
ins.set_title(cm(f"упругая деформация: {t_u*1000:.1f} мс"), fontsize=8.5, color=INK, loc="left", fontweight="normal")
ins.tick_params(labelsize=7); ins.set_xlabel("t, мс", fontsize=7.5)
ins.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:g}")); ins.yaxis.set_major_formatter(COMMA)
for s in ("top", "right"):
    ins.spines[s].set_visible(False)
axs[1].step(t, ep, where="post", color=S1, lw=1.6); axs[1].axhline(0, color=INK2, lw=0.8)
axs[1].set_ylabel("ε, рад/с²"); axs[1].set_ylim(-4.4, 4.4); axs[1].set_xlabel("время t, с")
axs[1].set_title("Угловое ускорение кулисы ε(t)", color=INK)
axs[1].annotate(cm(f"+{eps_r:.2f}"), (t_r / 2, eps_r), xytext=(0, 6), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].annotate(cm(f"{eps_t:.2f}"), (tp + t_t / 2, eps_t), xytext=(0, -14), textcoords="offset points", ha="center", color=INK, fontsize=9)
axs[1].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig4_omega_v7.png", facecolor="white"); plt.close(fig)

# ---------- рис. 5: проекции ползуна
fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.6), dpi=200, sharex=True)
data = ((yD, r"$y_D$, мм", r"Координата ползуна $y_D(t)$  ($x_D = e$ = const)"),
        (VDy, r"$V_{Dy}$, мм/с", r"Проекция скорости ползуна на ось y ДСК: $V_{Dy}(t)$;  $V_{Dx}$ = 0"),
        (aDy, r"$a_{Dy}$, мм/с²", r"Проекция ускорения ползуна на ось y ДСК: $a_{Dy}(t)$;  $a_{Dx}$ = 0"))
for ax, (yv, lab, title) in zip(axs, data):
    style(ax); zones(ax); ax.plot(t, yv, color=S1, lw=1.6); ax.set_ylabel(lab); ax.set_title(title, color=INK)
axs[1].axhline(0, color=INK2, lw=0.8); axs[2].axhline(0, color=INK2, lw=0.8); axs[1].set_ylim(-37, 4)
i = int(np.argmin(VDy)); axs[1].plot(t[i], VDy[i], "o", ms=6, color=S1, mec="white", mew=1.4)
axs[1].annotate(cm(f"{VDy[i]:.1f} мм/с"), (t[i], VDy[i]), xytext=(-10, 4), textcoords="offset points", ha="right", color=INK, fontsize=9)
axs[1].text(T * 0.985, -34.5, r"$V_{Dy}<0$ — ползун движется против оси y", color=INK2, fontsize=8.6, ha="right", va="center")
axs[0].text(tp + t_t / 2, yD.max() * 0.9, "пластическая деформация", ha="center", color=INK2)
axs[0].text(t_r - 0.008, yD.max() * 0.9, "касание с крышкой", ha="right", color=INK2, fontsize=8.5)
axs[2].set_xlabel("время t, с"); axs[2].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig5_slider_proj_v7.png", facecolor="white"); plt.close(fig)
print(f"kin: w={w:.4f} T={T:.4f} minV={VDy.min():.2f} a0={aDy[0]:.2f}")

# ===================================================== силовой расчёт
fz = np.load("forces_v7.npz")
phs, X, Fv, Lreq = fz["phi"], fz["X"], fz["F"], fz["Lreq"]
ph_n, ph_ob, ph_y, ph_k = (float(fz[k]) for k in ("phi_n", "phi_ob", "phi_y", "phi_k"))
L_max, ph_Lmax, L_des, P_dop = float(fz["L_max"]), float(fz["ph_Lmax"]), float(fz["L_des"]), float(fz["P_dop"])

# ---------- рис. 8: требуемая длина рукояти
fig, ax = plt.subplots(figsize=(7.8, 3.6), dpi=220)
style(ax)
ax.axvspan(ph_y, ph_k, color=SHADE, lw=0)
ax.plot(phs, Lreq, color=S1, lw=2, zorder=4, label=r"$L_{\mathrm{треб}}(\varphi) = F_{\mathrm{ук}}(\varphi)\,e\,/\,(P_{\mathrm{доп}}\cos^{3}\varphi)$")
ax.axhline(L_des, color=ACC, lw=1.3, ls=(0, (5, 3)), zorder=3)
ax.text(ph_n + 0.5, L_des + 6, "принято L = 450 мм (ГОСТ 6636-69, Ra20)", color=ACC, fontsize=8.8, va="bottom")
ax.plot(ph_Lmax, L_max, "o", ms=7, color=ACC, mec="white", mew=1.3, zorder=6)
ax.annotate(cm(f"max: L = {L_max:.1f} мм\nпри φ = {ph_Lmax:.2f}°\n(начало пластической деформации)"), (ph_Lmax, L_max),
            xytext=(33.0, 120), textcoords="data", fontsize=8.6, color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, shrinkB=5))
ax.text((ph_n + ph_ob) / 2, 40, "холостой ход: F = 0,\nрукоять не нагружена", ha="center", fontsize=8.5, color=INK2)
ax.set_xlim(ph_n + 1, ph_k - 1); ax.set_ylim(0, 480)
ax.set_xlabel("угол кулисы φ, град  (рабочий ход →)"); ax.set_ylabel("требуемая длина рукояти L, мм")
ax.set_title(r"Требуемая длина рукояти при допустимой силе руки $P_{\mathrm{доп}}$ = 120 Н", color=INK)
ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.02), fontsize=8.6, frameon=False)
fig.tight_layout(); fig.savefig("fig8_Lreq_v7.png", facecolor="white"); plt.close(fig)

# ---------- рис. 9: 9 неизвестных системы при L = 450
titles = [(r"$R_{10}^{x}$, Н", 0, ACC), (r"$R_{10}^{y}$, Н", 1, S1), (r"$R_{12}^{N}$, Н", 2, S1),
          (r"$M_{12}$, Н·мм", 3, INK), (r"$R_{23}^{x}$, Н", 4, ACC), (r"$R_{23}^{y}$, Н", 5, S1),
          (r"$R_{30}^{N}$, Н", 6, S3), (r"$M_{30}$, Н·мм", 7, INK), (r"сила руки $P$, Н", 8, "#8e44ad")]
fig, axs = plt.subplots(3, 3, figsize=(8.4, 7.0), dpi=220, sharex=True)
for ax, (tt, k, col) in zip(axs.ravel(), titles):
    style(ax); ax.axvspan(ph_y, ph_k, color=SHADE, lw=0); ax.axhline(0, color=INK2, lw=0.7)
    ax.plot(phs, X[:, k], color=col, lw=1.6)
    ax.set_title(tt, fontsize=9.6); ax.set_xlim(ph_n + 1, ph_k - 1)
    if k in (3, 7):
        ax.set_ylim(-1, 1); ax.text(0.5, 0.62, "≡ 0", transform=ax.transAxes, ha="center", fontsize=11, color=INK2)
    jy = int(np.argmin(np.abs(phs - ph_y)))
    if k not in (3, 7):
        ax.plot(phs[jy], X[jy, k], "o", ms=4, color=ACC, zorder=6)
axp = axs[2, 2]
axp.axhline(P_dop, color=ACC, lw=0.9, ls=(0, (4, 3))); axp.set_ylim(-5, 135)
axp.text(ph_n, P_dop + 2, "P_доп = 120 Н".replace("P_доп", r"$P_{\mathrm{доп}}$"), fontsize=7.8, color=ACC, va="bottom")
jy = int(np.argmin(np.abs(phs - ph_y)))
axp.annotate(cm(f"{X[jy, 8]:.1f} Н"), (phs[jy], X[jy, 8]), xytext=(7, 0), textcoords="offset points", fontsize=8, color=ACC, va="center")
for ax in axs[2]:
    ax.set_xlabel("угол кулисы φ, град")
fig.text(0.5, 0.004, "L = 450 мм; рабочий ход — слева направо; серым — пластическая деформация; точки — φ = 40,06°", ha="center",
         fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.02, 1, 1)); fig.savefig("fig9_unknowns_v7.png", facecolor="white"); plt.close(fig)
print("figs ok; L_max", L_max, "P_max", X[:, 8].max())
