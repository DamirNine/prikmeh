# -*- coding: utf-8 -*-
"""Расчёт v27 из v26: палец D — отдельная деталь (замечание преподавателя: камень — деталь с отверстием + палец, фиксация по
оси резьбой и гайкой). Рис. 13 — новый (fig13_kamen.py: в разрезе Б–Б палец запрессован в стенку обоймы, новый разрез В–В по
оси пальца — ползун на пальце, шайба и гайка М8, уступ, одна плоскость среза); текст под рисунком, п. 12.6 и табл. 17 — «палец
запрессован», вместо «заодно с обоймой». Меняются только word/document.xml и связи, добавляется одна картинка.
    python -I build_v27.py v26.docx v27.docx fig13_kamen.png"""
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
XS = "{http://www.w3.org/XML/1998/namespace}space"

zin = zipfile.ZipFile(SRC)
root = etree.fromstring(zin.read("word/document.xml"))
rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
P = list(root.iter(W + "p"))
txt = lambda p: "".join(t.text or "" for t in p.iter(W + "t"))
n_rep = 0


def expect(i, start):
    assert txt(P[i]).startswith(start), (i, txt(P[i])[:80], start)
    return P[i]


def replace(p, old, new):
    """замена в тексте абзаца (может быть разбит на несколько w:t; формулы Word не затрагиваются)"""
    global n_rep
    nodes = list(p.iter(W + "t"))
    text = "".join(t.text or "" for t in nodes)
    start = text.find(old)
    assert start >= 0 and text.count(old) == 1, (old, text[:120])
    end, pos, done = start + len(old), 0, False
    for t in nodes:
        s = t.text or ""
        a, b = pos, pos + len(s)
        pos = b
        if b <= start or a >= end:
            continue
        t.text = s[:max(start - a, 0)] + ("" if done else new) + (s[max(end - a, 0):] if b > end else "")
        t.set(XS, "preserve")
        done = True
    n_rep += 1


# ---------------- рисунок 13: новая картинка, ширина 16 см (как в v26), высота — по пропорциям
fig_p = P[1148]
cap = expect(1149, "Рисунок 13 — Камень и кулиса.")
d = fig_p.find(".//" + W + "drawing")
assert d is not None
png = open(FIG, "rb").read()
w_px, h_px = Image.open(io.BytesIO(png)).size
cx = 5760000
cy = round(cx * h_px / w_px)
rid = "rIdV27fig13"
etree.SubElement(rels, "{%s}Relationship" % PR, Id=rid, Type=R[1:-1] + "/image", Target="media/fig13_kamen_v27.png")
d.find(".//" + A + "blip").set(R + "embed", rid)
for e in (d.find(".//" + WP + "extent"), d.find(".//" + A + "xfrm/" + A + "ext")):
    e.set("cx", str(cx)); e.set("cy", str(cy))
d.find(".//" + PIC + "cNvPr").set("name", "fig13_kamen_v27.png")
replace(cap, "сечение обоймы и полосы.", "сечение обоймы и полосы; В–В — соединение камня с ползуном по оси пальца D.")

# ---------------- текст под рисунком
p = expect(1151, "В разрезе Б–Б обойма и полоса заштрихованы")
replace(p, "палец D расположен за секущей плоскостью и показан без штриховки.",
        "палец D расположен за секущей плоскостью и показан без штриховки, внутри стенки обоймы — штриховыми линиями.")
replace(p, " Палец D диаметром 10 мм выполнен заодно с обоймой.",
        " Палец D диаметром 10 мм — отдельная деталь, запрессованная в стенку обоймы. В разрезе В–В палец, шайба и гайка "
        "показаны нерассечёнными (ГОСТ 2.305): ползун поворачивается на пальце, а шайба и гайка М8 на его резьбовом конце не "
        "дают ползуну сместиться вдоль оси. Резьбовой конец нагружен только затяжкой гайки; срез пальца — по диаметру 10 мм "
        "в одной плоскости, между обоймой и ползуном.")

# ---------------- п. 12.6: конструкция пары D
p = expect(1254, "палец D выполнен заодно с обоймой камня")
replace(p, "палец D выполнен заодно с обоймой камня и входит",
        "палец D — отдельная деталь из стали 45, запрессован в стенку обоймы камня (посадка H7/r6) и входит")
replace(p, "в котором поворачивается;",
        "в котором поворачивается; вдоль оси ползун удерживают шайба и гайка М8 на резьбовом конце пальца: гайка затянута до "
        "упора шайбы в уступ пальца, уступ — в 0,5 мм перед ползуном, поэтому ползун не зажат (рисунок 13, г);")
replace(expect(1313, "D: палец Ø10 заодно с обоймой"), "D: палец Ø10 заодно с обоймой, сталь 45",
        "D: палец Ø10, запрессован в обойму, сталь 45")

left = [t for t in (txt(q) for q in root.iter(W + "p")) if "заодно" in t]
assert not left, left
data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
rels_data = etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True)
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, data)
        elif item.filename == "word/_rels/document.xml.rels":
            zout.writestr(item, rels_data)
        else:
            zout.writestr(item, zin.read(item.filename))
    zout.writestr("word/media/fig13_kamen_v27.png", png)
print(f"замен: {n_rep}; рисунок 13: {cx / 360000:.1f} × {cy / 360000:.1f} см → {DST}")
