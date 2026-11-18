# -*- coding: utf-8 -*-
"""Сборные рисунки для РПЗ и презентации (папка fig/): детали КОМПАС, карты APM «до/после», шаги сборки прототипа, герб МГТУ
(из образца РПЗ). Источники — картинки инструкции 18.11 и отчёта APM 16.11.
    python make_figs.py"""
import os
import fitz
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fig"); os.makedirs(OUT, exist_ok=True)
KUR = os.path.join(HERE, "..", "..")
IMG = os.path.join(HERE, "..", "инструкция", "img")
APM1, APM2 = os.path.join(KUR, "2026-11-09", "apm"), os.path.join(KUR, "2026-11-16", "apm")
FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
FONT_B = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38)


def trim(im, gray_bg=False):
    """обрезка поля: белого (картинки КОМПАС) или серого фона APM — по цветным и тёмным пикселям"""
    im = im.convert("RGB")
    if gray_bg:
        px = im.load(); m = Image.new("L", im.size, 0); mp = m.load()
        for y in range(0, im.height, 2):
            for x in range(0, im.width, 2):
                r, g, b = px[x, y]
                if max(r, g, b) - min(r, g, b) > 30 or r + g + b < 420:
                    mp[x, y] = 255
        bb = m.getbbox()
    else:
        bb = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()
    pad = 12
    return im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)))


def grid(items, cols, cell, out, label_font=FONT):
    """items: [(картинка, подпись)] — сетка с подписями под ячейками"""
    w, h = cell
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * w, rows * (h + 60)), "white")
    d = ImageDraw.Draw(canvas)
    for i, (im, cap) in enumerate(items):
        im = im.copy(); im.thumbnail((w - 30, h - 20))
        x0, y0 = (i % cols) * w, (i // cols) * (h + 60)
        canvas.paste(im, (x0 + (w - im.width) // 2, y0 + (h - im.height) // 2))
        tw = d.textlength(cap, font=label_font)
        d.text((x0 + (w - tw) / 2, y0 + h + 8), cap, fill="black", font=label_font)
    canvas.save(os.path.join(OUT, out), optimize=True)
    print(" ", out, canvas.size)


# детали КОМПАС
parts = [("p_stand", "1 Стойка"), ("p_kulisa", "2 Кулиса"), ("p_kamen", "3 Камень"), ("p_pin", "4 Палец D"),
         ("p_guide", "5 Направляющая"), ("p_screw", "6 Винт М10"), ("p_polzun", "7 Ползун"), ("p_washer", "8 Шайба"),
         ("p_nut", "9 Гайка М10"), ("p_cover", "10 Кожух")]
grid([(trim(Image.open(os.path.join(IMG, f + ".png"))), c) for f, c in parts], 5, (520, 560), "детали.png")
for f in ("00_общий_вид", "01_без_кожуха", "02_рукоять_вверху", "03_рукоять_внизу"):
    trim(Image.open(os.path.join(IMG, f + ".png"))).save(os.path.join(OUT, f + ".png"), optimize=True)
grid([(trim(Image.open(os.path.join(IMG, "02_рукоять_вверху.png"))), "рукоять вверху (φн = 59,47°)"),
      (trim(Image.open(os.path.join(IMG, "03_рукоять_внизу.png"))), "рукоять внизу (φк = 22,72°)")], 2, (900, 1000), "ход.png")

# APM: до / после
APM = [("кулиса", os.path.join(APM1, "Скрины", "кулиса_2_тест.png"), os.path.join(APM1, "Скрины", "кулиса_4_тест_новой_2.png")),
       ("ползун", os.path.join(APM1, "Скрины", "ползун_2_тест.png"), os.path.join(APM1, "Скрины", "ползун_4_тест_нового.png")),
       ("камень", os.path.join(APM1, "Скрины", "камень_2_тест.png"), os.path.join(APM1, "Скрины", "камень_4_тест_итог.png")),
       ("направляющая", os.path.join(APM2, "Скрины", "направляющая_2_тест.png"), os.path.join(APM2, "Скрины", "направляющая_6_тест_с_винтом.png"))]
for name, a, b in APM:
    ia = Image.open(a); ia = ia.crop((0, 16, ia.width, ia.height))           # у первого скрина сверху — край панели APM
    grid([(trim(ia, True), "до доработки"), (trim(Image.open(b), True), "после доработки")], 2, (1000, 820),
         f"apm_{name}.png")
trim(Image.open(os.path.join(APM1, "Скрины", "палец_2_тест_подшипниковая.png")), True).save(os.path.join(OUT, "apm_палец.png"))

# прототип: шаги сборки
steps = [("13_кулиса_на_ось", "кулиса с камнем на оси O"), ("135_направляющая", "направляющая в выемке"),
         ("15_шайба_гайка", "ползун, шайба и гайка М10"), ("17_кожух_на_месте", "кожух на защёлках")]
grid([(trim(Image.open(os.path.join(IMG, f + ".png"))), c) for f, c in steps], 4, (620, 760), "сборка.png")

# герб МГТУ — самая крупная картинка первой страницы образца
doc = fitz.open(os.path.join(KUR, "примеры", "РПЗ.pdf"))
imgs = sorted(doc[0].get_images(full=True), key=lambda t: -t[2] * t[3])
pix = fitz.Pixmap(doc, imgs[0][0])
if pix.n > 4:
    pix = fitz.Pixmap(fitz.csRGB, pix)
pix.save(os.path.join(OUT, "герб.png"))
print("  герб.png", pix.width, pix.height)
