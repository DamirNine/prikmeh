# -*- coding: utf-8 -*-
"""Рис. 3, 6, 8 (v15) — код figs_v8.py (2026-10-10): подпись «принято» на рис. 3 не перекрывает штриховые ограничения,
вставка рис. 6 не заходит на ось и на скачок силы, выноска рис. 8 подходит к точке снизу, не по кривой.
Данные — amin_v6.npz (calc_v6.py) и forces_v8.npz (calc_v8.py, 2026-10-10) в текущей папке;
запуск: python figs_v15.py <папка с npz>."""
import os, sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.5,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 10.5, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})
INK, INK2, GRID, S1, S2, S3, SHADE, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#e3742a", "#2f9e6b", "#f1f1ee", "#c4372b"
cm = lambda s: s.replace(".", ",").replace("-", "−")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))
OUT = os.path.dirname(os.path.abspath(__file__))
NPZ = sys.argv[1] if len(sys.argv) > 1 else "."

def style(ax):
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

fz = np.load(os.path.join(NPZ, "forces_v8.npz"))
PH_N, PH_OB, PH_Y, PH_K = (float(fz[k]) for k in ("phi_n", "phi_ob", "phi_y", "phi_k"))

# ===================================================== рис. 3: A_min(ψ) + угловой ход
z = np.load(os.path.join(NPZ, "amin_v6.npz"))
ps, A = z["ps"], z["A"]; ps_s, A_s = float(z["psi_star"]), float(z["A_star"])
psi_c, A_c, e_c = float(z["psi_c"]), float(z["A_c"]), float(z["e_c"])
fig, ax = plt.subplots(figsize=(7.8, 4.9), dpi=220)
style(ax)
ax.plot(ps, A, color=S1, lw=2.2, label=r"площадь $A_{\min}(\psi)$, мм²", zorder=5)
xl = np.linspace(ps_s, 58.0, 50)
ax.plot(xl, A_s * xl / ps_s, color=S2, lw=2.2, label=r"угловой ход $\psi$ в шкале уступок: $A^{*}\psi/\psi^{*}$", zorder=5)
for x in (ps_s, 37.06, 52.48):
    ax.axvline(x, color="#9ab7d9", lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.text(29.6, 232, "огранич. L ≤ 500 мм", fontsize=8, color=INK2, va="top")
ax.text(37.3, 232, r"огранич. $\varphi_{\mathrm{н}}\leq 60°$", fontsize=8, color=INK2, va="top")
ax.text(52.7, 232, "огранич. e ≥ 10 мм", fontsize=8, color=INK2, va="top")
ax.plot(psi_c, A_c, "o", ms=10, color=ACC, mec="white", mew=1.6, zorder=8)
ax.annotate("принято — точка равных уступок (25 %):\nψ = 36,75°, e = 12,53 мм, A = 100,2 мм²,\nокно 59,47° → 22,72°",
            (psi_c, A_c), xytext=(37.7, 160), textcoords="data", fontsize=8.8, color=ACC,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5), arrowprops=dict(arrowstyle="-|>", color=ACC, lw=0.9, shrinkB=7))
ax.set_xlim(28, 59); ax.set_ylim(60, 236)
ax.xaxis.set_major_locator(MultipleLocator(5))
ax.set_xlabel("угловой ход кулисы ψ, град"); ax.set_ylabel(r"минимальная площадь $A_{\min}$, мм²")
ax.set_title("Площадь треугольника и угловой ход: выбор компромисса", color=INK)
axe = ax.twinx(); axe.set_ylim(60 / 8, 236 / 8); axe.set_ylabel("e = A/8, мм", color=INK2)
axe.yaxis.set_major_formatter(COMMA); axe.spines["top"].set_visible(False)
axd = ax.twinx(); axd.spines["right"].set_position(("outward", 46)); axd.spines["top"].set_visible(False)
axd.set_ylim(100 * (60 / A_s - 1), 100 * (236 / A_s - 1)); axd.set_ylabel("относительная уступка δ, %", color=INK2)
axd.yaxis.set_major_locator(MultipleLocator(25)); axd.yaxis.set_major_formatter(COMMA)
ax.legend(loc="upper right", bbox_to_anchor=(0.995, 0.86), frameon=True, framealpha=0.95, edgecolor="#d0d0cc", fontsize=8.6)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_amin_psi_v15.png"), facecolor="white"); plt.close(fig)

# ===================================================== рис. 6: закон силы обжима
phs, X, Fv, Lreq = fz["phi"], fz["X"], fz["F"], fz["Lreq"]
F_t, F_max, sig_t = float(fz["F_t"]), float(fz["F_max"]), float(fz["sig_t"])
eps_t_, eps_m = float(fz["eps_y"]), float(fz["eps_max"])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.8, 3.5), dpi=220, gridspec_kw=dict(width_ratios=[1, 1.25]))
style(a1); style(a2)
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
a2.axvspan(PH_Y, PH_K, color=SHADE, lw=0)
a2.plot(phs, Fv, color=S1, lw=2)
a2.set_xlim(PH_N + 1, PH_K - 1); a2.set_ylim(-80, 2350)
a2.set_xlabel("угол кулисы φ, град  (рабочий ход →)"); a2.set_ylabel(r"сила обжима $F_{\mathrm{ук}}$, Н")
a2.set_title(r"б) закон силы обжима $F_{\mathrm{ук}}(\varphi)$", color=INK)
a2.text((PH_N + PH_OB) / 2, 160, "холостой ход\nF = 0", ha="center", fontsize=8.5, color=INK2)
a2.text((PH_Y + PH_K) / 2, 1050, "пластическая\nдеформация\nс упрочнением,\nk ≈ 16 Н/мм", ha="center", va="center", fontsize=8.5, color=INK2)
a2.annotate(cm(f"F_т = {F_t:.0f} Н").replace("F_т", "$F_{\\mathrm{т}}$"), (PH_Y, F_t), xytext=(53.5, 2120), textcoords="data", fontsize=8.6,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
a2.annotate(cm(f"F_ук = {F_max:.0f} Н").replace("F_ук", "$F_{\\mathrm{ук}}$"), (PH_K, F_max), xytext=(33.0, 2200), textcoords="data",
            fontsize=8.6, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
ins = a2.inset_axes([0.14, 0.33, 0.25, 0.28])
mm = (phs <= PH_OB + 0.08) & (phs >= PH_Y - 0.12)
ins.plot(phs[mm], Fv[mm], color=S1, lw=1.6); ins.axvspan(PH_OB, PH_Y, color="#dbe8f7", lw=0)
ins.set_xlim(PH_OB + 0.08, PH_Y - 0.12); ins.tick_params(labelsize=7)
ins.set_title(cm(f"упругий участок\n{PH_OB:.2f}° → {PH_Y:.2f}°"), fontsize=7.4, color=INK, loc="left", fontweight="normal", linespacing=1.1)
ins.xaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:.1f}"))); ins.yaxis.set_major_formatter(COMMA)
ins.xaxis.set_major_locator(MultipleLocator(0.2))
for s in ("top", "right"):
    ins.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig6_crimp_law_v15.png"), facecolor="white"); plt.close(fig)

# ===================================================== рис. 8: требуемая длина рукояти
L_max, ph_Lmax, L_des, P_dop = float(fz["L_max"]), float(fz["ph_Lmax"]), float(fz["L_des"]), float(fz["P_dop"])
fig, ax = plt.subplots(figsize=(7.8, 3.6), dpi=220)
style(ax)
ax.axvspan(PH_Y, PH_K, color=SHADE, lw=0)
ax.plot(phs, Lreq, color=S1, lw=2, zorder=4, label=r"$L_{\mathrm{треб}}(\varphi) = F_{\mathrm{ук}}(\varphi)\,e\,/\,(P_{\mathrm{доп}}\cos^{3}\varphi)$")
ax.axhline(L_des, color=ACC, lw=1.3, ls=(0, (5, 3)), zorder=3)
ax.text(PH_N + 0.5, L_des + 6, "принято L = 500 мм (ГОСТ 6636-69, Ra10)", color=ACC, fontsize=8.8, va="bottom")
ax.plot(ph_Lmax, L_max, "o", ms=7, color=ACC, mec="white", mew=1.3, zorder=6)
ax.annotate(cm(f"max: L = {L_max:.1f} мм\nпри φ = {ph_Lmax:.2f}°\n(начало пластической деформации)"), (ph_Lmax, L_max),
            xytext=(40.6, 255), textcoords="data", fontsize=8.6, color=INK, va="top",
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, shrinkB=5, relpos=(0.08, 1.0)))
ax.text((PH_N + PH_OB) / 2, 40, "холостой ход: F = 0,\nрукоять не нагружена", ha="center", fontsize=8.5, color=INK2)
ax.set_xlim(PH_N + 1, PH_K - 1); ax.set_ylim(0, 540)
ax.set_xlabel("угол кулисы φ, град  (рабочий ход →)"); ax.set_ylabel("требуемая длина рукояти L, мм")
ax.set_title(r"Требуемая длина рукояти при допустимой силе руки $P_{\mathrm{доп}}$ = 120 Н", color=INK)
ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.02), fontsize=8.6, frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig8_Lreq_v15.png"), facecolor="white"); plt.close(fig)
print("ok")
