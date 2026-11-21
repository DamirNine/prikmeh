# -*- coding: utf-8 -*-
"""21.11 (замечание Корнеева А.Е.: «идёт наслоение обозначений»): рис. 13 (продолжение), выносной элемент А — метки сечений
В–В (через ось пальца D) и Б–Б (рядом с пальцем) стояли друг на друге. Метки стираются и рисуются заново по ЕСКД: толстый
штрих следа плоскости, стрелка взгляда к оси O, буква над стрелкой; В и Б — на одной высоте и разнесены по x, буквы не
пересекаются. Линия-выноска размера 16,76 (x = 260) под нижними метками восстанавливается.
    python fix_fig13.py  → рисунки/рис13_продолжение.png"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, "рисунки", "рис13_продолжение_исходный.png")).convert("RGB")
d = ImageDraw.Draw(im)
W, INK = (255, 255, 255), (20, 20, 20)
d.rectangle((195, 219, 314, 259), fill=W)                  # верхние метки (край камня — ниже, y ≈ 263)
d.rectangle((195, 457, 314, 496), fill=W)                  # нижние метки (край камня — выше, y ≈ 453)
d.line((260, 456, 260, 497), fill=INK, width=1)            # выноска размера 16,76
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)


def mark(x, y_stroke, up, label, arrow_len=26):
    """штрих y_stroke (y0, y1), стрелка влево от штриха, буква над (up) или под стрелкой"""
    y0, y1 = y_stroke
    d.line((x, y0, x, y1), fill=INK, width=3)
    ya = y0 + 3 if up else y1 - 3
    d.line((x - 2, ya, x - arrow_len + 6, ya), fill=INK, width=2)
    d.polygon([(x - arrow_len, ya), (x - arrow_len + 9, ya - 4), (x - arrow_len + 9, ya + 4)], fill=INK)
    tx = x - arrow_len / 2 - 2
    bb = d.textbbox((0, 0), label, font=font)
    d.text((tx - (bb[2] - bb[0]) / 2, ya - 22 if up else ya + 4), label, fill=INK, font=font)


for x, lab in ((260, "В"), (300, "Б")):
    mark(x, (236, 256), True, lab)
    mark(x, (458, 478), False, lab)
im.save(os.path.join(HERE, "рисунки", "рис13_продолжение.png"))
im.crop((150, 180, 380, 530)).save(os.path.join(HERE, "рисунки", "_проверка_меток.png"))
print("ok")
