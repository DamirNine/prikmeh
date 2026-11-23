# -*- coding: utf-8 -*-
"""Слайд 3 (Корнеев 23.11 23:58: «напиши формулу нормально, а не просто текстом»): усилие укупоривания формулой.
    python make_f3.py → fig/ф_укупоривание.png"""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
fig = plt.figure(figsize=(6.2, 1.55))
fig.text(0.0, 0.72, r"$F_{\mathrm{ук}} = n\,\sigma_{\mathrm{раб}}\,A\,\ln\dfrac{D_k}{D_{\mathrm{обж}}}$", fontsize=21,
         color="#1E1E1E", ha="left", va="center")
fig.text(0.0, 0.18, r"$F_{\mathrm{ук}} = 2{,}0\cdot 435{,}75\cdot 19{,}61\cdot 0{,}1154 = 1974\ \mathrm{Н}$", fontsize=21,
         color="#1E1E1E", ha="left", va="center")
path = os.path.join(FIG, "ф_укупоривание.png")
fig.savefig(path, dpi=240, facecolor="white", bbox_inches="tight", pad_inches=0.05); plt.close(fig)
im = Image.open(path).convert("RGB")
bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).point(lambda v: 255 if v > 12 else 0).getbbox()
im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), bb[2] + 10, bb[3] + 10)).save(path); print(path)
