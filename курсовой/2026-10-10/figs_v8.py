# -*- coding: utf-8 -*-
"""Рисунки v8 (ψ = 36,75°, e = 12,53 мм, L = 500 мм): рис. 2, 3, 4, 5, 6, 8, 9."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from math import radians, degrees, tan, atan, cos

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

S, Sob, F_UK, P_HAND, LMAX, EMIN = 16.0, 6.0, 1974.0, 120.0, 500.0, 10.0
PSI_ACC, E_ACC = 36.75, 12.53
fz = np.load("forces_v8.npz")
PH_N, PH_OB, PH_Y, PH_K = (float(fz[k]) for k in ("phi_n", "phi_ob", "phi_y", "phi_k"))

def best_for_psi(psi, n=40001):
    pk = np.linspace(0.0, 60.0 - psi, n); pn = pk + psi
    e = S / (np.tan(np.radians(pn)) - np.tan(np.radians(pk)))
    phob = np.degrees(np.arctan(np.tan(np.radians(pk)) + Sob / e))
    L = F_UK * e / (P_HAND * np.cos(np.radians(phob)) ** 3)
    ok = (e >= EMIN - 1e-9) & (L <= LMAX + 1e-9)
    A = 0.5 * e * S
    i = int(np.argmin(np.where(ok, A, np.inf)))
    return pk, A, pk[i], A[i]

# ===================================================== рис. 2: A(φк) при разных ψ
fig, ax = plt.subplots(figsize=(7.8, 4.6), dpi=220)
style(ax)
cols = {30: S1, 35: S2, 36.75: ACC, 40: S3, 45: "#8e44ad"}
for psi, col in cols.items():
    pk, A, pk_opt, A_opt = best_for_psi(psi)
    lw = 2.6 if psi == PSI_ACC else 1.7
    ax.plot(pk, A, color=col, lw=lw, label=cm(f"ψ = {psi:g}°"), zorder=4 if psi == PSI_ACC else 3)
    ax.plot(pk_opt, A_opt, "o", ms=8 if psi == PSI_ACC else 6, color=col, mec="white", mew=1.2, zorder=6)
ax.annotate(cm(f"принято: ψ = 36,75°, φк = {PH_K:.2f}°,\ne = 12,53 мм, A = 100,2 мм² (равные уступки)"),
            (PH_K, 100.24), xytext=(8.3, 210.0), textcoords="data", fontsize=8.8, color=ACC,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5), arrowprops=dict(arrowstyle="-|>", color=ACC, lw=0.9, shrinkB=6))
ax.set_xlabel("конечный угол кулисы φк, град"); ax.set_ylabel("площадь треугольника A, мм²")
ax.set_title("Площадь треугольника O–Bн–Bк в зависимости от положения окна", color=INK)
ax.legend(title="угловой ход", fontsize=8.6, title_fontsize=8.6, frameon=False, loc="upper right")
ax.set_xlim(-1, 31.5)
fig.tight_layout(); fig.savefig("fig2_area_phik_v8.png", facecolor="white"); plt.close(fig)

# ===================================================== рис. 3: A_min(ψ) + угловой ход
z = np.load("amin_v6.npz")
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
            (psi_c, A_c), xytext=(38.6, 160), textcoords="data", fontsize=8.8, color=ACC,
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
fig.tight_layout(); fig.savefig("fig3_amin_psi_v8.png", facecolor="white"); plt.close(fig)

# ===================================================== кинематика (L = 500)
kz = np.load("kin_v8.npz")
t, om, ep, yD, VDy, aDy = kz["t"], kz["om"], kz["ep"], kz["y"], kz["V"], kz["A"]
t_r, t_u, t_t = float(kz["t_r"]), float(kz["t_u"]), float(kz["t_t"]); T = t_r + t_u + t_t; tp = t_r + t_u
w = float(om.max()); eps_r, eps_t = float(ep[0]), float(ep[-1])
def zones(ax):
    ax.axvspan(tp, T, color=SHADE, lw=0); ax.axvline(t_r, color=INK2, lw=0.9, ls=(0, (4, 3)))

fig, axs = plt.subplots(2, 1, figsize=(7.6, 4.8), dpi=200, sharex=True)
for ax in axs:
    style(ax); zones(ax)
axs[0].plot(t, om, color=S1, lw=1.6); axs[0].set_ylabel("ω, рад/с"); axs[0].set_ylim(0, 1.78)
axs[0].set_title("Угловая скорость кулисы ω(t)", color=INK)
axs[0].text(t_r / 2, 0.15, "разгон\n(холостой ход)", ha="center", color=INK2)
axs[0].text(tp + t_t / 2, 0.15, "торможение\n(пластическая деформация)", ha="center", color=INK2)
axs[0].text(t_r + 0.01, 1.74, "касание с крышкой", color=INK2, fontsize=8.5, va="top", ha="left")
axs[0].annotate(cm(f"ω_max = {w:.2f} рад/с").replace("ω_max", r"$\omega_{\max}$"), (tp, w), xytext=(14, 10), textcoords="offset points", color=INK, fontsize=9)
ins = axs[0].inset_axes([0.05, 0.58, 0.27, 0.34])
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
fig.tight_layout(); fig.savefig("fig4_omega_v8.png", facecolor="white"); plt.close(fig)

fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.6), dpi=200, sharex=True)
data = ((yD, r"$y_D$, мм", r"Координата ползуна $y_D(t)$  ($x_D = e$ = const)"),
        (VDy, r"$V_{Dy}$, мм/с", r"Проекция скорости ползуна на ось y ДСК: $V_{Dy}(t)$;  $V_{Dx}$ = 0"),
        (aDy, r"$a_{Dy}$, мм/с²", r"Проекция ускорения ползуна на ось y ДСК: $a_{Dy}(t)$;  $a_{Dx}$ = 0"))
for ax, (yv, lab, title) in zip(axs, data):
    style(ax); zones(ax); ax.plot(t, yv, color=S1, lw=1.6); ax.set_ylabel(lab); ax.set_title(title, color=INK)
axs[1].axhline(0, color=INK2, lw=0.8); axs[2].axhline(0, color=INK2, lw=0.8); axs[1].set_ylim(-36, 4)
i = int(np.argmin(VDy)); axs[1].plot(t[i], VDy[i], "o", ms=6, color=S1, mec="white", mew=1.4)
axs[1].annotate(cm(f"{VDy[i]:.1f} мм/с"), (t[i], VDy[i]), xytext=(-10, 4), textcoords="offset points", ha="right", color=INK, fontsize=9)
axs[1].text(T * 0.985, -33.5, r"$V_{Dy}<0$ — ползун движется против оси y", color=INK2, fontsize=8.6, ha="right", va="center")
axs[0].text(tp + t_t / 2, yD.max() * 0.9, "пластическая деформация", ha="center", color=INK2)
axs[0].text(t_r - 0.008, yD.max() * 0.9, "касание с крышкой", ha="right", color=INK2, fontsize=8.5)
axs[2].set_xlabel("время t, с"); axs[2].set_xlim(0, T)
fig.tight_layout(); fig.savefig("fig5_slider_proj_v8.png", facecolor="white"); plt.close(fig)

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
ins = a2.inset_axes([0.07, 0.33, 0.29, 0.30])
mm = (phs <= PH_OB + 0.08) & (phs >= PH_Y - 0.12)
ins.plot(phs[mm], Fv[mm], color=S1, lw=1.6); ins.axvspan(PH_OB, PH_Y, color="#dbe8f7", lw=0)
ins.set_xlim(PH_OB + 0.08, PH_Y - 0.12); ins.tick_params(labelsize=7)
ins.set_title(cm(f"упругий участок {PH_OB:.2f}°→{PH_Y:.2f}°"), fontsize=7.4, color=INK, loc="left", fontweight="normal")
ins.xaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:.1f}"))); ins.yaxis.set_major_formatter(COMMA)
ins.xaxis.set_major_locator(MultipleLocator(0.2))
for s in ("top", "right"):
    ins.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig("fig6_crimp_law_v8.png", facecolor="white"); plt.close(fig)

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
            xytext=(34.0, 130), textcoords="data", fontsize=8.6, color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, shrinkB=5))
ax.text((PH_N + PH_OB) / 2, 40, "холостой ход: F = 0,\nрукоять не нагружена", ha="center", fontsize=8.5, color=INK2)
ax.set_xlim(PH_N + 1, PH_K - 1); ax.set_ylim(0, 540)
ax.set_xlabel("угол кулисы φ, град  (рабочий ход →)"); ax.set_ylabel("требуемая длина рукояти L, мм")
ax.set_title(r"Требуемая длина рукояти при допустимой силе руки $P_{\mathrm{доп}}$ = 120 Н", color=INK)
ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.02), fontsize=8.6, frameon=False)
fig.tight_layout(); fig.savefig("fig8_Lreq_v8.png", facecolor="white"); plt.close(fig)

# ===================================================== рис. 9: 9 неизвестных при L = 500
titles = [(r"$R_{10}^{x}$, Н", 0, ACC), (r"$R_{10}^{y}$, Н", 1, S1), (r"$R_{12}^{N}$, Н", 2, S1),
          (r"$M_{12}$, Н·мм", 3, INK), (r"$R_{23}^{x}$, Н", 4, ACC), (r"$R_{23}^{y}$, Н", 5, S1),
          (r"$R_{30}^{N}$, Н", 6, S3), (r"$M_{30}$, Н·мм", 7, INK), (r"сила руки $P$, Н", 8, "#8e44ad")]
fig, axs = plt.subplots(3, 3, figsize=(8.4, 7.0), dpi=220, sharex=True)
jy = int(np.argmin(np.abs(phs - PH_Y)))
for ax, (tt, k, col) in zip(axs.ravel(), titles):
    style(ax); ax.axvspan(PH_Y, PH_K, color=SHADE, lw=0); ax.axhline(0, color=INK2, lw=0.7)
    ax.plot(phs, X[:, k], color=col, lw=1.6)
    ax.set_title(tt, fontsize=9.6); ax.set_xlim(PH_N + 1, PH_K - 1)
    if k in (3, 7):
        ax.set_ylim(-1, 1); ax.text(0.5, 0.62, "≡ 0", transform=ax.transAxes, ha="center", fontsize=11, color=INK2)
    else:
        ax.plot(phs[jy], X[jy, k], "o", ms=4, color=ACC, zorder=6)
axp = axs[2, 2]
axp.axhline(P_dop, color=ACC, lw=0.9, ls=(0, (4, 3))); axp.set_ylim(-5, 135)
axp.text(PH_N, P_dop + 2, r"$P_{\mathrm{доп}}$ = 120 Н", fontsize=7.8, color=ACC, va="bottom")
axp.annotate(cm(f"{X[jy, 8]:.1f} Н"), (phs[jy], X[jy, 8]), xytext=(7, 0), textcoords="offset points", fontsize=8, color=ACC, va="center")
for ax in axs[2]:
    ax.set_xlabel("угол кулисы φ, град")
fig.text(0.5, 0.004, cm(f"L = 500 мм; рабочий ход — слева направо; серым — пластическая деформация; точки — φ = {PH_Y:.2f}°"), ha="center",
         fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.02, 1, 1)); fig.savefig("fig9_unknowns_v8.png", facecolor="white"); plt.close(fig)
print("ok", round(L_max, 2), round(X[:, 8].max(), 2), round(w, 3), round(VDy.min(), 2))
