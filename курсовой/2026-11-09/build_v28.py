# -*- coding: utf-8 -*-
"""Расчёт v28 из v27: на рис. 13 палец D — своим цветом (отдельная деталь; как в 3D-модели), картинка из fig13_kamen.py.
Меняются только связи (новая картинка) и ссылка на неё в word/document.xml; текст не меняется.
    python -I build_v28.py v27.docx v28.docx fig13_kamen.png"""
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

zin = zipfile.ZipFile(SRC)
root = etree.fromstring(zin.read("word/document.xml"))
rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
P = list(root.iter(W + "p"))
txt = lambda p: "".join(t.text or "" for t in p.iter(W + "t"))
assert txt(P[1149]).startswith("Рисунок 13 — Камень и кулиса."), txt(P[1149])[:60]
d = P[1148].find(".//" + W + "drawing")
assert d.find(".//" + PIC + "cNvPr").get("name") == "fig13_kamen_v27.png"
png = open(FIG, "rb").read()
w_px, h_px = Image.open(io.BytesIO(png)).size
cx = 5760000
cy = round(cx * h_px / w_px)
etree.SubElement(rels, "{%s}Relationship" % PR, Id="rIdV28fig13", Type=R[1:-1] + "/image", Target="media/fig13_kamen_v28.png")
d.find(".//" + A + "blip").set(R + "embed", "rIdV28fig13")
for e in (d.find(".//" + WP + "extent"), d.find(".//" + A + "xfrm/" + A + "ext")):
    e.set("cx", str(cx)); e.set("cy", str(cy))
d.find(".//" + PIC + "cNvPr").set("name", "fig13_kamen_v28.png")
old = [r for r in rels if r.get("Target") == "media/fig13_kamen_v27.png"]          # прежняя картинка больше не нужна
assert len(old) == 1
rels.remove(old[0])
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
        elif item.filename == "word/_rels/document.xml.rels":
            zout.writestr(item, etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True))
        elif item.filename != "word/media/fig13_kamen_v27.png":
            zout.writestr(item, zin.read(item.filename))
    zout.writestr("word/media/fig13_kamen_v28.png", png)
print(f"рисунок 13 заменён: {cx / 360000:.1f} × {cy / 360000:.1f} см → {DST}")
