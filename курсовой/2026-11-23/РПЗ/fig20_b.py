# -*- coding: utf-8 -*-
"""РПЗ вариант Б, рис. 20 «Крайние положения» — из сборки без планок (2026-11-21/инструкция/img_B). → _media/image21_Б.png"""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "..", "2026-11-21", "инструкция", "img_B")
F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
def trim(im):
    im = im.convert("RGB"); bb = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox(); p = 12
    return im.crop((max(bb[0]-p, 0), max(bb[1]-p, 0), min(bb[2]+p, im.width), min(bb[3]+p, im.height)))
c = Image.new("RGB", (1800, 1060), "white"); d = ImageDraw.Draw(c)
for i, (f, t) in enumerate((("02_рукоять_вверху", "рукоять вверху (φн = 59,47°)"), ("03_рукоять_внизу", "рукоять внизу (φк = 22,72°)"))):
    im = trim(Image.open(os.path.join(IMG, f + ".png"))); im.thumbnail((870, 980))
    c.paste(im, (i*900 + (900-im.width)//2, (1000-im.height)//2)); d.text((i*900 + (900-d.textlength(t, font=F))/2, 1008), t, fill="black", font=F)
c.save(os.path.join(HERE, "_media", "image21_Б.png")); print(c.size)
