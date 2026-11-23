# -*- coding: utf-8 -*-
"""РПЗ рис. 19–22 (media image22–25): пары «до/после доработки» из скринов APM без шкалы SVM (Корнеев 23.11 23:22),
под каждым — max и min σэкв со шкалы APM. Картинки — ../Презентация/fig/apm_*.png (crop_apm.py).
    python fem_pairs.py → _media/image22…25_мкэ.png (2000×880, как исходные)"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "Презентация", "fig")
PAIRS = {22: (("кулиса_2_тест", "92,62", "0,0039"), ("кулиса_4_тест_новой_2", "92,58", "0,0034")),
         23: (("ползун_2_тест", "95,88", "0,031"), ("ползун_4_тест_нового", "49,01", "0,031")),
         24: (("камень_2_тест", "646", "0,0028"), ("камень_4_тест_итог", "100,1", "0,0088")),
         25: (("направляющая_2_тест", "920", "0"), ("направляющая_Б_тест", "60,7", "0,0038"))}
W, H, CAP = 2000, 880, 130
f1 = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
for n, pair in PAIRS.items():
    if n == 22:                                   # кулиса длинная — «до» над «после», подпись под каждой
        out = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(out)
        y = 6
        for k, (name, mx, mn) in enumerate(pair):
            im = Image.open(os.path.join(FIG, "apm_" + name + ".png")).convert("RGB")
            s = min((W - 80) / im.width, 300 / im.height)
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            out.paste(im, ((W - im.width) // 2, y)); y += im.height + 8
            t = ("до доработки" if k == 0 else "после доработки") + f": max {mx} МПа, min {mn} МПа"
            d.text(((W - d.textlength(t, font=f1)) / 2, y), t, fill="black", font=f1); y += 70
        out.crop((0, 0, W, y)).save(os.path.join(HERE, "_media", f"image{n}_мкэ.png")); print(n, y)
        continue
    out = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(out)
    for k, (name, mx, mn) in enumerate(pair):
        im = Image.open(os.path.join(FIG, "apm_" + name + ".png")).convert("RGB")
        bw, bh = W // 2 - 40, H - CAP - 20
        s = min(bw / im.width, bh / im.height)
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        x0 = k * W // 2 + (W // 2 - im.width) // 2
        y0 = 10 + (bh - im.height) // 2
        out.paste(im, (x0, y0))
        cx = k * W // 2 + W // 4
        lines = ("до доработки" if k == 0 else "после доработки",) + ((f"max {mx} МПа, min {mn} МПа",) if mx else ())
        for j, t in enumerate(lines):
            tw = d.textlength(t, font=f1)
            d.text((cx - tw / 2, H - CAP + 10 + j * 50), t, fill="black", font=f1)
    out.save(os.path.join(HERE, "_media", f"image{n}_мкэ.png")); print(n)
