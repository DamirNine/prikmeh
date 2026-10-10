# -*- coding: utf-8 -*-
"""Рисунки v6: рис. 3 (A_min и угловой ход), рис. 5 (проекции на оси ДСК), рис. 6–8 (силовой расчёт)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, Arc, Polygon
from math import radians, degrees, tan, atan, cos, sin

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.5,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 10.5, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})
INK, INK2, GRID, S1, S2, S3, SHADE = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#e3742a", "#2f9e6b", "#f1f1ee"
ACC = "#c4372b"
cm = lambda s: s.replace(".", ",").replace("-", "−")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))

def style(ax, grid=True):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    if grid:
        ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# =====================================================================
# Рис. 3 — A_min(ψ) + угловой ход в шкале относительных уступок
z = np.load("amin_v6.npz")
ps, A = z["ps"], z["A"]; ps_s, A_s = float(z["psi_star"]), float(z["A_star"])
psi_c, A_c, e_c = float(z["psi_c"]), float(z["A_c"]), float(z["e_c"])
fig, ax = plt.subplots(figsize=(7.8, 4.9), dpi=220)
style(ax)
ax.plot(ps, A, color=S1, lw=2.2, label=r"площадь $A_{\min}(\psi)$, мм²", zorder=5)
xl = np.linspace(ps_s, 58.0, 50)
ax.plot(xl, A_s * xl / ps_s, color=S2, lw=2.2, label=r"угловой ход $\psi$ в шкале уступок: $A^{*}\psi/\psi^{*}$", zorder=5)
# границы активных ограничений
for x, lab in ((ps_s, r"$L\leq 500$ мм" + "\n(левая граница)"), (37.06, r"$\varphi_{\mathrm{н}}\leq 60°$"), (52.48, r"$e\geq 10$ мм")):
    ax.axvline(x, color="#9ab7d9", lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.text(29.6, 232, "огранич. L ≤ 500 мм", fontsize=8, color=INK2, va="top")
ax.text(37.3, 232, r"огранич. $\varphi_{\mathrm{н}}\leq 60°$", fontsize=8, color=INK2, va="top")
ax.text(52.7, 232, "огранич. e ≥ 10 мм", fontsize=8, color=INK2, va="top")
# e = 12 мм (Ra10)
psi12 = 38.26
ax.plot([psi12, 58.5], [96, 96], color=INK2, lw=1.0, ls=(0, (2, 2)), zorder=3)
ax.text(58.4, 97.5, "e = 12 мм (Ra10), A = 96 мм²", fontsize=8.3, color=INK2, ha="right", va="bottom")
# точка равных уступок
ax.plot(psi_c, A_c, "o", ms=8, color="white", mec=INK, mew=1.8, zorder=8)
ax.annotate(cm(f"равные уступки {100*(A_c/A_s-1):.0f} %:\nψ = {psi_c:.1f}°, A = {A_c:.1f} мм², e = {e_c:.2f} мм"),
            (psi_c, A_c), xytext=(38.6, 166), textcoords="data", fontsize=8.8, color=INK,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, shrinkB=6))
# принятый вариант
ax.plot(40, 96, "o", ms=9, color=ACC, mec="white", mew=1.4, zorder=9)
ax.annotate("принято: ψ = 40°, e = 12 мм\n(окно 59,29° → 19,29°, L = 500 мм)", (40, 96), xytext=(41.2, 64.5),
            textcoords="data", fontsize=8.8, color=ACC, bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5),
            arrowprops=dict(arrowstyle="-|>", color=ACC, lw=0.9, shrinkB=6))
ax.plot(40, 93.56, "o", ms=4.5, color=S1, zorder=7)
ax.set_xlim(28, 59); ax.set_ylim(60, 236)
ax.xaxis.set_major_locator(MultipleLocator(5))
ax.set_xlabel("угловой ход кулисы ψ, град"); ax.set_ylabel(r"минимальная площадь $A_{\min}$, мм²")
ax.set_title("Площадь треугольника и угловой ход: выбор компромисса", color=INK)
# правые шкалы: e и относительная уступка
axe = ax.twinx(); axe.set_ylim(60 / 8, 236 / 8); axe.set_ylabel("e = A/8, мм", color=INK2)
axe.yaxis.set_major_formatter(COMMA); axe.spines["top"].set_visible(False)
axd = ax.twinx(); axd.spines["right"].set_position(("outward", 46)); axd.spines["top"].set_visible(False)
axd.set_ylim(100 * (60 / A_s - 1), 100 * (236 / A_s - 1)); axd.set_ylabel("относительная уступка δ, %", color=INK2)
axd.yaxis.set_major_locator(MultipleLocator(25)); axd.yaxis.set_major_formatter(COMMA)
ax.legend(loc="upper right", bbox_to_anchor=(0.995, 0.86), frameon=True, framealpha=0.95, edgecolor="#d0d0cc", fontsize=8.6)
fig.tight_layout(); fig.savefig("fig3_amin_psi_v6.png", facecolor="white"); plt.close(fig)

# =====================================================================
# Кинематика (как kin_v5.py) — для рис. 5
e, L = 12.0, 500.0
phi_k, S, S_OB = 19.29, 16.0, 6.0
sig_t, E = 415.0, 2.1e5
Dk, Dobzh = 32.10, 28.6
v_max = 700.0
eps_y = sig_t / E; dr_y = eps_y * Dk / 2; tg_a = ((Dk - Dobzh) / 2) / S_OB; d_y = dr_y / tg_a
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

fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.6), dpi=200, sharex=True)
data = ((yD, r"$y_D$, мм", r"Координата ползуна $y_D(t)$  ($x_D = e$ = const)"),
        (VDy, r"$V_{Dy}$, мм/с", r"Проекция скорости ползуна на ось y ДСК: $V_{Dy}(t)$;  $V_{Dx}$ = 0"),
        (aDy, r"$a_{Dy}$, мм/с²", r"Проекция ускорения ползуна на ось y ДСК: $a_{Dy}(t)$;  $a_{Dx}$ = 0"))
for ax, (yv, lab, title) in zip(axs, data):
    style(ax); zones(ax); ax.plot(t, yv, color=S1, lw=1.6); ax.set_ylabel(lab); ax.set_title(title, color=INK)
axs[1].axhline(0, color=INK2, lw=0.8); axs[2].axhline(0, color=INK2, lw=0.8); axs[1].set_ylim(-34, 4)
i = int(np.argmin(VDy)); axs[1].plot(t[i], VDy[i], "o", ms=6, color=S1, mec="white", mew=1.4)
axs[1].annotate(cm(f"{VDy[i]:.1f} мм/с"), (t[i], VDy[i]), xytext=(-10, 4), textcoords="offset points", ha="right", color=INK, fontsize=9)
axs[1].text(T*0.985, -31.5, r"$V_{Dy}<0$: на рабочем ходе ползун движется против оси y", color=INK2, fontsize=8.6, ha="right", va="center")
axs[0].text(tp + t_t / 2, yD.max() * 0.9, "пластическая деформация", ha="center", color=INK2)
axs[0].text(t_r - 0.008, yD.max() * 0.9, "касание с крышкой", ha="right", color=INK2, fontsize=8.5)
axs[2].set_xlabel("время t, с"); axs[2].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig5_slider_proj_v6.png", facecolor="white"); plt.close(fig)

# =====================================================================
# Силовой расчёт
fz = np.load("forces_v6.npz")
phs = fz["phi"]
F_t, F_max, C, k_h = float(fz["F_t"]), float(fz["F_max"]), float(fz["C"]), float(fz["k_h"])
ph_n, ph_ob, ph_y, ph_k = float(fz["phi_n"]), float(fz["phi_ob"]), float(fz["phi_y"]), float(fz["phi_k"])

# ---------- Рис. 6 — закон силы обжима
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.8, 3.5), dpi=220, gridspec_kw=dict(width_ratios=[1, 1.25]))
style(a1); style(a2)
eps_t_, eps_m = float(fz["eps_y"]), float(fz["eps_max"])
a1.plot([0, eps_t_, eps_m], [0, sig_t, 1.05 * sig_t], color=S1, lw=2)
a1.plot([eps_t_], [sig_t], "o", ms=5, color=S1); a1.plot([eps_m], [1.05 * sig_t], "o", ms=5, color=ACC)
a1.set_xlim(-0.004, 0.128); a1.set_ylim(0, 505)
a1.set_xlabel("деформация юбки ε"); a1.set_ylabel("напряжение σ, МПа")
a1.set_title("а) диаграмма σ(ε) жести крышки", color=INK)
a1.annotate(r"$\sigma_{\mathrm{т}}$ = 415 МПа", (eps_t_, sig_t), xytext=(14, -40), textcoords="offset points", fontsize=8.6,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
a1.annotate(r"$\sigma_{\max}$ = 1,05·$\sigma_{\mathrm{т}}$ = 435,75 МПа", (eps_m, 1.05 * sig_t), xytext=(0.012, 472), textcoords="data",
            fontsize=8.4, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
a1.text(0.006, 200, "упругий участок\nE = 2,1·10⁵ МПа", fontsize=8.3, color=INK2)
a1.text(0.045, 382, "упрочнение, $E_{\\mathrm{т}}$ ≈ 183 МПа", fontsize=8.3, color=INK2)
a1.text(eps_m, 15, cm(f"ε = ln(Dk/Dобж)\n= {eps_m:.4f}"), fontsize=8, color=INK2, ha="right")
Fv = fz["F"]
a2.axvspan(ph_y, ph_k, color=SHADE, lw=0)
a2.plot(phs, Fv, color=S1, lw=2)
a2.set_xlim(ph_n + 1, ph_k - 1); a2.set_ylim(-80, 2350)
a2.set_xlabel("угол кулисы φ, град  (рабочий ход →)"); a2.set_ylabel(r"сила обжима $F_{\mathrm{ук}}$, Н")
a2.set_title(r"б) закон силы обжима $F_{\mathrm{ук}}(\varphi)$", color=INK)
a2.text((ph_n + ph_ob) / 2, 160, "холостой ход\nF = 0", ha="center", fontsize=8.5, color=INK2)
a2.text((ph_y + ph_k) / 2, 1050, "пластическая\nдеформация\nс упрочнением,\nk ≈ 16 Н/мм", ha="center", va="center", fontsize=8.5, color=INK2)
a2.annotate(cm(f"F_т = {F_t:.0f} Н").replace("F_т", "$F_{\\mathrm{т}}$"), (ph_y, F_t), xytext=(53.5, 2120), textcoords="data", fontsize=8.6,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
a2.annotate(cm(f"F_ук = {F_max:.0f} Н").replace("F_ук", "$F_{\\mathrm{ук}}$"), (ph_k, F_max), xytext=(30.5, 2200), textcoords="data",
            fontsize=8.6, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
ins = a2.inset_axes([0.07, 0.33, 0.29, 0.30])
mm = (phs <= ph_ob + 0.08) & (phs >= ph_y - 0.12)
ins.plot(phs[mm], Fv[mm], color=S1, lw=1.6); ins.axvspan(ph_ob, ph_y, color="#dbe8f7", lw=0)
ins.set_xlim(ph_ob + 0.08, ph_y - 0.12); ins.tick_params(labelsize=7)
ins.set_title(cm(f"упругий участок {ph_ob:.2f}°→{ph_y:.2f}°"), fontsize=7.4, color=INK, loc="left", fontweight="normal")
ins.xaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:.2f}"))); ins.yaxis.set_major_formatter(COMMA)
ins.xaxis.set_major_locator(MultipleLocator(0.2))
for s in ("top", "right"):
    ins.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig("fig6_crimp_law_v6.png", facecolor="white"); plt.close(fig)

# ---------- Рис. 8 — силы и реакции в зависимости от φ
fig, axs = plt.subplots(2, 3, figsize=(8.2, 5.4), dpi=220, sharex=True)
axs = axs.ravel()
for ax in axs:
    style(ax); ax.axvspan(ph_y, ph_k, color=SHADE, lw=0); ax.axhline(0, color=INK2, lw=0.7)
    ax.set_xlim(ph_n + 1, ph_k - 1)
def mark(ax, val, txt, dx=8, dy=6, ha="left"):
    j = int(np.argmin(np.abs(phs - ph_y)))
    ax.plot(phs[j], val[j], "o", ms=4.5, color=ACC, zorder=6)
    ax.annotate(txt, (phs[j], val[j]), xytext=(dx, dy), textcoords="offset points", fontsize=7.8, color=ACC, ha=ha)
axs[0].plot(phs, fz["F"], color=INK, lw=1.6); axs[0].set_title(r"Сила обжима $F_{\mathrm{ук}}$", fontsize=9.5)
axs[1].plot(phs, fz["P"], color="#8e44ad", lw=1.6); axs[1].axhline(120, color=ACC, lw=0.9, ls=(0, (4, 3)))
axs[1].text(ph_n, 123, "P = 120 Н (принято)", fontsize=7.6, color=ACC, va="bottom")
axs[1].set_title("Сила руки P", fontsize=9.5); mark(axs[1], fz["P"], cm(f"{fz['P'].max():.1f} Н"), dx=8, dy=2)
axs[2].plot(phs, fz["R10x"], color=ACC, lw=1.5, label=r"$R_{10}^{x}$")
axs[2].plot(phs, fz["R10y"], color=S1, lw=1.5, label=r"$R_{10}^{y}$")
axs[2].plot(phs, fz["R10"], color=INK2, lw=1.1, ls=(0, (3, 2)), label=r"$|R_{10}|$")
axs[2].set_title("Реакции в опоре O", fontsize=9.5); axs[2].legend(fontsize=7.5, frameon=False, loc="lower left")
axs[3].plot(phs, fz["N"], color=S1, lw=1.6); axs[3].set_title(r"Кулиса–камень $R_{12}^{N}$", fontsize=9.5)
mark(axs[3], fz["N"], cm(f"{fz['N'].max():.0f} Н"), dx=-8, dy=4, ha="right")
axs[4].plot(phs, fz["R23x"], color=ACC, lw=1.5, label=r"$R_{23}^{x}$")
axs[4].plot(phs, fz["R23y"], color=S1, lw=1.5, label=r"$R_{23}^{y}$")
axs[4].set_title("Шарнир D (камень–ползун)", fontsize=9.5); axs[4].legend(fontsize=7.5, frameon=False, loc="lower left")
axs[5].plot(phs, fz["R30"], color=S3, lw=1.6, label=r"$R_{30}^{N}$")
axs[5].plot(phs, 0 * phs, color=INK, lw=1.0, ls=(0, (1, 2)), label=r"$M_{21}=M_{30}=0$")
axs[5].set_title("Направляющая ползуна", fontsize=9.5); axs[5].legend(fontsize=7.5, frameon=False, loc="upper right", bbox_to_anchor=(1.0, 0.9))
for ax in axs[3:]:
    ax.set_xlabel("угол кулисы φ, град")
for ax in (axs[0], axs[3]):
    ax.set_ylabel("Н")
for ax in (axs[1], axs[2], axs[4], axs[5]):
    ax.set_ylabel("Н")
fig.text(0.5, 0.005, "рабочий ход — слева направо; серым — пластическая деформация крышки", ha="center", fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.025, 1, 1)); fig.savefig("fig8_forces_v6.png", facecolor="white"); plt.close(fig)
print("ok", fz["P"].max(), fz["N"].max())
