# -*- coding: utf-8 -*-
"""Рисунки презентации 21.11 по замечаниям преподавателя (в fig/, размеры — в fig/sizes.json):
  схема_постановка.png — кинематическая схема для постановки задачи: без численных значений, без e и S;
  схема_результат.png  — та же схема с размерами, полученными в расчётах (значения до десятых);
    у обеих штриховка неподвижного звена (стойки у O и направляющей ползуна) — в одну сторону, 45° (ЕСКД, ГОСТ 2.306-68);
  звено1/2/3.png       — расчётные схемы звеньев (вырезаны из рисунка РПЗ) и ур1/2/3.png — их уравнения равновесия;
  сечения.png          — сечения звеньев, принятые по прочностному расчёту;
  сила_руки_t.png      — сила руки от времени: первичный и уточнённый расчёты и допустимая 120 Н;
  до_после_*.png       — детали прототипа до и после доработки под печать (картинки инструкций 18.11 и 21.11).
    python make_figs.py"""
import json, os
from math import radians, tan, cos, sin, sqrt
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Arc
from matplotlib.transforms import Affine2D
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
KURS = os.path.join(HERE, "..", "..")
RJ = json.load(open(os.path.join(KURS, "2026-11-04", "calc_v21.json"), encoding="utf-8"))
NPZ = np.load(os.path.join(KURS, "2026-11-04", "calc_v21.npz"))
plt.rcParams.update({"font.family": "Calibri", "mathtext.fontset": "custom", "mathtext.rm": "Calibri",
                     "mathtext.it": "Calibri:italic", "mathtext.bf": "Calibri:bold", "font.size": 13})
INK, INK2, BRASS, GREY, RED, BLUE = "#17212E", "#566579", "#C8902E", "#9AA5B2", "#B8432F", "#2F5E9E"
PHANTOM = (0, (9, 2.5, 1.2, 2.5, 1.2, 2.5))
MAIN, THIN = 2.6, 0.9
SIZES = json.load(open(os.path.join(FIG, "sizes.json"), encoding="utf-8"))


def trim_save(fig, name, pad=14):
    path = os.path.join(FIG, name)
    fig.savefig(path, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    im = Image.open(path).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
    im = im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)))
    im.save(path)
    SIZES[name] = im.size
    print(f"  {name}: {im.size}")


def hatch_line(ax, p0, p1, side, n=7, h=0.17):
    """неподвижная опора — линия p0–p1, штрихи по ЕСКД под 45° в одну сторону («/»), со стороны side (единичный вектор)"""
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=INK, lw=1.4, zorder=6)
    d = np.array([1.0, 1.0]) / sqrt(2) * h * sqrt(2)          # штрих «/»: (+h, +h) или (−h, −h)
    sgn = 1 if np.dot(side, [1, 1]) > 0 else -1
    for t in np.linspace(0.08, 1, n):
        a = np.array(p0) + t * (np.array(p1) - np.array(p0))
        b = a + sgn * d
        ax.plot([a[0], b[0]], [a[1], b[1]], color=INK, lw=0.8, zorder=6)


# ---------------------------------------------------------------- кинематическая схема
PH_N, PH_K, PH_OB, PH = RJ["phi_n"], RJ["phi_k"], RJ["phi_ob"], 48.0
E_S, L_S, HK = 2.2, 7.6, 5.0                      # без масштаба: e увеличено относительно L


def scheme(values, name):
    fig, ax = plt.subplots(figsize=(7.4, 7.8))
    ax.set_aspect("equal"); ax.axis("off")
    O = np.zeros(2)
    yD = lambda ph: E_S * tan(radians(ph))
    Kp = lambda ph: L_S * np.array([cos(radians(ph)), sin(radians(ph))])

    def arrow(p0, p1, color, lw=1.6, ms=13):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                          shrinkA=0, shrinkB=0), zorder=8)

    def dim(p0, p1, txt, off_txt, rot=0):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.8, mutation_scale=10,
                                                          shrinkA=0, shrinkB=0), zorder=3)
        m = (np.array(p0) + np.array(p1)) / 2 + np.array(off_txt)
        ax.text(*m, txt, ha="center", va="center", fontsize=15, color=INK, rotation=rot, zorder=9)

    def stone(ph, main):
        r = Rectangle((-0.34, -0.19), 0.68, 0.38, fc="white", ec=INK, lw=1.4 if main else THIN, ls="-" if main else PHANTOM,
                      zorder=6 if main else 4)
        r.set_transform(Affine2D().rotate_deg(ph).translate(E_S, yD(ph)) + ax.transData); ax.add_patch(r)
        ax.add_patch(Circle((E_S, yD(ph)), 0.085, fc="white", ec=INK, lw=1.2 if main else THIN, ls="-" if main else PHANTOM,
                            zorder=7 if main else 5))

    arrow((-0.9, 0), (8.6, 0), INK, lw=1.0, ms=11); ax.text(8.55, -0.35, "x", fontsize=15, ha="center", va="top", style="italic")
    arrow((0, -0.62), (0, 7.7), INK, lw=1.0, ms=11); ax.text(-0.3, 7.6, "y", fontsize=15, ha="right", va="center", style="italic")
    # стойка у O: шарнир на стойке, основание со штриховкой «/» вниз
    ax.add_patch(Circle(O, 0.13, fc="white", ec=INK, lw=1.4, zorder=7))
    ax.plot([0, 0], [-0.13, -0.62], color=INK, lw=2.0, zorder=6)
    hatch_line(ax, (-0.5, -0.62), (0.5, -0.62), (-1, -1))
    # кулиса: крайние положения и рабочее
    for ph in (PH_N, PH_K):
        K_ = Kp(ph); ax.plot([0, K_[0]], [0, K_[1]], color=INK, lw=THIN, ls=PHANTOM, zorder=2)
        stone(ph, False)
    K = Kp(PH)
    ax.plot([0, K[0]], [0, K[1]], color=INK, lw=MAIN, zorder=5, solid_capstyle="round")
    ax.plot(*K, "o", ms=5, color=INK, zorder=8)
    stone(PH, True)
    # ползун 3 в неподвижной направляющей: штриховка обеих стенок — в одну сторону («/»), снаружи
    yh = lambda ph: yD(ph) - HK
    ax.plot([E_S, E_S], [yD(PH) - 0.085, yh(PH)], color=INK, lw=MAIN, zorder=5, solid_capstyle="butt")
    ax.plot([E_S, E_S], [yD(PH) + 0.1, yD(PH_N) - 0.1], color=INK, lw=THIN, ls=PHANTOM, zorder=3)
    ax.plot([E_S, E_S], [yh(PH), yh(PH_K)], color=INK, lw=THIN, ls=PHANTOM, zorder=3)
    gy0, gy1 = -1.0, -0.2
    hatch_line(ax, (E_S - 0.2, gy0), (E_S - 0.2, gy1), (-1, -1), n=5)
    hatch_line(ax, (E_S + 0.2, gy0), (E_S + 0.2, gy1), (1, 1), n=5)
    # силы
    arrow(K + np.array([0, 1.5]), K + np.array([0, 0.12]), BLUE, lw=2.0, ms=15)
    ax.text(K[0] + 0.15, K[1] + 1.2, "P", color=BLUE, fontsize=17, ha="left", va="center", style="italic")
    # сопротивление укупориванию действует на ползун снизу вверх — как на расчётных схемах звеньев (21.11, замечание Корнеева)
    arrow((E_S, yh(PH) - 0.75), (E_S, yh(PH) - 0.04), RED, lw=2.0, ms=13)
    ax.text(E_S - 0.45, yh(PH) - 0.45, r"$F_{\mathrm{ук}}$", color=RED, fontsize=17, ha="right", va="center")
    # обозначения
    ax.text(-0.25, 0.25, "O", fontsize=16, ha="right", va="bottom")
    ax.text(E_S - 0.4, yD(PH) + 0.3, "D", fontsize=16, ha="right", va="bottom")
    ax.text(K[0] + 0.12, K[1] - 0.2, "K", fontsize=16, ha="left", va="top")
    ax.text(*(0.9 * K - 0.35 * np.array([-sin(radians(PH)), cos(radians(PH))])), "1", fontsize=16, ha="center", va="center")
    ax.text(E_S + 0.45, yD(PH) + 0.1, "2", fontsize=16, ha="left", va="bottom")
    ax.text(E_S + 0.42, yh(PH) + 0.42, "3", fontsize=16, ha="left", va="center")
    ax.text(0.45, -0.95, "0", fontsize=16, ha="left", va="center")
    for ph, lab, val in ((PH_N, r"$\varphi_{\mathrm{н}}$", f"{PH_N:.1f}°"), (PH_K, r"$\varphi_{\mathrm{к}}$", f"{PH_K:.1f}°")):
        K_ = Kp(ph)
        t = lab + (f" = {val}".replace(".", ",") if values else "")
        nrm = np.array([-sin(radians(ph)), cos(radians(ph))]) * (1 if ph > 45 else -1)   # φн — слева от линии, φк — под ней
        ax.text(*(0.86 * K_ + 0.42 * nrm), t, fontsize=15, color=INK2, ha="center", va="center",
                rotation=ph, rotation_mode="anchor")
    ax.add_patch(Arc(O, 2.6, 2.6, theta1=0, theta2=PH, color=INK, lw=0.9, zorder=4))
    ax.text(1.55 * cos(radians(PH / 2)), 1.55 * sin(radians(PH / 2)), r"$\varphi$", fontsize=17, ha="center", va="center")
    ax.text(*(0.72 * K + 0.36 * np.array([-sin(radians(PH)), cos(radians(PH))])), "L = OK = 500 мм" if values else "L = OK",
            fontsize=15, rotation=PH, ha="center", va="center", rotation_mode="anchor")
    if values:                                    # размеры — только после расчётов
        Bn, Bk = np.array([E_S, yD(PH_N)]), np.array([E_S, yD(PH_K)])
        xs = E_S + 2.0
        for p in (Bn, Bk):
            ax.plot([p[0] + 0.1, xs + 0.15], [p[1], p[1]], color=INK2, lw=0.6, zorder=2)
        dim((xs, Bn[1]), (xs, Bk[1]), "", (0, 0))
        ax.text(xs + 0.12, Bk[1] - 0.42, "S = 16 мм", fontsize=15, ha="left", va="center")
        ax.plot([E_S, E_S], [yh(PH_K) - 0.1, -5.15], color=INK2, lw=0.6, zorder=2)
        ax.plot([0, 0], [-1.0, -5.15], color=INK2, lw=0.6, zorder=2)
        dim((0, -5.0), (E_S, -5.0), "", (0, 0))
        ax.text(E_S + 0.25, -5.0, "e = 12,5 мм", fontsize=15, ha="left", va="center")
    ax.set_xlim(-1.1, 9.2); ax.set_ylim(-5.4 if values else -3.6, 7.9)
    trim_save(fig, name)


# ---------------------------------------------------------------- уравнения равновесия звеньев
EQ = {
    "ур1.png": [r"$\sum F_x:\ R_{10}^{x} + R_{12}^{N}\cos(\varphi + 90^\circ) = 0$",
                r"$\sum F_y:\ R_{10}^{y} + R_{12}^{N}\sin(\varphi + 90^\circ) - P = 0$",
                r"$\sum M_M:\ R_{10}^{x}\,y_M + R_{10}^{y}\,x_M + R_{12}^{N}\,a(\varphi) + M_{12} - P\,X_K = 0$"],
    "ур2.png": [r"$\sum F_x:\ R_{12}^{N}\cos(\varphi - 90^\circ) + R_{23}^{x} = 0$",
                r"$\sum F_y:\ R_{12}^{N}\sin(\varphi - 90^\circ) + R_{23}^{y} = 0$",
                r"$\sum M_M:\ -R_{12}^{N}\,a(\varphi) - M_{12} + R_{23}^{x}\,Y_D + R_{23}^{y}\,X_D = 0$"],
    "ур3.png": [r"$\sum F_x:\ -R_{23}^{x} + R_{30}^{N} = 0$",
                r"$\sum F_y:\ -R_{23}^{y} + F_{\mathrm{ук}} = 0$",
                r"$\sum M_M:\ -R_{23}^{x}\,Y_D - R_{23}^{y}\,X_D + R_{30}^{N}\,Y_D + M_{30} + F_{\mathrm{ук}}\,X_D = 0$"],
}


# 21.11 (Корнеев А.Е.: «формулы — нормально, красиво, не просто текстом»): формулы слайдов — математическим набором STIX
FORMULAS = {
    "ф_обжим.png": [r"$F_{\mathrm{ук}} = n\,\sigma_{\mathrm{раб}}\,A\,\ln\dfrac{D_k}{D_{\mathrm{обж}}} = 1974\ \mathrm{Н}$"],
    "ф_синтез.png": [r"$S = e\,(\mathrm{tg}\,\varphi_{\mathrm{н}} - \mathrm{tg}\,\varphi_{\mathrm{к}})$",
                     r"$A = \dfrac{1}{2}\,e\,S \rightarrow \min, \qquad \psi = \varphi_{\mathrm{н}} - \varphi_{\mathrm{к}} \rightarrow \min$"],
    "ф_кинематика.png": [r"$y_D = e\,\mathrm{tg}\,\varphi$",
                         r"$v_D = \dfrac{e\,\omega}{\cos^2\varphi}, \qquad a_D = \dfrac{e\,(\varepsilon + 2\,\omega^2\,\mathrm{tg}\,\varphi)}{\cos^2\varphi}$"],
    "ф_равновесие.png": [r"$\sum F_x = 0, \qquad \sum F_y = 0, \qquad \sum M = 0$"],
    "ф_сила_руки.png": [r"$P(\varphi) = \dfrac{F_{\mathrm{ук}}\,e}{L\,\cos^3\varphi}$"],
    "ф_момент.png": [r"$|M_D| = P\,(L\cos\varphi - e)$"],
    "ф_прочность.png": [r"$\sigma = \dfrac{N}{A} + \dfrac{M}{W} \leq [\sigma] = \dfrac{\sigma_{\mathrm{т}}}{n}, \quad n = 2{,}5$",
                        r"$n_{\mathrm{у}} = \dfrac{F_{\mathrm{кр}}}{F_{\mathrm{ук}}} \geq 3$"],
    "ф_инерция.png": [r"$\Phi = -m\,a_S, \qquad M_{\Phi} = -J_S\,\varepsilon, \qquad G = m\,g$"],
}


def equations():
    plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
    for name, lines in list(EQ.items()) + list(FORMULAS.items()):
        tall = any("dfrac" in x for x in lines)
        fig = plt.figure(figsize=(7.0, (0.95 if tall else 0.62) * len(lines)))
        for i, s in enumerate(lines):
            fig.text(0.0, 1 - (i + 0.5) / len(lines), s, fontsize=19, color="#1E1E1E", ha="left", va="center")
        trim_save(fig, name, pad=10)
    plt.rcParams.update({"mathtext.fontset": "custom", "font.family": "Calibri"})


def links():
    """звенья 1, 2, 3 из общего рисунка расчётных схем РПЗ (доли ширины/высоты подобраны по рисунку)"""
    im = Image.open(os.path.join(FIG, "схемы_первичный.png")).convert("RGB")
    W, H = im.size
    g = np.asarray(im.convert("L")) < 235
    cols = g.any(axis=0)
    xs = [x for x in range(int(0.5 * W), int(0.75 * W)) if not cols[x]]          # белый столбец между звеном 1 и звеньями 2–3
    xc = max(xs, key=lambda x: sum(1 for k in range(x, min(x + 200, W)) if not cols[k])) if xs else int(0.645 * W)
    rows = g[:, xc:].any(axis=1)
    ys = [y for y in range(int(0.3 * H), int(0.62 * H)) if not rows[y]]           # белая строка между звеньями 2 и 3
    runs, start = [], None
    for y in range(int(0.3 * H), int(0.62 * H)):
        if not rows[y] and start is None:
            start = y
        if rows[y] and start is not None:
            runs.append((start, y)); start = None
    a, b = max(runs, key=lambda r: r[1] - r[0])
    yc = (a + b) // 2
    print(f"  граница звеньев: x = {xc / W:.3f}, y = {yc / H:.3f}")
    boxes = {"звено1.png": (0, 0, xc / W, 1.0), "звено2.png": (xc / W, 0, 1.0, yc / H), "звено3.png": (xc / W, yc / H, 1.0, 1.0)}
    for name, (x0, y0, x1, y1) in boxes.items():
        c = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
        bb = ImageChops.difference(c, Image.new("RGB", c.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
        c = c.crop((max(bb[0] - 12, 0), max(bb[1] - 12, 0), min(bb[2] + 12, c.width), min(bb[3] + 12, c.height)))
        c.save(os.path.join(FIG, name))
        SIZES[name] = c.size
        print(f"  {name}: {c.size}")


# ---------------------------------------------------------------- сечения
def sections():
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    ax.set_aspect("equal"); ax.axis("off")
    plt.rcParams["hatch.linewidth"] = 1.0

    def dimh(x0, x1, y, txt):
        ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.8, mutation_scale=9,
                                                                    shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, y - 1.4, txt, ha="center", va="top", fontsize=15, color=INK)

    def dimv(x, y0, y1, txt):
        ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=0.8, mutation_scale=9,
                                                                    shrinkA=0, shrinkB=0))
        ax.text(x + 1.2, (y0 + y1) / 2, txt, ha="left", va="center", fontsize=15, color=INK)

    # кулиса 8 × 18
    ax.add_patch(Rectangle((0, 0), 8, 18, fc="white", ec=INK, lw=1.8, hatch="///"))
    dimh(0, 8, -2.5, "8"); dimv(10.5, 0, 18, "18")
    ax.text(4, 23.5, "Кулиса", ha="center", fontsize=17, weight="bold", color=INK)
    ax.text(4, 21.0, "полоса 8 × 18, Ст3сп", ha="center", fontsize=14, color=INK2)
    # шток Ø8
    cx = 32
    ax.add_patch(Circle((cx, 9), 4, fc="white", ec=INK, lw=1.8, hatch="///"))
    ax.plot([cx - 6, cx + 6], [9, 9], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)))
    ax.plot([cx, cx], [3, 15], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)))
    dimh(cx - 4, cx + 4, 2.5, "Ø8")
    ax.text(cx, 23.5, "Шток ползуна", ha="center", fontsize=17, weight="bold", color=INK)
    ax.text(cx, 21.0, "круг Ø8, Ст3сп", ha="center", fontsize=14, color=INK2)
    # ось O и палец D Ø10
    cx = 58
    ax.add_patch(Circle((cx, 9), 5, fc="white", ec=INK, lw=1.8, hatch="///"))
    ax.plot([cx - 7, cx + 7], [9, 9], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)))
    ax.plot([cx, cx], [2, 16], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)))
    dimh(cx - 5, cx + 5, 1.5, "Ø10")
    ax.text(cx, 23.5, "Ось O, палец D", ha="center", fontsize=17, weight="bold", color=INK)
    ax.text(cx, 21.0, "Ø10, сталь 45 / 40Х", ha="center", fontsize=14, color=INK2)
    ax.set_xlim(-3, 68); ax.set_ylim(-6, 26)
    trim_save(fig, "сечения.png")


# ---------------------------------------------------------------- сила руки от времени
def t_of_phi(phs):
    w, tr, tu, tt = RJ["w"], RJ["t_r"], RJ["t_u"], RJ["t_t"]
    er, et = w / tr, w / tt
    dr, du = w * tr / 2, w * tu
    d = np.radians(RJ["phi_n"] - phs)
    t = np.where(d <= dr, np.sqrt(2 * np.clip(d, 0, None) / er), 0.0)
    t = np.where((d > dr) & (d <= dr + du), tr + (d - dr) / w, t)
    d3 = np.clip(d - dr - du, 0, None)
    t = np.where(d > dr + du, tr + tu + (w - np.sqrt(np.clip(w * w - 2 * et * d3, 0, None))) / et, t)
    return t


def force_time():
    phs, X0, X1 = NPZ["phs"], NPZ["X0"], NPZ["X1"]
    t = t_of_phi(phs)
    o = np.argsort(t)
    t, P0, P1 = t[o], X0[o, 8], X1[o, 8]
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    ax.axvspan(t[np.argmax(P0 > 1)] if (P0 > 1).any() else 0.44, t[-1], color="#EEF0F3", zorder=0)
    ax.plot(t, P0, color=GREY, lw=2.4, label="первичный расчёт")
    ax.plot(t, P1, color=BRASS, lw=2.4, label="уточнённый расчёт")
    ax.axhline(120, color=RED, lw=1.8, ls=(0, (6, 3)), label="допустимая 120 Н")
    i0, i1 = np.argmax(P0), np.argmax(P1)
    ax.plot(t[i0], P0[i0], "o", color=GREY, ms=7); ax.plot(t[i1], P1[i1], "o", color=BRASS, ms=7)
    ax.annotate(f"{RJ['P0max']:.1f} Н".replace(".", ","), (t[i0], P0[i0]), xytext=(-66, 2), textcoords="offset points",
                fontsize=14, color=INK2)
    ax.annotate(f"{RJ['P1max']:.1f} Н".replace(".", ","), (t[i1], P1[i1]), xytext=(12, -16), textcoords="offset points",
                fontsize=14, color=BRASS, weight="bold")
    ax.set_xlabel("t, с", fontsize=15); ax.set_ylabel("P, Н", fontsize=15)
    ax.set_xlim(0, t[-1]); ax.set_ylim(-10, 135)
    ax.grid(color="#DDE1E6", lw=0.7); ax.tick_params(labelsize=13, colors=INK2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="center left", bbox_to_anchor=(0.01, 0.5), fontsize=13, frameon=False)
    ax.text(0.47, 128, "обжим", fontsize=13, color=INK2)
    trim_save(fig, "сила_руки_t.png")


# ---------------------------------------------------------------- до / после
def before_after():
    old = os.path.join(KURS, "2026-11-18", "инструкция", "img")
    new = os.path.join(KURS, "2026-11-21", "инструкция", "img")
    for name, src in (("до_направляющая.png", os.path.join(old, "p_guide.png")),
                      ("после_направляющая.png", os.path.join(new, "p_guide.png")),
                      ("до_ползун.png", os.path.join(old, "p_polzun.png")),
                      ("после_ползун.png", os.path.join(new, "p_polzun.png")),
                      ("после_головка.png", os.path.join(new, "p_head.png")),
                      ("сборка_узел.png", os.path.join(new, "155_головка.png"))):
        im = Image.open(src).convert("RGB")
        im.save(os.path.join(FIG, name))
        SIZES[name] = im.size
        print(f"  {name}: {im.size}")


scheme(False, "схема_постановка.png")
scheme(True, "схема_результат.png")
equations()
links()
sections()
force_time()
before_after()
json.dump(SIZES, open(os.path.join(FIG, "sizes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("готово")
