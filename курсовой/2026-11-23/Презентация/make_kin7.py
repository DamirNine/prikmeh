# -*- coding: utf-8 -*-
"""Слайд 7 «графики движения» (Корнеев 24.11 01:29): закон движения кулисы — формула из трёх слагаемых, угловая скорость
и угловое ускорение, и по каким формулам построены графики ползуна (координата, скорость, ускорение). Значения — до
десятых. ω, ε — модуль угловой скорости кулисы и его производная (как на графиках); φ убывает от φн до φк.
Формулы ползуна совпадают с производными слайда 6 при ω = −|dφ/dt|. → fig/ф_кинематика7.png
    python make_kin7.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})

LINES = [(r"$\psi = \dfrac{1}{2}\,\omega_{\max} t_{\mathrm{р}} + \omega_{\max} t_{\mathrm{у}}"
          r" + \dfrac{1}{2}\,\omega_{\max} t_{\mathrm{т}}$", 0.9),
         (r"$\omega_{\max} = \dfrac{v_{\max}}{L} = \dfrac{0{,}7}{0{,}5} = 1{,}4\ \mathrm{рад/с}$", 1.0),
         (r"$\varepsilon_{\mathrm{р}} = \dfrac{\omega_{\max}}{t_{\mathrm{р}}} = 3{,}2\ \mathrm{рад/с^2},\qquad"
          r"\varepsilon_{\mathrm{т}} = -\dfrac{\omega_{\max}}{t_{\mathrm{т}}} = -3{,}0\ \mathrm{рад/с^2}$", 1.0),
         (r"$\varphi(t) = \varphi_{\mathrm{н}} - \int_0^{\,t} \omega\,dt$", 0.95),
         (r"$y_D = e\,\mathrm{tg}\,\varphi,\qquad v_D = -\dfrac{e\,\omega}{\cos^2\varphi}$", 1.0),
         (r"$a_D = \dfrac{2\,e\,\omega^2 \sin\varphi}{\cos^3\varphi} - \dfrac{e\,\varepsilon}{\cos^2\varphi}$", 1.0)]

H = sum(h for _, h in LINES)
fig = plt.figure(figsize=(7.4, H * 0.8))
y = 1.0
for s, h in LINES:
    y -= h / H / 2
    fig.text(0.0, y, s, fontsize=19, color="#1E1E1E", ha="left", va="center")
    y -= h / H / 2
path = os.path.join(FIG, "ф_кинематика7.png")
fig.savefig(path, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
plt.close(fig)
im = Image.open(path).convert("RGB")
bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), min(bb[2] + 10, im.width), min(bb[3] + 10, im.height))).save(path)
print("ф_кинематика7.png", Image.open(path).size)
