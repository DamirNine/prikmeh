# -*- coding: utf-8 -*-
"""Рисунки раздела 12 (v10): 10, 11 — эпюры N, Q, M кулисы при φу и φк; 12 — узел у оси O;
13 — эскиз кулисы с сечениями А–А, Б–Б; 14 — требуемая высота сечения рукояти h(z)."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Wedge
from matplotlib.ticker import FuncFormatter

OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "strength_v10.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "font.size": 9.2,
                     "axes.edgecolor": "#8a8a86", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.titlesize": 9.8, "axes.titleweight": "bold",
                     "axes.titlelocation": "left", "hatch.linewidth": 0.7})
INK, INK2, GRID, S1, S2, S3, SHADE, ACC = "#0b0b0b", "#52514e", "#e6e6e3", "#2a78d6", "#e3742a", "#2f9e6b", "#f1f1ee", "#c4372b"
LIGHT = {S1: "#dbe8f7", S3: "#dcefe5", ACC: "#f6dcd9", S2: "#fbe6d6"}
cm = lambda s: s.replace(".", ",").replace("-", "−")
fmt = lambda x, d: cm(f"{x:.{d}f}")
COMMA = FuncFormatter(lambda v, p: cm(f"{v:g}"))
L = 500.0
H, w, b = float(R["H"]), float(R["w"]), float(R["b"])
lay, hd = R["lay"], R["handle"]
a1, a2, zt, hr = lay["a1"], lay["a2"], hd["zt"], hd["hr"]
dD, dO, Dh = R["pinD"]["d"], R["axO"]["d2"], R["axO"]["Dh"]

def arrow(ax, x0, y0, x1, y1, color=INK, lw=1.4, ms=11):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                                   shrinkA=0, shrinkB=0), zorder=6)

def sign(ax, x, y, s):
    ax.text(x, y, s, ha="center", va="center", fontsize=8.5, color=INK2, zorder=7,
            bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec=INK2, lw=0.7))

# ====================================================================== рис. 10, 11 — эпюры
def epury(pos, fname, tag):
    lOD, N, QOD, QDK, MD = pos["lOD"], pos["N"], pos["Q_OD"], pos["Q_DK"], pos["M_D"] / 1000
    phi = pos["phi"]
    fig = plt.figure(figsize=(7.9, 6.4), dpi=220)
    gs = fig.add_gridspec(4, 2, width_ratios=[1, 2.35], height_ratios=[1.15, 0.75, 1, 1], wspace=0.04, hspace=0.62)
    XL, XR = (-13.0, 42.0), (42.0, 512.0)
    rows = []
    for r in range(4):
        aL = fig.add_subplot(gs[r, 0]); aR = fig.add_subplot(gs[r, 1], sharey=aL)
        aL.set_xlim(*XL); aR.set_xlim(*XR)
        for a in (aL, aR):
            a.spines["top"].set_visible(False); a.xaxis.set_major_formatter(COMMA); a.yaxis.set_major_formatter(COMMA)
        aL.spines["right"].set_visible(False); aR.spines["left"].set_visible(False); aR.tick_params(left=False, labelleft=False)
        aL.set_xticks([0, 10, 20, 30, 40]); aR.set_xticks([100, 200, 300, 400, 500])
        rows.append((aL, aR))
    # --- расчётная схема
    aL, aR = rows[0]
    for a in (aL, aR):
        a.set_ylim(-1.35, 1.35); a.set_yticks([]); a.spines["left"].set_visible(False); a.spines["bottom"].set_visible(False)
        a.set_xticks([])
        a.plot([0, L], [0, 0], color=INK, lw=3.4, solid_capstyle="butt", zorder=3)
    aL.plot([41, 43], [-0.22, 0.22], color="white", lw=6, zorder=4); aL.plot([40.2, 41.8], [-0.25, 0.25], color=INK, lw=0.9, zorder=5)
    aR.plot([42.2, 43.8], [-0.25, 0.25], color=INK, lw=0.9, zorder=5)
    aL.plot(0, 0, "o", ms=7.5, mfc="white", mec=INK, mew=1.4, zorder=6)
    aL.plot(lOD, 0, "s", ms=8, mfc=SHADE, mec=INK, mew=1.2, zorder=6)
    aR.plot(L, 0, "o", ms=4.5, color=INK, zorder=6)
    aL.text(-1.6, -0.62, "O", fontsize=10, ha="right"); aL.text(lOD + 1.8, -0.62, "D", fontsize=10); aR.text(L - 4, 0.30, "K", fontsize=10, ha="right")
    # силы: в осях звена (u — вправо вдоль звена, n — вверх); стрелки начинаются в точке приложения
    arrow(aL, -12.0, 0.0, -0.9, 0.0, color=INK2)                                     # R10,u = P·sin φ (+u)
    aL.text(-6.5, 0.16, r"$R_{10,u}$", fontsize=8.2, color=INK2, ha="center", va="bottom")
    aL.text(-6.5, -0.16, fmt(-N, 1) + " Н", fontsize=8.0, color=INK2, ha="center", va="top")
    arrow(aL, 0.0, -0.05, 0.0, -1.2, color=INK2)                                     # R10,n = Q_OD < 0 (вниз)
    aL.text(1.4, -1.22, r"$R_{10,n}$ = " + fmt(QOD, 1) + " Н", fontsize=8.2, color=INK2, va="bottom")
    arrow(aL, lOD, 0.08, lOD, 1.25, color=INK)                                       # R12N — по нормали n (вверх)
    aL.text(lOD + 1.6, 1.0, r"$R_{12}^{N}$ = " + fmt(pos["R12N"], 1) + " Н", fontsize=8.2)
    aL.annotate("", xy=(0, 0.55), xytext=(lOD, 0.55), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    aL.text(lOD / 2, 0.62, r"$l_{OD}$ = " + fmt(lOD, 2), fontsize=7.8, color=INK2, ha="center", va="bottom")
    arrow(aR, L, 1.25, L, 0.08, color=INK)                                           # P·cos φ (−n)
    aR.text(L - 6, 1.05, r"$P\cos\varphi$ = " + fmt(QDK, 1) + " Н", fontsize=8.2, ha="right")
    arrow(aR, L - 1, -0.38, L - 46, -0.38, color=INK2)                              # P·sin φ (−u)
    aR.text(L - 50, -0.72, r"$P\sin\varphi$ = " + fmt(-N, 1) + " Н", fontsize=8.2, ha="right", color=INK2)
    aR.text(250, 0.42, f"L = 500 мм", fontsize=8.4, color=INK2, ha="center")
    aL.set_title(f"Расчётная схема кулисы при φ = {fmt(phi, 2)}° (силы — по оси u и нормали n звена)", loc="left", color=INK)
    # --- эпюры
    def diag(r, zs, ys, color, ylab, title, lims):
        aL_, aR_ = rows[r]
        for a in (aL_, aR_):
            a.fill_between(zs, 0, ys, facecolor=LIGHT[color], edgecolor=color, hatch="||", lw=0, zorder=2)
            a.plot(zs, ys, color=color, lw=1.6, zorder=3)
            a.axhline(0, color=INK, lw=1.0, zorder=4)
            a.grid(True, axis="y", color=GRID, lw=0.7); a.set_axisbelow(True)
        aL_.set_ylim(*lims); aL_.set_ylabel(ylab)
        aL_.set_title(title, loc="left", color=INK)
        d = 0.018
        aL_.plot((1 - d, 1 + d), (-0.04, 0.04), transform=aL_.transAxes, color=INK2, lw=0.8, clip_on=False)
        aR_.plot((-d * 0.42, d * 0.42), (-0.04, 0.04), transform=aR_.transAxes, color=INK2, lw=0.8, clip_on=False)
        return aL_, aR_
    # N
    aL_, aR_ = diag(1, np.array([0, L]), np.array([N, N]), S3, "N, Н", "Эпюра N — продольная сила (сжатие)", (-130, 60))
    aR_.text(250, N - 18, fmt(N, 1), ha="center", va="top", fontsize=8.6); sign(aR_, 120, N / 2, "−"); sign(aL_, 20, N / 2, "−")
    # Q
    zq = np.array([0, lOD, lOD, L]); yq = np.array([QOD, QOD, QDK, QDK])
    aL_, aR_ = diag(2, zq, yq, S1, "Q, Н", "Эпюра Q — поперечная сила", (-2900, 600))
    aL_.text(lOD / 2, QOD - 80, fmt(QOD, 1), ha="center", va="top", fontsize=8.6)
    aL_.text(lOD + 1.5, QDK + 90, "+" + fmt(QDK, 1), ha="left", va="bottom", fontsize=8.6)
    aR_.text(250, QDK + 90, "+" + fmt(QDK, 1), ha="center", va="bottom", fontsize=8.6)
    sign(aL_, lOD / 2, QOD / 2, "−")
    # M
    zm = np.array([0, lOD, L]); ym = np.array([0, MD, 0])
    aL_, aR_ = diag(3, zm, ym, ACC, "M, Н·м", "Эпюра M — изгибающий момент", (-50, 12))
    aL_.plot(lOD, MD, "o", ms=4.5, color=ACC, zorder=6)
    aL_.text(lOD, MD - 1.6, fmt(MD, 2), ha="center", va="top", fontsize=8.6)
    sign(aR_, 150, MD * 0.35, "−")
    for a in rows[3]:
        a.set_xlabel("")
    fig.text(0.56, 0.035, "z — расстояние от оси O вдоль звена, мм   (слева — участок у оси O в увеличенном масштабе)",
             ha="center", fontsize=8.6, color=INK2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.95, bottom=0.08)
    fig.savefig(os.path.join(OUT, fname), facecolor="white"); plt.close(fig)

epury(R["A"], "fig10_epury_phiy_v10.png", "A")
epury(R["B"], "fig11_epury_phik_v10.png", "B")

# ====================================================================== рис. 12 — узел у оси O
lmin, lmax = lay["lmin"], lay["lmax"]; rb1, dO1 = R["axO"]["rb1"], R["axO"]["d1"]
fig = plt.figure(figsize=(7.9, 5.6), dpi=220)
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.02], hspace=0.30, wspace=0.12)
axa, axb = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]); axc = fig.add_subplot(gs[1, :])

def plate(ax, slot_from, hole=None):
    Hh = H / 2
    th = np.linspace(np.pi / 2, 3 * np.pi / 2, 60)
    xs = np.concatenate([[46], np.cos(th) * Hh, [46]])
    ys = np.concatenate([[Hh], np.sin(th) * Hh, [-Hh]])
    ax.add_patch(Polygon(np.column_stack([xs, ys]), closed=True, fc="#e9eef5", ec=INK, lw=1.2, zorder=1))
    ax.add_patch(Rectangle((slot_from, -w / 2), 50 - slot_from, w, fc="white", ec=INK, lw=1.0, zorder=2))
    ax.plot([46, 46], [-Hh - 2, Hh + 2], color="white", lw=5, zorder=3)
    ax.plot([45.2, 46.8], [-Hh - 2, Hh + 2], color=INK2, lw=0.8, zorder=4)
    if hole:
        ax.add_patch(Circle((0, 0), hole / 2, fc="white", ec=INK, lw=1.1, zorder=3))

def stone(ax, zc, style="solid", hatch="////", fc=SHADE):
    ax.add_patch(Rectangle((zc - w / 2, -w / 2), w, w, fc=fc if style == "solid" else "none", ec=INK, lw=1.0,
                           ls="-" if style == "solid" else (0, (3, 2)), hatch=hatch if style == "solid" else None, zorder=5))
    ax.add_patch(Circle((zc, 0), dD / 2, fc="white" if style == "solid" else "none", ec=INK, lw=0.9,
                        ls="-" if style == "solid" else (0, (3, 2)), zorder=6))

for ax in (axa, axb):
    ax.set_aspect("equal"); ax.set_xlim(-22, 47); ax.set_ylim(-25, 25); ax.axis("off")
    ax.plot([-21, 46], [0, 0], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)), zorder=7)
# а) одна плоскость
plate(axa, rb1 + 1.0, hole=dO1)
axa.add_patch(Circle((0, 0), rb1, fc="none", ec=INK, lw=0.9, ls=(0, (3, 2)), zorder=4))
stone(axa, lmin)
ov = Wedge((0, 0), rb1, -90, 90, fc=ACC, alpha=0.55, ec="none", zorder=8)
axa.add_patch(ov)
clip = Rectangle((lmin - w / 2, -w / 2), w, w, transform=axa.transData)
ov.set_clip_path(clip)
axa.annotate("", xy=(lmin - w / 2, -21), xytext=(rb1, -21), arrowprops=dict(arrowstyle="<->", color=ACC, lw=0.9))
axa.plot([lmin - w / 2] * 2, [-w / 2, -22], color=ACC, lw=0.6); axa.plot([rb1] * 2, [-2, -22], color=ACC, lw=0.6)
axa.text((lmin - w / 2 + rb1) / 2, -23.5, "перекрытие " + fmt(lay["overlap1"], 1) + " мм", ha="center", va="top", fontsize=8.2, color=ACC)
axa.text(-21, 21.5, f"ось O Ø{dO1:g}, бобышка R{rb1:g}", fontsize=8.0, color=INK2)
axa.text(lmin + 1, w / 2 + 1.0, "камень в конце хода", fontsize=8.0, color=INK2)
axa.set_title("а) ось и камень в одной плоскости", loc="left", fontsize=9.4)
# б) принято
plate(axb, a1)
axb.add_patch(Circle((0, 0), Dh / 2, fc="none", ec=S1, lw=1.0, ls=(0, (4, 2)), zorder=4))
axb.add_patch(Circle((0, 0), dO / 2, fc="none", ec=S1, lw=1.0, ls=(0, (4, 2)), zorder=4))
stone(axb, lmin)
stone(axb, lmax, style="dash")
axb.text(-21, 21.5, f"ступица Ø{Dh:g} и ось Ø{dO:g} — позади планки", fontsize=8.0, color=S1)
axb.text(lmax - 2, w / 2 + 1.0, "начало хода", fontsize=8.0, color=INK2)
axb.text(lmin - w / 2 - 0.5, -w / 2 - 1.5, "конец хода", fontsize=8.0, color=INK2, va="top")
axb.annotate("", xy=(0, -21), xytext=(a1, -21), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
axb.plot([a1] * 2, [-w / 2, -22], color=INK2, lw=0.6)
axb.text(a1 / 2 + 1, -23.5, r"$a_1$ = " + fmt(a1, 1), ha="left", va="top", fontsize=8.0, color=INK2)
axb.set_title("б) принято: паз в планке перед ступицей", loc="left", fontsize=9.4)
# в) слои по толщине
ax = axc
ax.set_xlim(-40, 52); ax.set_ylim(-24, 50); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("в) расположение слоёв по толщине", loc="left", fontsize=9.4)
zA = R["A"]["lOD"]
ax.add_patch(Rectangle((-36, -22), 19, 44, fc="#dcdcd8", ec=INK, lw=1.0, hatch="////", zorder=1))
ax.text(-26.5, 24, "стойка", ha="center", fontsize=8.2)
ax.add_patch(Rectangle((-17 + 1 - 1, -Dh / 2), R["axO"]["lh"], Dh, fc="#e9eef5", ec=INK, lw=1.0, zorder=2))
ax.text(-9, Dh / 2 + 1.2, "ступица", ha="center", fontsize=8.2)
ax.add_patch(Rectangle((-34, -dO / 2), 33.5, dO, fc="white", ec=S1, lw=1.0, zorder=3))
ax.text(-16, -dO / 2 - 1.2, f"ось O Ø{dO:g}", fontsize=8.0, color=S1, va="top")
ax.add_patch(Rectangle((0, -H / 2), b, 66, fc="#e9eef5", ec=INK, lw=1.0, zorder=2))
ax.text(b / 2, 48.5, "планка", ha="center", fontsize=8.2)
ax.add_patch(Rectangle((0, zA - w / 2), b, w, fc="none", ec=INK, lw=0.9, ls=(0, (3, 2)), zorder=4))
ax.text(b / 2, zA - w / 2 - 1.2, "камень", ha="center", va="top", fontsize=7.8, color=INK2)
ax.add_patch(Rectangle((b + 1, zA - 12), 12, 24, fc="#f3ece2", ec=INK, lw=1.0, zorder=2))
ax.text(b + 7, zA + 13.2, "ползун", ha="center", fontsize=8.2)
ax.add_patch(Rectangle((0.6, zA - dD / 2), b + 1 + 12 - 0.6, dD, fc="white", ec=ACC, lw=1.0, zorder=5))
ax.text(b + 13.8, zA, f"палец D Ø{dD:g}", fontsize=8.0, color=ACC, va="center")
# плечи
ax.plot([b / 2], [0], "o", ms=5, color=INK, zorder=8); ax.plot([b / 2], [zA], "o", ms=5, color=INK, zorder=8)
ax.annotate("", xy=(-17, -16.5), xytext=(b / 2, -16.5), arrowprops=dict(arrowstyle="<->", color=S1, lw=0.9))
ax.plot([-17, -17], [-22, -15], color=S1, lw=0.6); ax.plot([b / 2] * 2, [-1, -17], color=S1, lw=0.6)
ax.text((-17 + b / 2) / 2, -18, "плечо " + fmt(R["axO"]["arm2"], 0) + " мм", ha="center", va="top", fontsize=8.0, color=S1)
ax.annotate("", xy=(b / 2, zA + 18.5), xytext=(b + 1, zA + 18.5), arrowprops=dict(arrowstyle="<->", color=ACC, lw=0.9))
ax.plot([b / 2] * 2, [zA + 1, zA + 19.5], color=ACC, lw=0.6); ax.plot([b + 1] * 2, [zA + 12, zA + 19.5], color=ACC, lw=0.6)
ax.text(b + 2, zA + 20, "плечо " + fmt(R["pinD"]["arm"], 0) + " мм", ha="left", va="bottom", fontsize=8.0, color=ACC)
fig.subplots_adjust(left=0.02, right=0.99, top=0.95, bottom=0.02)
fig.savefig(os.path.join(OUT, "fig12_node_O_v10.png"), facecolor="white"); plt.close(fig)

# ====================================================================== рис. 13 — эскиз кулисы и сечения
def outline_y(z):
    z = np.asarray(z, float)
    return np.where(z <= a2, H / 2, np.where(z <= zt, H / 2 + (hr / 2 - H / 2) * (z - a2) / (zt - a2), hr / 2))
fig = plt.figure(figsize=(7.9, 4.9), dpi=220)
gs = fig.add_gridspec(2, 3, height_ratios=[0.40, 1.2], width_ratios=[1.6, 0.6, 0.6], hspace=0.10, wspace=0.08)
ax0 = fig.add_subplot(gs[0, :]); ax1 = fig.add_subplot(gs[1, 0]); ax2 = fig.add_subplot(gs[1, 1]); ax3 = fig.add_subplot(gs[1, 2])
def link_patch(ax, zmax=L):
    th = np.linspace(np.pi / 2, 3 * np.pi / 2, 60)
    zz = np.linspace(0, zmax, 400)
    up_ = np.column_stack([zz, outline_y(zz)]); lo_ = np.column_stack([zz[::-1], -outline_y(zz[::-1])])
    arc = np.column_stack([np.cos(th) * H / 2, np.sin(th) * H / 2])
    ax.add_patch(Polygon(np.vstack([[[0, H / 2]], arc, [[0, -H / 2]], np.column_stack([zz, -outline_y(zz)]), np.column_stack([zz[::-1], outline_y(zz[::-1])])]),
                         closed=True, fc="#e9eef5", ec=INK, lw=1.0, zorder=1))
    ax.add_patch(Rectangle((a1, -w / 2), a2 - a1, w, fc="white", ec=INK, lw=0.9, zorder=2))
# общий вид
ax = ax0; link_patch(ax)
ax.set_aspect("equal"); ax.set_xlim(-24, 512); ax.set_ylim(-34, 30); ax.axis("off")
ax.plot([-22, 508], [0, 0], color=INK2, lw=0.5, ls=(0, (10, 2, 1, 2)))
ax.add_patch(Circle((0, 0), Dh / 2, fc="none", ec=S1, lw=0.8, ls=(0, (3, 2)), zorder=3))
for zc_, lab in ((R["A"]["lOD"], "А"), (300.0, "Б")):
    ax.plot([zc_, zc_], [-24, 24], color=INK, lw=0.8, ls=(0, (6, 2)))
    ax.text(zc_ + 2, 22, lab, fontsize=9); ax.text(zc_ + 2, -27, lab, fontsize=9)
ax.annotate("", xy=(0, -31), xytext=(L, -31), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax.text(250, -30, "L = 500", ha="center", va="bottom", fontsize=8.2, color=INK2)
ax.text(zt + 4, hr / 2 + 2, "переход " + fmt(a2, 1) + "…" + fmt(zt, 1), fontsize=7.8, color=INK2)
ax.text(L - 2, hr / 2 + 2, f"рукоять {b:g}×{hr:g}", fontsize=7.8, color=INK2, ha="right")
ax.set_title("а) общий вид звена 1 (планка толщиной 10 мм; штриховая окружность — ступица позади планки)", loc="left", fontsize=9.2)
# зона паза крупно
ax = ax1; link_patch(ax, zmax=70)
ax.set_aspect("equal"); ax.set_xlim(-22, 80); ax.set_ylim(-31, 27); ax.axis("off")
ax.plot([62, 62], [-H / 2 - 3, H / 2 + 3], color="white", lw=6, zorder=3); ax.plot([61, 63], [-H / 2 - 3, H / 2 + 3], color=INK2, lw=0.8, zorder=4)
ax.plot([-20, 60], [0, 0], color=INK2, lw=0.5, ls=(0, (10, 2, 1, 2)))
stone(ax, R["A"]["lOD"])
ax.add_patch(Circle((0, 0), Dh / 2, fc="none", ec=S1, lw=0.8, ls=(0, (3, 2)), zorder=3))
ax.add_patch(Circle((0, 0), dO / 2, fc="none", ec=S1, lw=0.8, ls=(0, (3, 2)), zorder=3))
def dim_h(ax, x0, x1, y, txt, col=INK2):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=col, lw=0.8))
    ax.text((x0 + x1) / 2, y + 0.6, txt, ha="center", va="bottom", fontsize=7.8, color=col)
def dim_v(ax, x, y0, y1, txt, col=INK2, side="left"):
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", color=col, lw=0.8))
    ax.text(x + (-0.8 if side == "left" else 0.8), (y0 + y1) / 2, txt, ha="right" if side == "left" else "left", va="center", fontsize=7.8, color=col, rotation=0)
dim_h(ax, 0, a1, -H / 2 - 4, fmt(a1, 1)); dim_h(ax, 0, a2, -H / 2 - 10, fmt(a2, 1))
for x_ in (a1, a2):
    ax.plot([x_, x_], [-w / 2, -H / 2 - 11], color=INK2, lw=0.5)
ax.plot([0, 0], [-H / 2, -H / 2 - 11], color=INK2, lw=0.5)
dim_v(ax, 68, -H / 2, H / 2, f"H = {H:g}", side="right")
ax.plot([a2, 69], [H / 2, H / 2], color=INK2, lw=0.5); ax.plot([a2, 69], [-H / 2, -H / 2], color=INK2, lw=0.5)
ax.annotate("", xy=(30.5, -w / 2), xytext=(30.5, w / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8), zorder=6)
ax.text(31.2, 4.5, f"w = {w:g}", ha="left", va="center", fontsize=7.8, color=INK2, zorder=7,
        bbox=dict(fc="white", ec="none", pad=0.6))
ax.text(-21, 24, f"камень {w:g}×{w:g}×{b:g} при φу, палец Ø{dD:g}", fontsize=7.8, color=INK2)
ax.set_title("б) зона паза (крупно)", loc="left", fontsize=9.2)
# сечения
def sec(ax, title, parts, Htot):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-14, 22); ax.set_ylim(-Htot / 2 - 9, Htot / 2 + 9)
    for (y0, hh) in parts:
        ax.add_patch(Rectangle((0, y0), b, hh, fc="#e9eef5", ec=INK, lw=1.0, hatch="////", zorder=2))
    ax.annotate("", xy=(0, -Htot / 2 - 4), xytext=(b, -Htot / 2 - 4), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(b / 2, -Htot / 2 - 4.8, f"b = {b:g}", ha="center", va="top", fontsize=7.8, color=INK2)
    ax.annotate("", xy=(-4, -Htot / 2), xytext=(-4, Htot / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(-4.8, 0, f"{Htot:g}", ha="right", va="center", fontsize=7.8, color=INK2)
    ax.set_title(title, loc="left", fontsize=9.2)
t = (H - w) / 2
sec(ax2, "в) А–А", [(-H / 2, t), (w / 2, t)], H)
ax2.annotate("", xy=(b + 3, -w / 2), xytext=(b + 3, w / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
ax2.text(b + 3.8, 0, f"{w:g}", va="center", fontsize=7.8, color=INK2)
ax2.text(b + 1.5, H / 2 - t / 2, f"t = {t:g}", va="center", fontsize=7.8, color=INK2)
sec(ax3, "г) Б–Б", [(-hr / 2, hr)], hr)
ax3.set_ylim(-H / 2 - 9, H / 2 + 9)
fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.02)
fig.savefig(os.path.join(OUT, "fig13_kulisa_v10.png"), facecolor="white"); plt.close(fig)

# ====================================================================== рис. 14 — h(z) рукояти
A = R["A"]; sa = R["mat"]["sig_a"]; Nabs = abs(A["N"]); q = A["Q_DK"]
zz = np.linspace(0, L, 2001)
Mz = np.where(zz <= A["lOD"], abs(A["Q_OD"]) * zz, q * (L - zz))
hreq = (Nabs + np.sqrt(Nabs ** 2 + 24 * sa * b * Mz)) / (2 * sa * b)
fig, ax = plt.subplots(figsize=(7.9, 3.7), dpi=220)
ax.grid(True, color=GRID, lw=0.7); ax.set_axisbelow(True)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
ax.axvspan(0, a2, color=SHADE, lw=0)
ax.text(a2 / 2, -9.5, "зона паза (А–А)", ha="center", va="center", rotation=90, fontsize=7.8, color=INK2,
        bbox=dict(fc=SHADE, ec="none", pad=0.8))
zb = np.arange(a2 + 5, L, 15.0)
hb = (Nabs + np.sqrt(Nabs ** 2 + 24 * sa * b * q * (L - zb))) / (2 * sa * b)
ax.vlines(zb, -hb / 2, hb / 2, color=S1, lw=2.2, zorder=3, label=r"требуемая высота $h_{треб}(z)$ при φу, [σ] = 142 МПа (за пазом " + fmt(hd["h_req_a2"], 1) + " мм)")
ax.plot(zz[zz >= a2], hreq[zz >= a2] / 2, color=S1, lw=0.8, zorder=3); ax.plot(zz[zz >= a2], -hreq[zz >= a2] / 2, color=S1, lw=0.8, zorder=3)
zp = np.linspace(0, L, 1001); yp = outline_y(zp)
ax.plot(zp, yp, color=S2, lw=2.0, zorder=4, label="принятый профиль кулисы с рукоятью")
ax.plot(zp, -yp, color=S2, lw=2.0, zorder=4)
ax.axhline(0, color=INK2, lw=0.8, ls=(0, (10, 2, 1, 2)))
ax.annotate(f"σ = {fmt(hd['sig_max'], 1)} МПа (наибольшее\nв рукояти)", (zt, hr / 2), xytext=(185, 14.5), textcoords="data",
            fontsize=8.2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
ax.text(L - 4, hr / 2 + 1.0, f"{b:g} × {hr:g}", ha="right", va="bottom", fontsize=8.2)
ax.set_xlim(-5, 505); ax.set_ylim(-20, 20)
ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
ax.set_xlabel("z — расстояние от оси O вдоль звена, мм"); ax.set_ylabel("± h/2 относительно оси звена, мм")
ax.set_title("Распределение требуемой высоты сечения по длине кулисы с рукоятью", loc="left", color=INK)
ax.legend(loc="lower right", fontsize=8.2, frameon=True, framealpha=0.95, edgecolor="#d0d0cc")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig14_handle_h_v10.png"), facecolor="white"); plt.close(fig)
print("ok")
