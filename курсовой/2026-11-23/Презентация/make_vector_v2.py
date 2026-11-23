# -*- coding: utf-8 -*-
"""v2 (23.11 23:24): только вектор_контур.png — точки O, B, D обычные маленькие чёрные.
Исходный docstring:
Кинематические схемы 23.11 по замечанию преподавателя («неаккуратно и неправильно») — в стиле образца Корнеева
(схема механизма полки, фото 23.11 16:26) и ДЗ прошлого семестра:
  чёрно-белые; шарниры — полые кружки с буквой внутри (не чёрные точки); неподвижный шарнир O — кружок на
  треугольной опоре со штриховкой основания; камень — прямоугольник на кулисе, внутри шарнир D, звено 3 огибает
  палец дугой; направляющая ползуна — две параллельные линии со штриховкой снаружи; названия звеньев — выносками.
  fig/схема_постановка.png — без численных значений; fig/схема_результат.png — с размерами из расчёта.
    python make_schemes.py"""
import json, os
from math import radians, tan, cos, sin
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Arc, PathPatch
from matplotlib.path import Path
from matplotlib.transforms import Affine2D
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
KURS = os.path.join(HERE, "..", "..")
RJ = json.load(open(os.path.join(KURS, "2026-11-04", "calc_v21.json"), encoding="utf-8"))
SIZES = json.load(open(os.path.join(FIG, "sizes.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "Arial", "mathtext.fontset": "custom", "mathtext.rm": "Arial",
                     "mathtext.it": "Arial:italic", "font.size": 14})
K_ = "black"
MAIN, THIN = 2.4, 0.9
PHANTOM = (0, (10, 2.5, 1.5, 2.5, 1.5, 2.5))
PH_N, PH_K, PH = RJ["phi_n"], RJ["phi_k"], 46.0
E_S, L_S, HK = 2.4, 7.6, 4.9
PH_LEN = {"н": 1.0, "к": 0.8}                            # крайние положения кулисы — короче рабочего, чтобы не мешать подписям            # без масштаба: e увеличено относительно L, чтобы камень и ползун были видны
RJ_ = 0.21                               # радиус кружка шарнира
STONE = (1.0, 0.62)                      # камень: длина вдоль кулисы × ширина


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


def scheme(values, name):
    fig, ax = plt.subplots(figsize=(8.6, 8.4))
    ax.set_aspect("equal"); ax.axis("off")
    yD = lambda ph: E_S * tan(radians(ph))
    u = lambda ph: np.array([cos(radians(ph)), sin(radians(ph))])          # орт кулисы
    nrm = lambda ph: np.array([-sin(radians(ph)), cos(radians(ph))])

    def line(p0, p1, lw=MAIN, ls="-", z=5, cap="round"):
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=K_, lw=lw, ls=ls, zorder=z, solid_capstyle=cap)

    def hatch(p0, p1, side, n=9, h=0.2, lw_base=1.6):
        """неподвижное звено: линия p0–p1 и штрихи «/» под 45° со стороны side"""
        p0, p1 = np.array(p0, float), np.array(p1, float)
        line(p0, p1, lw=lw_base, z=6, cap="butt")
        d = np.array([1.0, 1.0]) * h * (1 if np.dot(side, [1, 1]) > 0 else -1)
        for t in np.linspace(0.06, 1, n):
            a = p0 + t * (p1 - p0)
            line(a, a + d, lw=0.9, z=6, cap="butt")

    def joint(c, letter="", r=RJ_, lw=1.5, ls="-", z=9, fs=12):
        ax.add_patch(Circle(c, r, fc="white", ec=K_, lw=lw, ls=ls, zorder=z))
        if letter:
            ax.text(c[0], c[1] - 0.01, letter, fontsize=fs, ha="center", va="center", zorder=z + 1, weight="bold")

    def leader(p, txt, to, ha="left"):
        """выноска как на образце: S-образная тонкая линия от звена к подписи"""
        p, to = np.array(p, float), np.array(to, float)
        m = (p + to) / 2
        verts = [p, (p[0], m[1]), (to[0], m[1]), to]
        ax.add_patch(PathPatch(Path(verts, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc="none", ec=K_,
                               lw=0.9, zorder=3))
        ax.text(to[0] + (0.08 if ha == "left" else -0.08), to[1], txt, fontsize=13.5, ha=ha, va="center", weight="bold")

    def arrow(p0, p1, lw=1.8, ms=15):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=K_, lw=lw, mutation_scale=ms,
                                                          shrinkA=0, shrinkB=0), zorder=8)

    def stone(ph, main):
        lw, ls = (1.6, "-") if main else (THIN, PHANTOM)
        D = np.array([E_S, yD(ph)])
        r = Rectangle((-STONE[0] / 2, -STONE[1] / 2), *STONE, fc="white", ec=K_, lw=lw, ls=ls, zorder=7 if main else 4)
        r.set_transform(Affine2D().rotate_deg(ph).translate(*D) + ax.transData); ax.add_patch(r)
        # шарнир D (2–3): звено 3 огибает палец дугой снизу и уходит вниз
        ax.add_patch(Arc(D, 2 * (RJ_ + 0.08), 2 * (RJ_ + 0.08), theta1=200, theta2=340, color=K_, lw=lw, ls=ls,
                         zorder=8 if main else 5))
        joint(D, "D" if main else "", lw=lw, ls=ls, z=9 if main else 5)

    O = np.zeros(2)
    # оси
    arrow((-0.9, 0), (9.0, 0), lw=0.9, ms=11); ax.text(9.0, -0.3, "x", fontsize=15, ha="center", va="top", style="italic")
    arrow((0, -0.2), (0, 8.0), lw=0.9, ms=11); ax.text(-0.25, 7.95, "y", fontsize=15, ha="right", va="center", style="italic")
    # стойка 0: шарнир O на треугольной опоре со штриховкой
    tri = Polygon([(0, -RJ_), (-0.5, -1.05), (0.5, -1.05)], closed=True, fc="white", ec=K_, lw=1.5, zorder=7)
    ax.add_patch(tri)
    hatch((-0.85, -1.05), (0.85, -1.05), (-1, -1), n=9)
    ax.text(0, -0.72, "0", fontsize=13, ha="center", va="center", zorder=8, weight="bold")
    # кулиса: крайние положения (тонкие штрихпунктирные) и рабочее
    for ph, k in ((PH_N, "н"), (PH_K, "к")):
        line(O, PH_LEN[k] * L_S * u(ph), lw=THIN, ls=PHANTOM, z=2)
        stone(ph, False)
    Kp = L_S * u(PH)
    line(O + RJ_ * u(PH), Kp)
    joint(O, "O")
    D = np.array([E_S, yD(PH)])
    stone(PH, True)
    # ползун 3: шток от шарнира D вниз, головка внизу; ход — тонкими линиями
    yh = D[1] - HK
    line(D - np.array([0, RJ_ + 0.08]), (E_S, yh), cap="butt")
    line((E_S - 0.45, yh), (E_S + 0.45, yh), lw=3.2, cap="butt")                  # головка
    # направляющая 0: две линии вдоль штока, штриховка снаружи
    g0, g1 = -1.75, -0.35
    hatch((E_S - 0.3, g0), (E_S - 0.3, g1), (-1, -1), n=6)
    hatch((E_S + 0.3, g0), (E_S + 0.3, g1), (1, 1), n=6)
    # силы
    arrow(Kp + np.array([0, 1.55]), Kp + np.array([0, 0.05]), lw=2.0)
    ax.text(Kp[0] + 0.18, Kp[1] + 1.2, "P", fontsize=18, ha="left", va="center", style="italic")
    arrow((E_S, yh - 1.0), (E_S, yh - 0.06), lw=2.0)
    ax.text(E_S + 0.2, yh - 0.62, r"$F_{\mathrm{ук}}$", fontsize=18, ha="left", va="center")
    # обозначения точек и звеньев
    ax.text(Kp[0] + 0.15, Kp[1] - 0.12, "K", fontsize=16, ha="left", va="top", weight="bold")
    ax.text(*(0.88 * Kp - 0.34 * nrm(PH)), "1", fontsize=16, ha="center", va="center", weight="bold")
    ax.text(*(D + 0.62 * nrm(PH) - 0.42 * u(PH)), "2", fontsize=16, ha="center", va="center", weight="bold")
    ax.text(E_S - 0.32, (D[1] + g1) / 2 - 0.1, "3", fontsize=16, ha="right", va="center", weight="bold")
    # φ, φн, φк
    ax.add_patch(Arc(O, 2.4, 2.4, theta1=0, theta2=PH, color=K_, lw=0.9, zorder=4))
    ax.text(1.45 * cos(radians(PH / 2)), 1.45 * sin(radians(PH / 2)), r"$\varphi$", fontsize=18, ha="center", va="center")
    for ph, k, lab, val in ((PH_N, "н", r"$\varphi_{\mathrm{н}}$", f"{PH_N:.1f}°"), (PH_K, "к", r"$\varphi_{\mathrm{к}}$", f"{PH_K:.1f}°")):
        t = lab + (f" = {val}".replace(".", ",") if values else "")
        side = 1 if ph > 45 else -1
        ax.text(*((PH_LEN[k] - (0.17 if values else 0.06)) * L_S * u(ph) + 0.36 * side * nrm(ph)), t, fontsize=15, ha="center", va="center",
                rotation=ph, rotation_mode="anchor")
    ax.text(*(0.74 * Kp + 0.34 * nrm(PH)), "L = OK = 500 мм" if values else "L = OK", fontsize=15, rotation=PH,
            ha="center", va="center", rotation_mode="anchor")
    # выноски с названиями звеньев
    LX = 6.3
    leader(0.93 * Kp, "Кулиса с рукоятью", (LX, 4.3))
    leader(D + 0.45 * u(PH) - 0.28 * nrm(PH), "Камень", (LX, 2.75))
    leader((E_S + 0.45, yh), "Ползун с головкой", (LX, yh - 0.35))
    leader((E_S + 0.3, g0 + 0.35), "Направляющая", (LX, g0 + 0.2))
    leader((-0.45, -1.2), "Стойка", (-1.6, -2.1), ha="right")
    if values:                                    # размеры — только после расчётов
        Bn, Bk = np.array([E_S, yD(PH_N)]), np.array([E_S, yD(PH_K)])
        xs = -1.0
        for p in (Bn, Bk):
            line((xs - 0.15, p[1]), (p[0] - 0.55, p[1]), lw=0.6, z=2)
        ax.annotate("", xy=(xs, Bk[1]), xytext=(xs, Bn[1]), arrowprops=dict(arrowstyle="<|-|>", color=K_, lw=0.8,
                                                                           mutation_scale=10, shrinkA=0, shrinkB=0))
        ax.text(xs - 0.12, (Bn[1] + Bk[1]) / 2, "S = 16 мм", fontsize=15, ha="center", va="bottom", rotation=90)
        ybot = yh - 1.55
        line((E_S, g0 - 0.05), (E_S, ybot - 0.15), lw=0.6, z=2)
        line((0, -1.15), (0, ybot - 0.15), lw=0.6, z=2)
        ax.annotate("", xy=(E_S, ybot), xytext=(0, ybot), arrowprops=dict(arrowstyle="<|-|>", color=K_, lw=0.8,
                                                                         mutation_scale=10, shrinkA=0, shrinkB=0))
        ax.text(E_S / 2, ybot + 0.1, "e = 12,5 мм", fontsize=15, ha="center", va="bottom")
    ax.set_xlim(-2.6 if values else -2.2, 9.4); ax.set_ylim(yh - (2.0 if values else 1.2), 8.3)
    trim_save(fig, name)


def vector_contour():
    """кинематический анализ (замечание преподавателя 23.11): векторный контур O–B–D — треугольник,
    уравнение замкнутости l = e + y_D, проекции, выражение стороны y_D и дифференцирование"""
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.set_aspect("equal"); ax.axis("off")
    ph = 50.0
    e = 3.0
    O, B, D = np.zeros(2), np.array([e, 0.0]), np.array([e, e * tan(radians(ph))])

    def vec(p0, p1, lw=2.4):
        d = (p1 - p0) / np.linalg.norm(p1 - p0)
        p0, p1 = p0 + 0.06 * d, p1 - 0.06 * d                      # от точки до точки
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=K_, lw=lw, mutation_scale=22,
                                                          shrinkA=0, shrinkB=0), zorder=8)
    ax.annotate("", xy=(5.4, 0), xytext=(-0.6, 0), arrowprops=dict(arrowstyle="-|>", color=K_, lw=0.9, mutation_scale=11))
    ax.annotate("", xy=(0, 4.6), xytext=(0, -0.6), arrowprops=dict(arrowstyle="-|>", color=K_, lw=0.9, mutation_scale=11))
    ax.text(5.4, -0.25, "x", fontsize=15, style="italic", ha="center", va="top")
    ax.text(-0.22, 4.55, "y", fontsize=15, style="italic", ha="right", va="center")
    # кулиса (продолжение) тонко
    ax.plot([0, 1.35 * D[0]], [0, 1.35 * D[1]], color=K_, lw=0.8, ls=PHANTOM, zorder=2)
    vec(O, B); vec(B, D); vec(O, D)
    ax.plot([B[0] - 0.28, B[0] - 0.28, B[0]], [0, 0.28, 0.28], color=K_, lw=0.8)          # прямой угол
    ax.add_patch(Arc(O, 1.6, 1.6, theta1=0, theta2=ph, color=K_, lw=1.0))
    ax.text(1.0 * cos(radians(ph / 2)), 1.0 * sin(radians(ph / 2)), r"$\varphi$", fontsize=18, ha="center", va="center")
    ax.text(e / 2, -0.3, r"$\vec{e}$", fontsize=20, ha="center", va="top")
    ax.text(B[0] + 0.2, D[1] / 2, r"$\vec{y}_D$", fontsize=20, ha="left", va="center")
    m = D / 2 + 0.38 * np.array([-sin(radians(ph)), cos(radians(ph))])
    ax.text(*m, r"$\vec{l}_{OD}$", fontsize=20, ha="center", va="center")   # как в РПЗ (Корнеев 00:14)
    for p, t, off in ((O, "O", (-0.32, 0.22)), (B, "B", (0.25, -0.3)), (D, "D", (0.28, 0.1))):
        ax.add_patch(Circle(p, 0.075, fc=K_, ec=K_, lw=1.0, zorder=9))   # обычные маленькие чёрные точки (Корнеев 23:24)
        ax.text(p[0] + off[0], p[1] + off[1], t, fontsize=16, ha="center", va="center", weight="bold")
    ax.set_xlim(-0.9, 5.6); ax.set_ylim(-0.9, 4.9)
    trim_save(fig, "вектор_контур.png")


def contour_formulas():
    plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
    # 24.11 Корнеев: стрелки векторов — длинные, как в РПЗ; добавлена точка K (конец рукояти, как в РПЗ п. 3.3)
    lines = [r"$\overrightarrow{l_{OD}} = \vec{e} + \overrightarrow{y_D}$",
             r"$x:\ \ l_{OD}\,\cos\varphi = e, \qquad y:\ \ l_{OD}\,\sin\varphi = y_D$",
             r"$y_D = e\,\mathrm{tg}\,\varphi$",
             r"$v_D = \dfrac{d y_D}{d t} = \dfrac{e\,\omega}{\cos^2\varphi}$",
             r"$a_D = \dfrac{d v_D}{d t} = \dfrac{e\,(\varepsilon + 2\,\omega^2\,\mathrm{tg}\,\varphi)}{\cos^2\varphi}$",
             r"$K:\ \ x_K = L\,\cos\varphi, \qquad y_K = L\,\sin\varphi$",
             r"$v_K = \omega\,L, \qquad a_K^{\tau} = \varepsilon\,L, \qquad a_K^{n} = \omega^2 L$"]
    h = [0.7, 0.62, 0.62, 0.95, 0.95, 0.62, 0.62]
    fig = plt.figure(figsize=(7.0, sum(h)))
    y = 1.0
    for s, hh in zip(lines, h):
        y -= hh / sum(h) / 2
        fig.text(0.0, y, s, fontsize=19, color="#1E1E1E", ha="left", va="center")
        y -= hh / sum(h) / 2
    trim_save(fig, "ф_контур.png", pad=10)
    plt.rcParams.update({"mathtext.fontset": "custom", "font.family": "Arial"})


if __name__ == "__main__":                    # векторный контур и его формулы (схемы — make_schemes_v3.py)
    vector_contour()
    contour_formulas()
    json.dump(SIZES, open(os.path.join(FIG, "sizes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
