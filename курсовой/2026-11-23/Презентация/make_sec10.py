# -*- coding: utf-8 -*-
"""Слайд 10 (Корнеев 24.11 02:27): все формулы прочностного расчёта звеньев (РПЗ пп. 8.5–8.6) — слева;
итоги проверок формулами (РПЗ табл. 12, 13; значения до десятых) — справа снизу.
fig/ф_сечения10.png, fig/ф_итоги10.png        python make_sec10.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
INK, HEAD = "#1E1E1E", "#1F3864"


def block(name, items, width, fs, hl, hf, hf_d):
    hs = [hl if k == "h" else (hf_d if "dfrac" in t else hf) for k, t in items]
    H = sum(hs)
    fig = plt.figure(figsize=(width, H))
    y = 0.0
    for (k, t), h in zip(items, hs):
        yc = 1 - (y + h / 2) / H
        if k == "h":
            fig.text(0.0, yc, t, fontsize=fs - 3, weight="bold", color=HEAD, ha="left", va="center", family="Arial")
        else:
            fig.text(0.02, yc, t, fontsize=fs, color=INK, ha="left", va="center")
        y += h
    path = os.path.join(FIG, name)
    fig.savefig(path, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    im = Image.open(path).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
    im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), min(bb[2] + 10, im.width), min(bb[3] + 10, im.height))).save(path)
    print(name, Image.open(path).size)


block("ф_сечения10.png", [
    ("h", "Шток — сжатие и устойчивость (μ = 2, l = 60 мм)"),
    ("f", r"$\sigma = \dfrac{F_{\mathrm{ук}}}{A} \leq [\sigma] = \dfrac{\sigma_{\mathrm{т}}}{n};\qquad \lambda = \dfrac{\mu\,l}{i},\quad i = \sqrt{\dfrac{I_{\min}}{A}} = \dfrac{d}{4}$"),
    ("f", r"$\lambda < 100:\quad \sigma_{\mathrm{кр}} = a - b\,\lambda \leq \sigma_{\mathrm{т}},\quad F_{\mathrm{кр}} = \sigma_{\mathrm{кр}}\,A$"),
    ("f", r"$\lambda \geq 100:\quad F_{\mathrm{кр}} = \dfrac{\pi^2 E\,I_{\min}}{(\mu\,l)^2};\qquad n_{\mathrm{у}} = \dfrac{F_{\mathrm{кр}}}{F_{\mathrm{ук}}} \geq 3$"),
    ("h", "Ось O, палец D — срез (одна плоскость); отверстия — смятие"),
    ("f", r"$\tau_{\mathrm{ср}} = \dfrac{4\,R}{\pi\,d^2} \leq [\tau_{\mathrm{ср}}],\qquad \sigma_{\mathrm{см}} = \dfrac{R}{d\,l} \leq [\sigma_{\mathrm{см}}]$"),
    ("h", "Перемычки у отверстий — срез"),
    ("f", r"$\tau = \dfrac{R}{2\,c\,s} \leq [\tau]$"),
], 7.2, 19, 0.5, 0.6, 0.95)

block("ф_итоги10.png", [
    ("h", "Шток Ø8, Ст3сп"),
    ("f", r"$\sigma = 39{,}3 \leq 98\ \mathrm{МПа};\quad \lambda = 60,\ \ F_{\mathrm{кр}} = 12\,144\ \mathrm{Н},\ \ n_{\mathrm{у}} = \dfrac{12\,144}{1974} = 6{,}2 \geq 3$"),
    ("h", "Пара O: ось Ø10, сталь 45 (R = 2432 Н)"),
    ("f", r"$\tau_{\mathrm{ср}} = 31{,}0 \leq 50;\quad \sigma_{\mathrm{см}} = 12{,}2 \leq 24;\quad \tau = 38{,}0 \leq 49\ \mathrm{МПа}$"),
    ("h", "Пара D: палец Ø10, сталь 40Х (R = 2515 Н)"),
    ("f", r"$\tau_{\mathrm{ср}} = 32{,}0 \leq 50;\quad \sigma_{\mathrm{см}} = 15{,}7 \leq 24;\quad \tau = 11{,}2 \leq 49\ \mathrm{МПа}$"),
], 8.6, 19, 0.46, 0.52, 0.9)

# вариант Б (Корнеев 24.11 12:12): реакция R30 = 1671 Н на полке, h = 57,9 мм ниже D (φу) → M = 96,7 Н·м, W = πd³/32 = 50,3 мм³
block("ф_итоги10_Б.png", [
    ("h", "Шток Ø8, Ст3сп"),
    ("f", r"$\sigma = 39{,}3 \leq 98\ \mathrm{МПа};\quad \lambda = 60,\ \ F_{\mathrm{кр}} = 12\,144\ \mathrm{Н},\ \ n_{\mathrm{у}} = \dfrac{12\,144}{1974} = 6{,}2 \geq 3$"),
    ("f", r"$\mathrm{Вариант\ Б,\ изгиб:}\ \sigma = \dfrac{R_{30}\,h}{W} = 1924 > 98\ \mathrm{МПа}\ -\ \mathrm{не\ выполняется}$"),
    ("h", "Пара O: ось Ø10, сталь 45 (R = 2432 Н)"),
    ("f", r"$\tau_{\mathrm{ср}} = 31{,}0 \leq 50;\quad \sigma_{\mathrm{см}} = 12{,}2 \leq 24;\quad \tau = 38{,}0 \leq 49\ \mathrm{МПа}$"),
    ("h", "Пара D: палец Ø10, сталь 40Х (R = 2515 Н)"),
    ("f", r"$\tau_{\mathrm{ср}} = 32{,}0 \leq 50;\quad \sigma_{\mathrm{см}} = 15{,}7 \leq 24;\quad \tau = 11{,}2 \leq 49\ \mathrm{МПа}$"),
], 8.6, 19, 0.46, 0.52, 0.9)
