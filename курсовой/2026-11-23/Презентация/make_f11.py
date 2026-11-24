# -*- coding: utf-8 -*-
"""Слайд 11 (Корнеев 24.11 12:22): основные формулы уточнённого силового расчёта (РПЗ разд. 9, 9.2, 9.3) — полосой над результатом.
fig/ф_уточн11.png      python make_f11.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
fig = plt.figure(figsize=(11.0, 1.1))
for y, t in ((0.75, r"$G_1 = m_1 g,\quad G_3 = m_3 g;\qquad \Phi_{1\tau} = m_1\,\varepsilon\,z_S,\quad \Phi_{1n} = m_1\,\omega^2 z_S,\quad M_{\Phi 1} = J_S\,\varepsilon$"),
             (0.25, r"$\Phi_3 = -m_3\,a_{Dy},\qquad F_{\mathrm{пр}} = F_{\mathrm{ук}} - G_3 + \Phi_3;\qquad \sum F_x = 0,\quad \sum F_y = 0,\quad \sum M_M = 0$")):
    fig.text(0, y, t, fontsize=20, color="#1E1E1E", ha="left", va="center")
p = os.path.join(FIG, "ф_уточн11.png")
fig.savefig(p, facecolor="white", dpi=240, bbox_inches="tight", pad_inches=0.06)
im = Image.open(p).convert("RGB")
bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), bb[2] + 10, bb[3] + 10)).save(p)
print(Image.open(p).size)
