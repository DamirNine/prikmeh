# -*- coding: utf-8 -*-
"""Рисунки раздела 12 (v13): 10, 11 — схема и эпюры N, Q, M на истинном (наклонном) положении кулисы при φу и φк;
12 — шток ползуна: схема, эпюра N, критическое напряжение σкр(λ); 13 — камень-обойма на кулисе: вид и сечение А–А."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.ticker import FuncFormatter

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "strength_v13.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.titlesize": 9.8, "axes.titleweight": "bold", "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, GRID, S1, S3, ACC, VIO = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#2f9e6b", "#c4372b", "#7b3fa0"
LIGHT = {S1: "#dbe8f7", S3: "#dcefe5", ACC: "#f6dcd9"}
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
L = 500.0


def arrow(ax, p0, p1, color=INK, lw=1.4, ms=10):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                      shrinkA=0, shrinkB=0), zorder=6)


# ====================================================================== рис. 10, 11 — эпюры на наклонной кулисе
def epury(pos, fname):
    phi = np.radians(pos["phi"]); u = np.array([np.cos(phi), np.sin(phi)]); n = np.array([-np.sin(phi), np.cos(phi)])
    lOD = pos["lOD"]; O = np.zeros(2); D = lOD * u; K = L * u
    N, QOD, QDK, MD = pos["N"], pos["Q_OD"], pos["Q_DK"], pos["M_D"]
    fig, axs = plt.subplots(2, 2, figsize=(7.9, 7.0), dpi=220)
    titles = ["а) расчётная схема (силы в истинных направлениях)", "б) эпюра N — продольная сила, Н",
              "в) эпюра Q — поперечная сила, Н", "г) эпюра M — изгибающий момент, Н·м"]
    for ax, t in zip(axs.flat, titles):
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(t, fontsize=9.2)
        ax.plot([-40, L * np.cos(phi) + 30], [0, 0], color=INK2, lw=0.6, ls=(0, (6, 3)))           # горизонталь (ось x)
        ax.plot([O[0], K[0]], [O[1], K[1]], color=INK, lw=2.6, zorder=4, solid_capstyle="round")
        ax.plot(*O, "o", ms=6.5, mfc="white", mec=INK, mew=1.3, zorder=7); ax.plot(*D, "s", ms=6, mfc="#f1f1ee", mec=INK, zorder=7)
        ax.plot(*K, "o", ms=4, color=INK, zorder=7)
        ax.text(*(O + np.array([-10, -26])), "O", fontsize=9); ax.text(*(K + np.array([8, -6])), "K", fontsize=9)
        ax.set_xlim(-120, L * np.cos(phi) + 70); ax.set_ylim(-150, L * np.sin(phi) + 90)
    # а) схема
    ax = axs[0, 0]
    ax.text(*(D + np.array([-4, 14])), "D", fontsize=9, ha="right")
    arrow(ax, tuple(D), tuple(D + 85 * n), VIO); ax.text(*(D + 92 * n + np.array([-4, 10])), r"$R_{12}^{N}$ = " + fmt(pos["R12N"], 0) + " Н",
                                                        fontsize=7.8, color=VIO, ha="center")
    arrow(ax, (O[0], O[1]), (O[0] + 70, O[1]), VIO); ax.text(O[0] + 74, O[1] - 30, r"$R_{10}^{x}$ = " + fmt(pos["R10x"], 0) + " Н", fontsize=7.6, color=VIO)
    arrow(ax, (O[0], O[1]), (O[0], O[1] - 70), VIO); ax.text(O[0] - 6, O[1] - 92, r"$R_{10}^{y}$ = " + fmt(pos["R10y"], 0) + " Н", fontsize=7.6, color=VIO, ha="left")
    arrow(ax, (K[0], K[1] + 80), (K[0], K[1] + 3), INK, lw=1.8); ax.text(K[0] - 8, K[1] + 62, "P = " + fmt(pos["P"], 1) + " Н", fontsize=8, ha="right")
    ax.text(*(0.5 * K - 30 * n), "L = 500 мм", fontsize=8, color=INK2, rotation=np.degrees(phi), ha="center", va="center")
    th = np.linspace(0, phi, 30); ax.plot(60 * np.cos(th), 60 * np.sin(th), color=INK2, lw=0.8)
    ax.text(68 * np.cos(phi / 2), 68 * np.sin(phi / 2), f"φ = {fmt(pos['phi'], 2)}°", fontsize=7.8, color=INK2, va="center")

    def epure(ax, zs, vals, scale, color, labels):
        pts_base = [z * u for z in zs]; pts_top = [z * u + v * scale * n for z, v in zip(zs, vals)]
        ax.add_patch(Polygon(np.vstack([pts_base, pts_top[::-1]]), closed=True, fc=LIGHT[color], ec="none", zorder=2))
        ax.plot(*np.array(pts_top).T, color=color, lw=1.5, zorder=3)
        zz = np.linspace(zs[0], zs[-1], 34)
        vv = np.interp(zz, zs, vals) if len(set(zs)) == len(zs) else None
        for z in zz:
            if vv is not None:
                v = np.interp(z, zs, vals)
            else:
                v = vals[next(k for k in range(len(zs) - 1) if zs[k] <= z <= zs[k + 1] and zs[k] != zs[k + 1])]
            p0 = z * u; p1 = p0 + v * scale * n
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=0.5, zorder=2)
        for z, v, txt, off in labels:
            p = z * u + v * scale * n + off
            ax.text(*p, txt, fontsize=7.8, ha="center", va="center", zorder=8, bbox=dict(fc="white", ec="none", pad=0.6))
    epure(axs[0, 1], [0, L], [N, N], 0.55, S3, [(250, N, fmt(N, 1) + " (сжатие)", -16 * n)])
    epure(axs[1, 0], [0, lOD, lOD + 1e-6, L], [QOD, QOD, QDK, QDK], 0.03, S1,
          [(lOD / 2, QOD, fmt(QOD, 1) + " (O–D)", np.array([70, -6])), (300, QDK, "+" + fmt(QDK, 1), 16 * n)])
    epure(axs[1, 1], [0, lOD, L], [0, MD / 1000, 0], 2.2, ACC,
          [(lOD, MD / 1000, fmt(MD / 1000, 2) + " (под камнем)", np.array([92, -2]))])
    for ax in axs.flat[1:]:
        ax.text(*(D + np.array([10, 18])), "D", fontsize=8.5)
    fig.suptitle(f"Кулиса с рукоятью в положении φ = {fmt(pos['phi'], 2)}°: ординаты эпюр отложены по нормали к оси звена",
                 fontsize=9.6, fontweight="bold", x=0.02, ha="left")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.91, bottom=0.01, wspace=0.05, hspace=0.12)
    fig.savefig(os.path.join(OUT, fname), facecolor="white"); plt.close(fig)


epury(R["A"], "fig10_epury_phiy_v13.png")
epury(R["B"], "fig11_epury_phik_v13.png")

# ====================================================================== рис. 12 — шток
rd, rp, it = R["rod"], R["rod_par"], R["rod_iter"]
fig = plt.figure(figsize=(7.9, 4.4), dpi=220)
gs = fig.add_gridspec(1, 3, width_ratios=[0.8, 0.6, 1.8], wspace=0.35)
ax = fig.add_subplot(gs[0]); ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-30, 30); ax.set_ylim(-95, 25)
ax.add_patch(Rectangle((-22, 0), 44, 12, fc="#dcdcd8", ec=INK, hatch="////", lw=0.9))
ax.text(0, 15, "направляющая (заделка)", ha="center", fontsize=7.4, color=INK2)
d = rd["d"]; ax.add_patch(Rectangle((-d / 2, -60), d, 60, fc="white", ec=INK, lw=1.2))
ax.add_patch(Rectangle((-14, -68), 28, 8, fc="#e9eef5", ec=INK, lw=0.9)); ax.text(16, -66, "головка", fontsize=7.2, color=INK2)
arrow(ax, (0, -92), (0, -68.5), S3, lw=1.6); ax.text(3, -86, r"$F_{ук}$ = " + fmt(rp["F"], 0) + " Н", fontsize=7.6, color=S3)
ax.annotate("", xy=(-24, 0), xytext=(-24, -60), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(-26, -30, "l = 60", rotation=90, ha="right", va="center", fontsize=7.4, color=INK2)
ax.set_title(f"а) шток Ø{d:g}, μ = 2", fontsize=9)
ax = fig.add_subplot(gs[1])
ax.fill_betweenx([-60, 0], 0, -rp["F"], facecolor=LIGHT[S3], edgecolor=S3, hatch="--", lw=0)
ax.plot([-rp["F"], -rp["F"]], [-60, 0], color=S3, lw=1.6); ax.axvline(0, color=INK, lw=1)
ax.set_xlim(-2600, 300); ax.set_ylim(-70, 8); ax.set_yticks([0, -20, -40, -60]); ax.set_xticks([-2000, 0])
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:g}"))); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: cm(f"{v:g}")))
ax.text(-rp["F"] / 2, -30, fmt(-rp["F"], 0), ha="center", fontsize=7.8, bbox=dict(fc="white", ec="none", pad=0.5))
ax.set_xlabel("N, Н"); ax.set_ylabel("мм от направляющей"); ax.set_title("б) эпюра N", fontsize=9)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
ax = fig.add_subplot(gs[2])
lam = np.linspace(20, 160, 500)
E = 2.1e5
sk = np.where(lam >= rp["lam_pr"], np.pi ** 2 * E / lam ** 2, np.minimum(rp["a"] - rp["b"] * lam, rp["sT"]))
ax.plot(lam, sk, color=INK, lw=1.6, label="σ_кр(λ): σ_т — Ясинский — Эйлер")
ax.plot(lam[lam >= 60], np.pi ** 2 * E / lam[lam >= 60] ** 2, color=INK2, lw=0.8, ls="--")
for r in it:
    if r["d"] in (6, rd["d"]):
        ax.plot(r["lam"], r["sk"], "o", ms=5, color=ACC if r["d"] == rd["d"] else S1, zorder=5)
        ax.text(r["lam"] - 3, r["sk"] - 14, f"Ø{r['d']:g}: λ = {r['lam']:.0f}, n_у = {fmt(r['ny'], 2)}", fontsize=7.4, ha="right")
ax.axvline(rp["lam_pr"], color=INK2, lw=0.6, ls=":"); ax.text(rp["lam_pr"] + 1, 30, "λ_пред = 100", fontsize=7.2, color=INK2)
ax.set_xlim(20, 160); ax.set_ylim(0, 290); ax.grid(True, color=GRID, lw=0.7)
ax.set_xlabel("гибкость λ = μ·l/i"); ax.set_ylabel("σ_кр, МПа"); ax.set_title("в) критическое напряжение (Ст3)", fontsize=9)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
fig.subplots_adjust(left=0.03, right=0.98, top=0.9, bottom=0.14)
fig.savefig(os.path.join(OUT, "fig12_rod_v13.png"), facecolor="white"); plt.close(fig)

# ====================================================================== рис. 13 — камень-обойма
K_ = R["kul"]; b, h = K_["b"], K_["h"]; lk = R["stone"]["lk"]; s = 4.0
mech = R["mech"]
fig = plt.figure(figsize=(7.9, 3.6), dpi=220)
gs = fig.add_gridspec(1, 2, width_ratios=[1.75, 0.8], wspace=0.08)
ax = fig.add_subplot(gs[0]); ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-16, 70); ax.set_ylim(-26, 30)
th = np.linspace(np.pi / 2, 3 * np.pi / 2, 50)
ax.add_patch(Polygon(np.vstack([[[66, h / 2]], np.column_stack([np.cos(th) * h / 2, np.sin(th) * h / 2]), [[66, -h / 2]]]),
                     closed=True, fc="#e9eef5", ec=INK, lw=1.1))
ax.plot([66, 66], [-h / 2 - 2, h / 2 + 2], color="white", lw=5); ax.plot([65, 67], [-h / 2 - 2, h / 2 + 2], color=INK2, lw=0.8)
ax.add_patch(Circle((0, 0), 2.2, fc="white", ec=INK, lw=1)); ax.text(-3, -5, "O", ha="right", fontsize=8.5)
for z, ls_, lab in ((R["A"]["lOD"], "-", "φу"), (mech["lOD_min"], (0, (3, 2)), "φк"), (mech["lOD_max"], (0, (3, 2)), "φн")):
    ax.add_patch(Rectangle((z - lk / 2, -h / 2 - s), lk, h + 2 * s, fc="#f3ece2" if ls_ == "-" else "none", ec=INK if ls_ == "-" else INK2,
                           lw=1.0, ls=ls_, alpha=0.85 if ls_ == "-" else 1, zorder=3 if ls_ == "-" else 2))
    ax.add_patch(Circle((z, 0), 2.6, fc="white" if ls_ == "-" else "none", ec=INK if ls_ == "-" else INK2, lw=0.9, ls=ls_, zorder=4))
    ax.text(z, h / 2 + s + 1.5 + {"φк": 0, "φу": 4.5, "φн": 9}[lab], f"{lab}: {fmt(z, 1)}", ha="center", fontsize=7.2, color=INK2)
ax.plot([-14, 64], [0, 0], color=INK2, lw=0.5, ls=(0, (8, 2, 1, 2)))
ax.annotate("", xy=(mech["lOD_min"] - lk / 2, -h / 2 - s - 4), xytext=(0, -h / 2 - s - 4), arrowprops=dict(arrowstyle="<->", color=ACC, lw=0.8))
ax.text((mech["lOD_min"] - lk / 2) / 2, -h / 2 - s - 5, fmt(mech["lOD_min"] - lk / 2, 1), ha="center", va="top", fontsize=7.4, color=ACC)
ax.text(30, -h / 2 - 10, f"кулиса — полоса {b:g} × {h:g}", fontsize=7.6, color=INK2)
ax.set_title(f"а) камень-обойма {lk:g} мм на кулисе (сплошная — φу, штриховые — φк и φн)", fontsize=9)
ax = fig.add_subplot(gs[1]); ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-22, 26); ax.set_ylim(-20, 20)
ax.add_patch(Polygon([[-b / 2 - s, -h / 2 - s], [b / 2 + 0.5, -h / 2 - s], [b / 2 + 0.5, -h / 2], [-b / 2, -h / 2], [-b / 2, h / 2],
                      [b / 2 + 0.5, h / 2], [b / 2 + 0.5, h / 2 + s], [-b / 2 - s, h / 2 + s]], closed=True,
                     fc="#f3ece2", ec=INK, lw=1.0, hatch="////"))
ax.add_patch(Rectangle((-b / 2, -h / 2), b, h, fc="#e9eef5", ec=INK, lw=1.0, hatch="\\\\\\\\"))
ax.add_patch(Rectangle((-b / 2 - s - 12, -3), 12, 6, fc="white", ec=INK, lw=1.0))
ax.text(-b / 2 - s - 6, 5, "палец D\nк ползуну", ha="center", va="bottom", fontsize=6.8, color=INK2)
arrow(ax, (0, h / 2 + s + 6), (0, h / 2 + 0.3), VIO, lw=1.1, ms=7)
ax.text(1.5, h / 2 + s + 4, r"$R_{12}^{N}$", fontsize=7.6, color=VIO)
ax.text(b / 2 + 2, 0, f"{b:g} × {h:g}", fontsize=7.4, va="center", color=INK2)
ax.set_title("б) сечение А–А", fontsize=9)
fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.03)
fig.savefig(os.path.join(OUT, "fig13_kamen_v13.png"), facecolor="white"); plt.close(fig)
print("ok")
