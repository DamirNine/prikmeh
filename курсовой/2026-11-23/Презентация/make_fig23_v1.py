# -*- coding: utf-8 -*-
"""Рисунки 23.11 по комментариям Корнеева к презентации:
  звено1/2/3_v23.png       — расчётные схемы звеньев из fbd/fig7_fbd_v24.png (точки — белые кружки);
  схемы_уточняющий_v23.png — fbd/fig13_fbd_v24.png целиком (обрезка полей);
  сечения_v23.png          — принятые сечения: размеры с выносными линиями (ГОСТ 2.307-2011), не «в воздухе»;
  ф_кулиса_сечение.png     — критерии для опасного сечения кулисы (изгиб со сжатием, срез по Журавскому);
  ф_проверки.png           — формулы: устойчивость штока (Эйлер / Ясинский), срез оси и пальца, смятие отверстий;
  ф_обжим_v23.png          — усилие укупоривания для слайда с крышкой.
    python make_fig23.py"""
import os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
FBD = os.path.join(HERE, "..", "fbd")
INK, INK2, RED = "#17212E", "#566579", "#B8432F"


def trim(im, pad=14):
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)))


def trim_save(fig, name, pad=12):
    path = os.path.join(FIG, name)
    fig.savefig(path, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    im = trim(Image.open(path).convert("RGB"), pad)
    im.save(path)
    print(f"  {name}: {im.size}")


def links():
    """звенья 1, 2, 3 из fig7_fbd_v23: звено 1 слева, звенья 2 и 3 — справа друг над другом (как links() в make_figs.py)"""
    im = Image.open(os.path.join(FBD, "fig7_fbd_v24.png")).convert("RGB")
    W, H = im.size
    g = np.asarray(im.convert("L")) < 235
    cols = g.any(axis=0)
    xs = [x for x in range(int(0.5 * W), int(0.8 * W)) if not cols[x]]
    xc = max(xs, key=lambda x: sum(1 for k in range(x, min(x + 200, W)) if not cols[k]))
    rows = g[:, xc:].any(axis=1)
    runs, start = [], None
    for y in range(int(0.25 * H), int(0.7 * H)):
        if not rows[y] and start is None:
            start = y
        if rows[y] and start is not None:
            runs.append((start, y)); start = None
    a, b = runs[-1]                      # последний просвет: под подписью «Звено 2 — камень», над звеном 3
    yc = (a + b) // 2
    print(f"  граница звеньев: x = {xc / W:.3f}, y = {yc / H:.3f}")
    for name, box in (("звено1_v23.png", (0, 0, xc, H)), ("звено2_v23.png", (xc, 0, W, yc)), ("звено3_v23.png", (xc, yc, W, H))):
        c = trim(im.crop(box), 12)
        c.save(os.path.join(FIG, name)); print(f"  {name}: {c.size}")
    r = trim(Image.open(os.path.join(FBD, "fig13_fbd_v24.png")).convert("RGB"))
    r.save(os.path.join(FIG, "схемы_уточняющий_v23.png")); print(f"  схемы_уточняющий_v23.png: {r.size}")


def sections():
    """сечения: выносные линии от контура (сплошные тонкие, с вылетом 1…5 мм за размерную), размерные — со стрелками,
    числа над размерной линией (ГОСТ 2.307-2011); оси круглых сечений — штрихпунктир"""
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    ax.set_aspect("equal"); ax.axis("off")
    plt.rcParams["hatch.linewidth"] = 1.0
    TH = 0.7

    def dim_h(x0, x1, y_obj, y_dim, txt):
        for x in (x0, x1):                                           # выносные линии
            ax.plot([x, x], [y_obj - 0.4, y_dim - 1.0], color=INK, lw=TH)
        ax.annotate("", xy=(x1, y_dim), xytext=(x0, y_dim), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=TH,
                                                                           mutation_scale=9, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, y_dim + 0.35, txt, ha="center", va="bottom", fontsize=14, color=INK)

    def dim_v(y0, y1, x_obj, x_dim, txt):
        for y in (y0, y1):
            ax.plot([x_obj + 0.4, x_dim + 1.0], [y, y], color=INK, lw=TH)
        ax.annotate("", xy=(x_dim, y1), xytext=(x_dim, y0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=TH,
                                                                           mutation_scale=9, shrinkA=0, shrinkB=0))
        ax.text(x_dim - 0.35, (y0 + y1) / 2, txt, ha="right", va="center", fontsize=14, color=INK, rotation=90)

    def axes(cx, cy, r):
        ax.plot([cx - r - 2, cx + r + 2], [cy, cy], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)))
        ax.plot([cx, cx], [cy - r - 2, cy + r + 2], color=INK2, lw=0.6, ls=(0, (8, 2, 1, 2)))

    # кулиса 8 × 18 (сечение D)
    ax.add_patch(Rectangle((0, 0), 8, 18, fc="white", ec=INK, lw=1.8, hatch="///"))
    dim_h(0, 8, 0, -4.0, "8")
    dim_v(0, 18, 8, 12.0, "18")
    ax.text(5, 25.0, "Кулиса — сечение D", ha="center", fontsize=15, weight="bold", color=INK)
    ax.text(5, 22.3, "полоса 8 · 18, Ст3сп", ha="center", fontsize=13, color=INK2)
    # шток Ø8
    cx, cy, r = 33, 9, 4
    ax.add_patch(Circle((cx, cy), r, fc="white", ec=INK, lw=1.8, hatch="///")); axes(cx, cy, r)
    dim_h(cx - r, cx + r, cy - r, cy - r - 4.0, "Ø8")
    for x in (cx - r, cx + r):
        ax.plot([x, x], [cy, cy - r - 0.4], color=INK, lw=TH)
    ax.text(cx, 25.0, "Шток ползуна", ha="center", fontsize=15, weight="bold", color=INK)
    ax.text(cx, 22.3, "круг Ø8, Ст3сп", ha="center", fontsize=13, color=INK2)
    # ось O и палец D Ø10
    cx, cy, r = 59, 9, 5
    ax.add_patch(Circle((cx, cy), r, fc="white", ec=INK, lw=1.8, hatch="///")); axes(cx, cy, r)
    dim_h(cx - r, cx + r, cy - r, cy - r - 3.0, "Ø10")
    for x in (cx - r, cx + r):
        ax.plot([x, x], [cy, cy - r - 0.4], color=INK, lw=TH)
    ax.text(cx, 25.0, "Ось O, палец D", ha="center", fontsize=15, weight="bold", color=INK)
    ax.text(cx, 22.3, "Ø10, сталь 45 / 40Х", ha="center", fontsize=13, color=INK2)
    ax.set_xlim(-3, 70); ax.set_ylim(-7, 27)
    trim_save(fig, "сечения_v23.png")


def formula_block(name, items, width=7.2):
    """items: [(подпись или None, формула или None)] — подписи Arial жирным, формулы STIX"""
    plt.rcParams.update({"mathtext.fontset": "stix"})
    hs = []
    for lab, f in items:
        hs.append((0.42 if lab else 0) + ((0.95 if f and "dfrac" in f else 0.6) if f else 0))
    fig = plt.figure(figsize=(width, sum(hs)))
    y = 1.0
    for (lab, f), h in zip(items, hs):
        if lab:
            fig.text(0.0, y - 0.21 / sum(hs), lab, fontsize=15, weight="bold", color=INK, ha="left", va="center",
                     family="Arial")
            y -= 0.42 / sum(hs)
        if f:
            hh = (0.95 if "dfrac" in f else 0.6) / sum(hs)
            fig.text(0.02, y - hh / 2, f, fontsize=19, color="#1E1E1E", ha="left", va="center", family="STIXGeneral")
            y -= hh
    trim_save(fig, name, pad=10)


def formulas():
    formula_block("ф_кулиса_сечение.png", [
        ("Изгиб со сжатием (нормальные напряжения):", r"$\sigma = \dfrac{|N|}{A} + \dfrac{|M_D|}{W} \leq [\sigma] = \dfrac{\sigma_{\mathrm{т}}}{n}$"),
        ("Срез на участке O–D (Журавский):", r"$\tau_{\max} = \dfrac{1{,}5\,|Q|}{b\,h} \leq [\tau]$"),
    ], width=5.2)
    formula_block("ф_проверки.png", [
        ("Изгиб со сжатием — кулиса, сечение D:", r"$\sigma = \dfrac{|N|}{A} + \dfrac{|M|}{W} \leq [\sigma] = \dfrac{\sigma_{\mathrm{т}}}{n},\quad n = 2{,}5$"),
        ("Устойчивость — шток (μ = 2, l = 60 мм):", r"$\lambda = \dfrac{\mu\,l}{i},\ \ i = \dfrac{d}{4};\qquad \lambda < 100:\ \ \sigma_{\mathrm{кр}} = a - b\,\lambda$"),
        (None, r"$\lambda \geq 100:\ \ F_{\mathrm{кр}} = \dfrac{\pi^2 E\,I_{\min}}{(\mu\,l)^2};\qquad n_{\mathrm{у}} = \dfrac{F_{\mathrm{кр}}}{F_{\mathrm{ук}}} \geq 3$"),
        ("Срез — ось O, палец D (одна плоскость):", r"$\tau_{\mathrm{ср}} = \dfrac{4\,R}{\pi\,d^2} \leq [\tau_{\mathrm{ср}}]$"),
        ("Смятие — отверстия:", r"$\sigma_{\mathrm{см}} = \dfrac{R}{d\,l} \leq [\sigma_{\mathrm{см}}]$"),
    ], width=6.4)
    formula_block("ф_обжим_v23.png", [
        (None, r"$F_{\mathrm{ук}} = n\,\sigma_{\mathrm{раб}}\,A\,\ln\dfrac{D_k}{D_{\mathrm{обж}}} = 1974\ \mathrm{Н}$"),
    ], width=5.0)


if __name__ == "__main__":
    links()
    sections()
    formulas()
