# -*- coding: utf-8 -*-
"""Расчёт v30 из v29: материал пальца D — сталь 40Х (APM FEM: 192 МПа > [σ] = 142 МПа стали 45): текст п. 12.6,
табл. 17 и 22, абзацы о проверках, подпись на рис. 13 (fig13_kamen.py). Меняются только эти w:t и картинка.
    python -I build_v30.py v29.docx v30.docx fig13_kamen.png"""
import io, sys, zipfile
from lxml import etree
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC, DST, FIG = sys.argv[1], sys.argv[2], sys.argv[3]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
# (абзац, в котором это есть; что заменить — внутри одного w:t; на что). Буквы O и D — отдельные w:t, их не трогаем
TEXT = [
    ("отдельная деталь из стали 45,", "отдельная деталь из стали 45,", "отдельная деталь из стали 40Х,"),
    ("— сталь 45, [", " и палец ", " — сталь 45, палец "),
    ("— сталь 45, [", " — сталь 45, [", " — сталь 40Х (наибольшее напряжение пальца по расчёту в APM FEM — 192 МПа, больше допускаемых "
                                         "142 МПа для стали 45); для обоих ["),
    ("из стали 45 диаметром 10 мм сохраняются", " и палец ", " из стали 45 и палец "),
    ("из стали 45 диаметром 10 мм сохраняются", " из стали 45 диаметром 10 мм", " из стали 40Х диаметром 10 мм"),
    ("Изгиб осей и пальцев, сварное", "Изгиб осей и пальцев, сварное соединение ступицы и местные напряжения не проверены.",
     "Изгиб пальца проверен в APM FEM (192 МПа; палец — сталь 40Х, [σ] = 314 МПа); изгиб оси, сварное соединение "
     "ступицы и местные напряжения не проверены."),
    ("запрессован в обойму, сталь 45", ", запрессован в обойму, сталь 45", ", запрессован в обойму, сталь 40Х"),
    ("Ø10 мм, сталь 45: срез", "Ø10 мм, сталь 45: срез", "Ø10 мм, ось — сталь 45, палец — сталь 40Х: срез"),
]

zin = zipfile.ZipFile(SRC)
root = etree.fromstring(zin.read("word/document.xml"))
rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
# текст: каждая замена — внутри одного w:t нужного абзаца (абзац или ячейка таблицы — самый внутренний w:p)
for mark, old, new in TEXT:
    ps = [p for p in root.iter(W + "p") if mark in "".join(t.text or "" for t in p.iter(W + "t"))]
    assert len(ps) >= 1, mark
    ts = [t for p in ps for t in p.iter(W + "t") if t.text and old in t.text]
    assert len(ts) == 1, (mark, old, len(ts))
    ts[0].text = ts[0].text.replace(old, new)
body = "".join(t.text or "" for t in root.iter(W + "t"))
assert "палец D — сталь 45" not in body and "палец D из стали 45" not in body
# рисунок 13
dr = [d for d in root.iter(W + "drawing") if d.find(".//" + PIC + "cNvPr").get("name") == "fig13_kamen_v29.png"]
assert len(dr) == 1
d = dr[0]
png = open(FIG, "rb").read()
w_px, h_px = Image.open(io.BytesIO(png)).size
cx = 5760000
cy = round(cx * h_px / w_px)
etree.SubElement(rels, "{%s}Relationship" % PR, Id="rIdV30fig13", Type=R[1:-1] + "/image", Target="media/fig13_kamen_v30.png")
d.find(".//" + A + "blip").set(R + "embed", "rIdV30fig13")
for e in (d.find(".//" + WP + "extent"), d.find(".//" + A + "xfrm/" + A + "ext")):
    e.set("cx", str(cx)); e.set("cy", str(cy))
d.find(".//" + PIC + "cNvPr").set("name", "fig13_kamen_v30.png")
old = [r for r in rels if r.get("Target") == "media/fig13_kamen_v29.png"]
assert len(old) == 1
rels.remove(old[0])
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
        elif item.filename == "word/_rels/document.xml.rels":
            zout.writestr(item, etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True))
        elif item.filename != "word/media/fig13_kamen_v29.png":
            zout.writestr(item, zin.read(item.filename))
    zout.writestr("word/media/fig13_kamen_v30.png", png)
print(f"текст: {len(TEXT)} замены; рисунок 13: {cx / 360000:.1f} × {cy / 360000:.1f} см → {DST}")
