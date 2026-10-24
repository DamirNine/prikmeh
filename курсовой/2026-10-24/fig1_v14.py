# -*- coding: utf-8 -*-
"""Рис. 1 (v14): подписи L·cos φ, F_ук и φ_н отодвинуты от ползуна и штриховки направляющих.
Штриховка под прежними подписями восстановлена зеркально: направляющие симметричны относительно оси ползуна (x_лев + x_прав = 930 пикс.)."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans"})
a = np.asarray(Image.open(os.path.join(SP, "fig1_scheme_v13.png")).convert("RGB")).copy()
H, W = a.shape[:2]
AX = 930


def mirror(x0, x1, y0, y1):
    for x in range(x0, x1):
        a[y0:y1, x] = a[y0:y1, AX - x]


def white(x0, x1, y0, y1):
    a[y0:y1, x0:x1] = 255


mirror(412, 447, 1036, 1140)        # нижняя левая направляющая — из нижней правой
white(350, 412, 1066, 1134)         # прежняя F_ук
mirror(486, 516, 300, 413)          # верхняя правая направляющая — из верхней левой
white(486, 552, 413, 440); white(516, 552, 388, 413)   # прежняя φ_н
white(481, 603, 955, 993)           # прежняя L·cos φ

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(a, interpolation="none"); ax.axis("off")
ax.set_xlim(-0.5, W - 0.5); ax.set_ylim(H - 0.5, -0.5)
ax.text(700, 974, "L·cos φ", fontsize=22.5, color="black", ha="center", va="center")
ax.text(404, 1098, r"$F_{ук}$", fontsize=27, color=(195 / 255, 51 / 255, 39 / 255), ha="right", va="center")
ax.text(522, 412, r"$\varphi_{н}$", fontsize=24, color=(101 / 255, 101 / 255, 101 / 255), ha="left", va="center")
fig.savefig(os.path.join(SP, "fig1_scheme_v14.png"), dpi=100, facecolor="white"); plt.close(fig)
print("ok")
