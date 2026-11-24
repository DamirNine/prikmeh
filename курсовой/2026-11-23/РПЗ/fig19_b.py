# -*- coding: utf-8 -*-
"""РПЗ вариант Б, рис. 19 (Корнеев 24.11 12:39): в ячейке «5 Направляющая» — деталь без планок. → _media/image20_Б.png"""
import os, io
from docx import Document
import numpy as np
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
d = Document(os.path.join(HERE, "РПЗ_укупориватель_исходный.docx"))
part = next(p for p in d.part.package.iter_parts() if str(p.partname).endswith("/image20.png"))
im = Image.open(io.BytesIO(part.blob)).convert("RGB")
W, H = im.size
x0, x1, y1 = int(W * 0.80), W, int(H * 0.5)                     # ячейка 5: правая верхняя, подпись ниже детали
a = np.asarray(im.crop((x0, 0, x1, y1))).astype(int)
ink = (255 - a).max(axis=2) > 20
rows = np.nonzero(ink.any(axis=1))[0]
gaps = [(r, s) for r, s in zip(rows[:-1], rows[1:]) if s - r > 3]
top, bot = rows[0], gaps[-1][0]                                 # деталь — до пустой полосы над подписью
col = np.nonzero(ink[top:bot + 1].any(axis=0))[0]
g = Image.open(os.path.join(HERE, "..", "Презентация", "fig", "фэм_после_направляющая_Б.png")).convert("RGB")
bb = ImageChops.difference(g, Image.new("RGB", g.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
g = g.crop(bb)
bw, bh = (x1 - x0) - 20, bot - top
s = min(bw / g.width, bh / g.height); g = g.resize((int(g.width * s), int(g.height * s)), Image.LANCZOS)
im.paste((255, 255, 255), (x0 + col[0] - 4, top - 2, min(x0 + col[-1] + 5, W), bot + 3))
cx = x0 + (col[0] + col[-1]) // 2
px = min(max(cx - g.width // 2, x0), W - g.width)
im.paste(g, (px, top + (bh - g.height) // 2))
im.save(os.path.join(HERE, "_media", "image20_Б.png")); print(im.size, top, bot, px, g.size)
