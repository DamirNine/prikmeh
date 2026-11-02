# -*- coding: utf-8 -*-
"""Сборка v19 (02.11) поверх v18: рис. 14 — только уточнённый силовой расчёт (figs_v19.py), без первичного и разности."""
import os
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v18.docx")
DST = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v19.docx")
doc = Document(SRC)
body = doc.element.body


def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def find_p(prefix):
    for el in body.iterchildren(qn("w:p")):
        if ptext(el).startswith(prefix):
            return el
    raise KeyError(prefix)


def sub_any(el, old, new):
    ts = list(el.iter(qn("w:t")))
    full = "".join(t.text or "" for t in ts)
    assert full.count(old) == 1, (old, full.count(old))
    i = full.index(old); j = i + len(old); pos, first = 0, True
    for t in ts:
        s0, e0 = pos, pos + len(t.text or ""); pos = e0
        if e0 <= i or s0 >= j:
            continue
        txt = t.text or ""
        t.text = txt[:max(0, i - s0)] + (new if first else "") + (txt[j - s0:] if e0 > j else "")
        t.set(qn("xml:space"), "preserve"); first = False


cap14 = find_p("Рисунок 14 — ")
pic = cap14.getprevious()
blip = next(pic.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))
png = os.path.join(SP, "fig14_unknowns_v19.png")
doc.part.related_parts[blip.get(qn("r:embed"))]._blob = open(png, "rb").read()
w, h = Image.open(png).size
ext = next(pic.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent"))
cx = int(ext.get("cx")); cy = int(round(cx * h / w)); ext.set("cy", str(cy))
for a_ext in pic.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}ext"):
    if a_ext.get("cx"):
        a_ext.set("cx", str(cx)); a_ext.set("cy", str(cy))
for r in cap14.findall(qn("w:r"))[1:]:
    cap14.remove(r)
cap14.find(qn("w:r")).find(qn("w:t")).text = ("Рисунок 14 — Неизвестные системы 9 уравнений уточнённого силового расчёта в зависимости "
                                              "от угла кулисы φ (L = 500 мм); серым — пластическая деформация")
sub_any(find_p("Все девять неизвестных системы в первичном и уточнённом"),
        "Все девять неизвестных системы в первичном и уточнённом расчётах показаны на рисунке 14 (как на рисунке 9)",
        "Все девять неизвестных системы уточнённого расчёта показаны на рисунке 14 (первичного — на рисунке 9)")
doc.save(DST)
print("saved", DST)
