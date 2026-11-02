# -*- coding: utf-8 -*-
"""Сборка v20 (02.11) поверх v19: рис. 12 перерисован (fig12_v20.py) — сечение Б–Б с губками внутри рисунка,
палец D — одна деталь с обоймой; наложенная поверх рис. 12 картинка пользователя (плавающая) удалена."""
import os
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v19.docx")
DST = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v20.docx")
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
doc = Document(SRC)
body = doc.element.body


def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


cap = next(p for p in body.iterchildren(qn("w:p")) if ptext(p).startswith("Рисунок 12 — "))
pic = cap.getprevious()
anchors, inlines = list(pic.iter(WP + "anchor")), list(pic.iter(WP + "inline"))
assert len(anchors) == 1 and len(inlines) == 1, (len(anchors), len(inlines))
# плавающая картинка — удалить вместе с её прогоном
run = anchors[0]
while run.tag != qn("w:r"):
    run = run.getparent()
run.getparent().remove(run)
# основная картинка — заменить содержимое и высоту
blip = next(inlines[0].iter(A + "blip"))
png = os.path.join(SP, "fig12_kamen_v20.png")
doc.part.related_parts[blip.get(qn("r:embed"))]._blob = open(png, "rb").read()
w, h = Image.open(png).size
ext = inlines[0].find(WP + "extent")
cx = int(ext.get("cx")); cy = int(round(cx * h / w)); ext.set("cy", str(cy))
for a_ext in inlines[0].iter(A + "ext"):
    if a_ext.get("cx"):
        a_ext.set("cx", str(cx)); a_ext.set("cy", str(cy))
# подпись: палец D заодно с обоймой
t = list(cap.iter(qn("w:t")))[-1]
assert t.text.rstrip().endswith("рабочее ребро полосы"), t.text
t.text = t.text.rstrip() + "; палец D выполнен заодно с обоймой"
doc.save(DST)
print("saved", DST)
