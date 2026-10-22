# -*- coding: utf-8 -*-
"""Рис. 1 с камнем-роликом: берёт расчётную схему из v10 и рисует в точке D ролик (окружность) с осью вместо камня-бруска."""
import io, os
from PIL import Image, ImageDraw
from docx import Document
from docx.oxml.ns import qn

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SP, "..", "2026-10-11", "Расчет_силовой_и_кинематический_тангенсный_механизм_v10.docx")
doc = Document(SRC)
els = list(doc.element.body.iterchildren())
txt = lambda el: "".join(x.text or "" for x in el.iter(qn("w:t")))
BLIP = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
i = next(k for k, el in enumerate(els) if txt(el).startswith("Рисунок 1 —"))
blip = next(els[i - 1].iter(BLIP))
im = Image.open(io.BytesIO(doc.part.related_parts[blip.get(qn("r:embed"))].blob)).convert("RGBA")

S = 4                                                    # суперсэмплинг для гладкого контура
big = im.resize((im.width * S, im.height * S), Image.LANCZOS)
d = ImageDraw.Draw(big)
cx, cy = 465 * S, 730.5 * S                              # точка D на схеме, пиксели исходной картинки
R, r_pin, r_dot = 33 * S, 9 * S, 3.6 * S
d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4 * S)
d.ellipse((cx - r_pin, cy - r_pin, cx + r_pin, cy + r_pin), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=3 * S)
d.ellipse((cx - r_dot, cy - r_dot, cx + r_dot, cy + r_dot), fill=(0, 0, 0, 255))
big.resize(im.size, Image.LANCZOS).save(os.path.join(SP, "fig1_scheme_roller.png"))
print("ok")
