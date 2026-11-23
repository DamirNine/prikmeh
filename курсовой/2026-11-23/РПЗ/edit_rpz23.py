# -*- coding: utf-8 -*-
"""РПЗ 23.11 (замечания преподавателя через Корнеева):
  рис. 2, 16 — новые кинематические схемы (образец, повёрнутый на 90°; пары O¹⁰₁В, C¹²₁П, D²³₁В) — Презентация/make_schemes_v2.py;
  рис. 8, 14 — схемы звеньев с белыми кружками вместо чёрных точек (fbd/fig7, fig13_fbd_v23.png);
  рис. 11, 12 — эпюры: точки O, D, K белыми кружками (dots_to_rings.py);
  табл. 19 — σэкв вместо σvM,max; п. 3.1 — пара C (1–2).
    python edit_rpz23.py   (вход РПЗ_укупориватель_исходный.docx → РПЗ_укупориватель.docx)"""
import os
from docx import Document
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "Презентация", "fig")
FBD = os.path.join(HERE, "..", "fbd")
M = os.path.join(HERE, "_media")
NEW = {"image4.png": os.path.join(P, "схема_постановка.png"), "image19.png": os.path.join(P, "схема_результат.png"),
       "image10.png": os.path.join(FBD, "fig7_fbd_v23.png"), "image17.png": os.path.join(FBD, "fig13_fbd_v23.png"),
       "image13.png": os.path.join(M, "image13_кружки.png"), "image14.png": os.path.join(M, "image14_кружки.png")}
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

d = Document(os.path.join(HERE, "РПЗ_укупориватель_исходный.docx"))
body = d.element.body
from PIL import Image
for blip in body.iter(f"{{{NS['a']}}}blip"):
    rid = blip.get(f"{{{NS['r']}}}embed")
    part = d.part.related_parts[rid]
    name = os.path.basename(str(part.partname))
    if name not in NEW:
        continue
    part._blob = open(NEW[name], "rb").read()
    w, h = Image.open(NEW[name]).size
    inline = next(a for a in blip.iterancestors() if a.tag in (f"{{{NS['wp']}}}inline", f"{{{NS['wp']}}}anchor"))
    ext = inline.find("wp:extent", NS)
    cx, cy = int(ext.get("cx")), int(ext.get("cy"))
    if abs(cx / cy - w / h) > 0.01:                      # другие пропорции — сохраняем высоту, меняем ширину
        cx = int(cy * w / h)
        ext.set("cx", str(cx))
        for e in inline.iter(f"{{{NS['a']}}}ext"):
            if e.get("cx"): e.set("cx", str(cx))
    print(f"  {name} ← {os.path.basename(NEW[name])} ({w}×{h})")

# табл. 19: σ_{vM,max} → σ_{экв}
for t in body.iter(f"{{{NS['m']}}}t"):
    if t.text == "vM":
        sub = t.getparent().getparent()
        rs = sub.findall("m:r", NS)
        t.text = "экв"
        for r in rs[1:]:
            sub.remove(r)
        print("  табл. 19: σэкв")
# п. 3.1: пара C (1–2)
for p in d.paragraphs:
    if p.text.startswith("Кинематические пары: O (0–1)"):
        for r in p.runs:
            if "1–2 и 3–0" in r.text:
                r.text = r.text.replace("1–2 и 3–0", "C (1–2) и 3–0"); print("  п. 3.1: C (1–2)")
d.save(os.path.join(HERE, "РПЗ_укупориватель.docx"))
print("сохранено")
