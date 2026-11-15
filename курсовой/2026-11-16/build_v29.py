# -*- coding: utf-8 -*-
"""Расчёт v29 из v28: палец D — текущая деталь (резьба М10 × 1,5, шайба 10, гайка М10 навинчена до конца резьбы, шайба
в 0,5 мм перед ползуном): рис. 13 (fig13_kamen.py) и два абзаца — текст под рис. 13 и описание пары в п. 12.6. Меняются
только эти места (w:t абзацев, картинка и её связь); остальное document.xml — без изменений.
    python -I build_v29.py v28.docx v29.docx fig13_kamen.png"""
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
TEXT = [
    ("а шайба и гайка М8 на его резьбовом конце не дают ползуну сместиться вдоль оси.",
     "а шайба и гайка М10 на его резьбовом конце (резьба М10 × 1,5) не дают ползуну сместиться вдоль оси."),
    ("вдоль оси ползун удерживают шайба и гайка М8 на резьбовом конце пальца: гайка затянута до упора шайбы в уступ пальца, "
     "уступ — в 0,5 мм перед ползуном, поэтому ползун не зажат (рисунок 13, г)",
     "вдоль оси ползун удерживают шайба 10 и гайка М10 на резьбовом конце пальца (резьба М10 × 1,5): гайка навинчена до "
     "конца резьбы, шайба — в 0,5 мм перед ползуном, поэтому ползун не зажат (рисунок 13, г)"),
]

zin = zipfile.ZipFile(SRC)
root = etree.fromstring(zin.read("word/document.xml"))
rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
# текст: каждая замена — внутри одного w:t
for old, new in TEXT:
    ts = [t for t in root.iter(W + "t") if t.text and old in t.text]
    assert len(ts) == 1, (old[:50], len(ts))
    ts[0].text = ts[0].text.replace(old, new)
body = "".join(t.text or "" for t in root.iter(W + "t"))
assert "М8" not in body and "уступ пальца" not in body, "остались упоминания М8 / уступа"
# рисунок 13
dr = [d for d in root.iter(W + "drawing") if d.find(".//" + PIC + "cNvPr").get("name") == "fig13_kamen_v28.png"]
assert len(dr) == 1
d = dr[0]
png = open(FIG, "rb").read()
w_px, h_px = Image.open(io.BytesIO(png)).size
cx = 5760000
cy = round(cx * h_px / w_px)
etree.SubElement(rels, "{%s}Relationship" % PR, Id="rIdV29fig13", Type=R[1:-1] + "/image", Target="media/fig13_kamen_v29.png")
d.find(".//" + A + "blip").set(R + "embed", "rIdV29fig13")
for e in (d.find(".//" + WP + "extent"), d.find(".//" + A + "xfrm/" + A + "ext")):
    e.set("cx", str(cx)); e.set("cy", str(cy))
d.find(".//" + PIC + "cNvPr").set("name", "fig13_kamen_v29.png")
old = [r for r in rels if r.get("Target") == "media/fig13_kamen_v28.png"]
assert len(old) == 1
rels.remove(old[0])
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
        elif item.filename == "word/_rels/document.xml.rels":
            zout.writestr(item, etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True))
        elif item.filename != "word/media/fig13_kamen_v28.png":
            zout.writestr(item, zin.read(item.filename))
    zout.writestr("word/media/fig13_kamen_v29.png", png)
print(f"текст: {len(TEXT)} замены; рисунок 13: {cx / 360000:.1f} × {cy / 360000:.1f} см → {DST}")
