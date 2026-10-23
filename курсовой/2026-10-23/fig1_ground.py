# -*- coding: utf-8 -*-
"""Рис. 1: опора стойки под осью O перерисована ровно и симметрично (основание, равная штриховка); варианты с бруском и с роликом."""
import io, os
from PIL import Image, ImageDraw
from docx import Document
from docx.oxml.ns import qn

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SP, "..", "2026-10-11", "Расчет_силовой_и_кинематический_тангенсный_механизм_v10.docx")
doc = Document(SRC)
els = list(doc.element.body.iterchildren())
txt = lambda el: "".join(x.text or "" for x in el.iter(qn("w:t")))
i = next(k for k, el in enumerate(els) if txt(el).startswith("Рисунок 1 —"))
blip = next(els[i - 1].iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))
base = Image.open(io.BytesIO(doc.part.related_parts[blip.get(qn("r:embed"))].blob)).convert("RGBA")

def ground(im):
    S = 4
    big = im.resize((im.width * S, im.height * S), Image.LANCZOS); d = ImageDraw.Draw(big)
    x0, yb = 184, 1015                         # ось y (стойка) и основание
    d.rectangle(((x0 - 60) * S, (yb - 6) * S, (x0 + 60) * S, (yb + 40) * S), fill=(255, 255, 255, 255))
    d.line((x0 * S, (yb - 8) * S, x0 * S, (yb + 40) * S), fill=(0, 0, 0, 255), width=3 * S)      # продолжение оси y
    d.line(((x0 - 46) * S, yb * S, (x0 + 46) * S, yb * S), fill=(0, 0, 0, 255), width=4 * S)      # основание
    for k in range(9):                                                                              # штриховка 45°
        xs = x0 - 40 + 10 * k
        d.line((xs * S, (yb + 2) * S, (xs - 12) * S, (yb + 14) * S), fill=(0, 0, 0, 255), width=3 * S)
    return big.resize(im.size, Image.LANCZOS)

def roller(im):
    S = 4
    big = im.resize((im.width * S, im.height * S), Image.LANCZOS); d = ImageDraw.Draw(big)
    cx, cy = 465 * S, 730.5 * S
    for r, w, fill in ((33, 4, (255, 255, 255, 255)), (9, 3, (255, 255, 255, 255))):
        d.ellipse((cx - r * S, cy - r * S, cx + r * S, cy + r * S), fill=fill, outline=(0, 0, 0, 255), width=w * S)
    r = 3.6 * S; d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 0, 0, 255))
    return big.resize(im.size, Image.LANCZOS)

sq = ground(base); sq.save(os.path.join(SP, "fig1_scheme_square.png"))
roller(sq).save(os.path.join(SP, "fig1_scheme_roller.png"))
print("ok")
