# -*- coding: utf-8 -*-
"""Слайд 5 (синтез, Корнеев 23.11 23:51): схема с крайними положениями; выделены треугольник O–Bн–Bк
(площадь A = e·S/2 → min) и угловой ход ψ = φн − φк. Основа — make_schemes_v3.py. → fig/схема_синтез.png
Кинематическая схема v2 (Корнеев, 23.11 22:41): «преподаватель сказал просто повернуть данный рисунок на 90° и
расставить обозначения» — образец fig/образец_схемы_22-41.jpg (кулиса 1 — камень 2 — звено 3) повёрнут на 90° против
часовой: кулиса из O вверх-вправо, звено 3 вертикально. Оси xOy — как раньше (O в начале, x вправо, y вверх).
Вторую стойку справа не рисуем (Корнеев убрал её намеренно).
Камень и направляющая — по эскизу Корнеева 23.11 23:15 (fig/образец_камня_23-15.jpg). Кинематические пары как на образце: O(1-0) вращательная, C(1-2) поступательная, D(2-3) вращательная.
  fig/схема_постановка.png — без чисел; fig/схема_результат.png — с размерами и крайними положениями.
    python make_schemes_v2.py"""
import json, os
from math import radians, tan, cos, sin
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc, Polygon
from matplotlib.transforms import Affine2D
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
KURS = os.path.join(HERE, "..", "..")
RJ = json.load(open(os.path.join(KURS, "2026-11-04", "calc_v21.json"), encoding="utf-8"))
SIZES = json.load(open(os.path.join(FIG, "sizes.json"), encoding="utf-8"))
TNR = "Times New Roman"
plt.rcParams.update({"font.family": TNR, "mathtext.fontset": "custom", "mathtext.rm": TNR,
                     "mathtext.it": TNR + ":italic", "mathtext.bf": TNR + ":bold", "font.size": 16})
K_ = "black"
HL, HL_FILL = "#B8432F", "#F6D5CF"           # выделение треугольника синтеза
LW, THIN = 2.0, 0.9
PHANTOM = (0, (10, 2.5, 1.5, 2.5, 1.5, 2.5))
PH_N, PH_K, PH = RJ["phi_n"], RJ["phi_k"], 46.0
E_S, L_S = 2.4, 7.6                 # без масштаба: e увеличено относительно L
RJ_ = 0.17                          # радиус кружка шарнира
STONE = (1.25, 0.8)                 # камень: длина вдоль кулисы × ширина


def trim_save(fig, name, pad=16):
    path = os.path.join(FIG, name)
    fig.savefig(path, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    im = Image.open(path).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
    im = im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)))
    im.save(path)
    SIZES[name] = im.size
    print(f"  {name}: {im.size}")


def scheme(values, name, synth=False):
    fig, ax = plt.subplots(figsize=(8.4, 8.6))
    ax.set_aspect("equal"); ax.axis("off")
    u = lambda ph: np.array([cos(radians(ph)), sin(radians(ph))])
    nrm = lambda ph: np.array([-sin(radians(ph)), cos(radians(ph))])
    yD = lambda ph: E_S * tan(radians(ph))

    def line(p0, p1, lw=LW, ls="-", z=5, cap="butt"):
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=K_, lw=lw, ls=ls, zorder=z, solid_capstyle=cap)

    def ground(p0, p1, side, n=5, h=0.28):
        """неподвижное звено: линия p0–p1 и штрихи на сторону side; все штрихи на схеме параллельны — наклон «/»
        (Корнеев 23.11: «стойка смотрит в одну сторону», без «ёлочки»)"""
        p0, p1 = np.array(p0, float), np.array(p1, float)
        line(p0, p1, lw=1.6, z=6)
        d = h * np.array([1.0, 1.0]) * (1 if np.dot(side, [1, 1]) > 0 else -1)
        L = np.linalg.norm(p1 - p0); dt = np.dot(d, (p1 - p0) / L) / L       # штрих не выходит за концы линии
        for k in np.linspace(max(0, -dt), min(1, 1 - dt), n):
            a = p0 + k * (p1 - p0)
            line(a, a + d, lw=1.1, z=6)

    def joint(c, lw=1.6, ls="-", z=9, r=RJ_):
        ax.add_patch(Circle(c, r, fc="white", ec=K_, lw=lw, ls=ls, zorder=z))

    def shelf(p, to, txt, right=True):
        """выноска с полкой, номер звена над полкой (как на образце)"""
        p, to = np.array(p, float), np.array(to, float)
        end = to + np.array([0.75 if right else -0.75, 0])
        line(p, to, lw=0.9, z=3); line(to, end, lw=0.9, z=3)
        ax.text((to[0] + end[0]) / 2, to[1] + 0.08, txt, fontsize=18, ha="center", va="bottom")

    def pair(p, letter, sup, sub, ha="left"):
        ax.text(*p, rf"$\mathbf{{{letter}}}^{{\mathbf{{{sup}}}}}_{{\mathbf{{{sub}}}}}$", fontsize=21, ha=ha, va="center")

    def arrow(p0, p1, lw=1.8, ms=16):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=K_, lw=lw, mutation_scale=ms,
                                                          shrinkA=0, shrinkB=0), zorder=8)

    def stone(ph, main):
        """камень 2 по эскизу Корнеева (23.11 23:15): прямоугольник на кулисе, внутри шарнир D; звено 3 — вертикальная
        прямая, огибающая палец D полуокружностью слева (сверху вниз), выходит из камня вверх и вниз"""
        lw, ls, z = (1.6, "-", 7) if main else (THIN, PHANTOM, 4)
        D = np.array([E_S, yD(ph)])
        r = Rectangle((-STONE[0] / 2, -STONE[1] / 2), *STONE, fc="white" if (main or not synth) else "none", ec=K_,
                      lw=lw, ls=ls, zorder=z)
        r.set_transform(Affine2D().rotate_deg(ph).translate(*D) + ax.transData); ax.add_patch(r)
        rb = RJ_ + 0.12
        ax.add_patch(Arc(D, 2 * rb, 2 * rb, theta1=90, theta2=270, color=K_, lw=lw, ls=ls, zorder=z + 1))
        half = (STONE[1] / 2) / cos(radians(ph))                    # от D до края камня по вертикали x = e
        lw3 = LW if main else THIN
        line((E_S, D[1] + rb), (E_S, D[1] + half + (0.55 if main else 0)), lw=lw3, ls=ls, z=z + 1)
        line((E_S, D[1] - rb), (E_S, D[1] - half), lw=lw3, ls=ls, z=z + 1)
        joint(D, lw=lw, ls=ls, z=z + 2)
        return D

    O = np.zeros(2)
    # оси xOy — как в презентации и РПЗ
    arrow((-0.2, 0), (8.6, 0), lw=0.9, ms=12); ax.text(8.6, -0.28, "x", fontsize=19, ha="center", va="top", style="italic")
    arrow((0, -0.2), (0, 8.4), lw=0.9, ms=12); ax.text(-0.22, 8.35, "y", fontsize=19, ha="right", va="center", style="italic")
    # стойка 0 у шарнира O: на образце — сверху, после поворота — слева
    a0 = np.array([-0.75, 0])
    line(O, a0 + [0, 0.32], lw=1.6); line(O, a0 - [0, 0.32], lw=1.6)
    ground(a0 + [0, 0.7], a0 - [0, 0.7], (-1, 0), n=6)
    ax.text(-1.45, -0.95, "0", fontsize=18, ha="center", va="center", weight="bold")

    if values:                                   # крайние положения кулисы и камня
        for ph, ln in ((PH_N, 1.0), (PH_K, 0.8)):
            line(O, ln * L_S * u(ph), lw=THIN, ls=PHANTOM, z=2)
            stone(ph, False)
    Kp = L_S * u(PH)
    line(O + RJ_ * u(PH), Kp, cap="round")                     # кулиса 1
    joint(O)
    D = stone(PH, True)
    # звено 3 ниже камня — через направляющую
    yb = -2.6
    line((E_S, D[1] - (STONE[1] / 2) / cos(radians(PH))), (E_S, yb))
    # направляющая 3–0 по эскизу: две линии по обе стороны звена 3, штриховка снаружи
    g0, g1 = -1.9, -0.75
    ground((E_S - 0.3, g1), (E_S - 0.3, g0), (-1, 0), n=5)
    ground((E_S + 0.3, g1), (E_S + 0.3, g0), (1, 0), n=5)
    ax.text(E_S + 0.9, (g0 + g1) / 2, "0", fontsize=18, ha="left", va="center", weight="bold")

    # обозначения кинематических пар (как на образце)
    ax.text(0.3, -0.42, "O", fontsize=21, ha="left", va="center", weight="bold")   # индексы пар убраны (Корнеев 23:26)
    C = 0.75 * D
    # подпись пары C¹²₁П убрана (Корнеев 23.11 23:20: «убери эти штуки»)
    ax.text(*(D + np.array([0.78, -0.22])), "D", fontsize=21, ha="left", va="center", weight="bold")
    # номера звеньев на полках
    shelf(0.99 * Kp, 0.99 * Kp + np.array([0.5, -0.45]), "1")
    shelf(D - 0.3 * u(PH) + 0.4 * nrm(PH), (1.2, 3.1), "2", right=False)
    shelf((E_S, -2.4), (1.45, -2.1), "3", right=False)
    # точка K, силы, угол φ
    ax.text(Kp[0] - 0.3, Kp[1] + 0.02, "K", fontsize=19, ha="right", va="bottom", weight="bold")
    arrow(Kp + np.array([0, 1.45]), Kp + np.array([0, 0.04]), lw=2.0)
    ax.text(Kp[0] + 0.18, Kp[1] + 1.05, "P", fontsize=21, ha="left", va="center", style="italic")
    arrow((E_S, yb - 1.0), (E_S, yb - 0.04), lw=2.0)
    ax.text(E_S + 0.2, yb - 0.55, r"$F_{\mathrm{ук}}$", fontsize=21, ha="left", va="center")
    if not synth:
        ax.add_patch(Arc(O, 2.6, 2.6, theta1=0, theta2=PH, color=K_, lw=0.9, zorder=4))
        ax.text(1.6 * cos(radians(PH / 2)), 1.6 * sin(radians(PH / 2)), r"$\varphi$", fontsize=21, ha="center", va="center")
    else:                                        # синтез: треугольник O–Bн–Bк (площадь → min) и угловой ход ψ
        Bn, Bk = np.array([E_S, yD(PH_N)]), np.array([E_S, yD(PH_K)])
        ax.add_patch(Polygon([O, Bn, Bk], closed=True, fc=HL_FILL, ec="none", zorder=1.5))
        ax.add_patch(Polygon([O, Bn, Bk], closed=True, fc="none", ec=HL, lw=2.6, zorder=8.5))
        for p_ in (Bn, Bk):
            ax.add_patch(Circle(p_, 0.07, fc=HL, ec=HL, zorder=12))
        ax.add_patch(Arc(O, 3.2, 3.2, theta1=PH_K, theta2=PH_N, color=HL, lw=2.2, zorder=6))
        am = radians((PH_N + PH_K) / 2)
        ax.text(1.95 * cos(am), 1.95 * sin(am), r"$\psi$", fontsize=24, color=HL, ha="center", va="center", zorder=9)
        ax.text(*(Bn + np.array([0.72, 0.38])), r"$\mathbf{B}_{\mathbf{н}}$", fontsize=21, color=HL, ha="left", va="center")
        ax.text(*(Bk + np.array([0.62, -0.62])), r"$\mathbf{B}_{\mathbf{к}}$", fontsize=21, color=HL, ha="left", va="center")
        ax.text(4.0, -0.95, r"$A_{OB_{\mathrm{н}}B_{\mathrm{к}}} = \frac{1}{2}\,e\,S \rightarrow \min$", fontsize=21,
                color=HL, ha="left", va="center")
        ax.text(4.0, -1.85, r"$\psi = \varphi_{\mathrm{н}} - \varphi_{\mathrm{к}}$", fontsize=21, color=HL, ha="left",
                va="center")
    if values:
        for ph, ln, lab, val in ((PH_N, 1.0, r"\varphi_{\mathrm{н}}", PH_N), (PH_K, 0.8, r"\varphi_{\mathrm{к}}", PH_K)):
            side = 1 if ph > 45 else -1
            t = rf"${lab}$ = {val:.1f}°".replace(".", ",")
            ax.text(*((ln - 0.1) * L_S * u(ph) + 0.36 * side * nrm(ph)), t, fontsize=17, ha="center", va="center",
                    rotation=ph, rotation_mode="anchor")
        ax.text(*(0.79 * Kp - 0.34 * nrm(PH)), "L = OK = 500 мм", fontsize=13, rotation=PH, ha="center", va="center",
                rotation_mode="anchor")
        Bn, Bk = np.array([E_S, yD(PH_N)]), np.array([E_S, yD(PH_K)])
        xs = -1.6
        for p in (Bn, Bk):
            line((p[0] - 0.75, p[1]), (xs - 0.15, p[1]), lw=0.6, z=2)
        ax.annotate("", xy=(xs, Bk[1]), xytext=(xs, Bn[1]), arrowprops=dict(arrowstyle="<|-|>", color=K_, lw=0.8,
                                                                           mutation_scale=11, shrinkA=0, shrinkB=0))
        ax.text(xs - 0.15, (Bn[1] + Bk[1]) / 2, "S = 16 мм", fontsize=17, ha="right", va="center", rotation=90)
        ybot = yb - 1.5
        line((0, -0.25), (0, ybot - 0.15), lw=0.6, z=2)
        line((E_S, yb - 1.05), (E_S, ybot - 0.15), lw=0.6, z=2)
        ax.annotate("", xy=(E_S, ybot), xytext=(0, ybot), arrowprops=dict(arrowstyle="<|-|>", color=K_, lw=0.8,
                                                                         mutation_scale=11, shrinkA=0, shrinkB=0))
        ax.text(E_S / 2, ybot + 0.1, "e = 12,5 мм", fontsize=17, ha="center", va="bottom")
    ax.set_xlim(-2.6 if values else -2.0, 9.0); ax.set_ylim(yb - (2.0 if values else 1.2), 8.7)
    trim_save(fig, name)


if __name__ == "__main__":
    scheme(True, "схема_синтез.png", synth=True)
    json.dump(SIZES, open(os.path.join(FIG, "sizes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
