# -*- coding: utf-8 -*-
"""РПЗ 23.11 (замечания преподавателя через Корнеева):
  рис. 2, 16 — новые кинематические схемы (образец, повёрнутый на 90°; пары O¹⁰₁В, C¹²₁П, D²³₁В) — Презентация/make_schemes_v2.py;
  рис. 8, 14 — схемы звеньев с белыми кружками вместо чёрных точек (fbd/fig7, fig13_fbd_v24.png);
  рис. 11, 12 — эпюры: точки O, D, K белыми кружками (dots_to_rings.py);
  табл. 19 — σэкв вместо σvM,max; рис. 19–22 — скрины МКЭ без шкалы SVM, max/min под каждым.
    python edit_rpz23.py   (вход РПЗ_укупориватель_исходный.docx → РПЗ_укупориватель.docx)"""
import os
from docx import Document
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "Презентация", "fig")
FBD = os.path.join(HERE, "..", "fbd")
M = os.path.join(HERE, "_media")
NEW = {"image4.png": os.path.join(P, "схема_постановка.png"), "image19.png": os.path.join(P, "схема_результат.png"),
       "image10.png": os.path.join(FBD, "fig7_fbd_v24.png"), "image17.png": os.path.join(FBD, "fig13_fbd_v24.png"),
       "image13.png": os.path.join(M, "image13_кружки.png"), "image14.png": os.path.join(M, "image14_кружки.png"),
       # рис. 19–22: скрины APM без шкалы SVM, max/min под каждым (Корнеев 23:22; fem_pairs.py)
       **{f"image{n}.png": os.path.join(M, f"image{n}_мкэ.png") for n in (22, 23, 24, 25)}}
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
    if abs(cx / cy - w / h) > 0.01:                      # другие пропорции: уже — сохраняем высоту, шире — ширину
        if w / h < cx / cy:
            cx = int(cy * w / h)
        else:
            cy = int(cx * h / w)
        ext.set("cx", str(cx)); ext.set("cy", str(cy))
        for e in inline.iter(f"{{{NS['a']}}}ext"):
            if e.get("cx"): e.set("cx", str(cx)); e.set("cy", str(cy))
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
# п. 3.1 без изменений: подпись пары C со схемы убрана (Корнеев 23:20)
d.save(os.path.join(HERE, "РПЗ_укупориватель.docx"))
print("сохранено")
