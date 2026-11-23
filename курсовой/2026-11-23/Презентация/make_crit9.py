# -*- coding: utf-8 -*-
"""Слайд 9 (Корнеев 24.11 02:09: постановка задачи убрана, остаются эпюры и критерии) — две формулы критериев сечения
кулисы отдельными картинками (подписи — текстом на слайде): fig/ф_крит_изгиб.png, fig/ф_крит_срез.png
    python make_crit9.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
for name, tex in (("ф_крит_изгиб.png", r"$\sigma = \dfrac{|N|}{A} + \dfrac{|M_D|}{W} \leq [\sigma] = \dfrac{\sigma_{\mathrm{т}}}{n}$"),
                  ("ф_крит_срез.png", r"$\tau_{\max} = \dfrac{1{,}5\,|Q|}{b\,h} \leq [\tau]$")):
    fig = plt.figure(figsize=(6.0, 1.2))
    fig.text(0.0, 0.5, tex, fontsize=21, color="#1E1E1E", ha="left", va="center")
    path = os.path.join(FIG, name)
    fig.savefig(path, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    im = Image.open(path).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
    im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), min(bb[2] + 10, im.width), min(bb[3] + 10, im.height))).save(path)
    print(name, Image.open(path).size)
