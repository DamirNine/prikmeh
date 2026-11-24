# -*- coding: utf-8 -*-
"""РПЗ 23.11 (замечания преподавателя через Корнеева):
  рис. 2, 16 — новые кинематические схемы (образец, повёрнутый на 90°; пары O¹⁰₁В, C¹²₁П, D²³₁В) — Презентация/make_schemes_v2.py;
  рис. 8, 14 — схемы звеньев с белыми кружками вместо чёрных точек (fbd/fig7, fig13_fbd_v24.png);
  рис. 11, 12 — эпюры: точки O, D, K белыми кружками (dots_to_rings.py);
  табл. 19 — σэкв вместо σvM,max; рис. 19–22 — скрины МКЭ без шкалы SVM, max/min под каждым;
  п. 3.2 — контур O → B → D и новый рис. 3 (вектор_контур.png), последующие рисунки и ссылки +2;
  п. 5.1 — новый рис. 4 (схема_синтез.png, треугольник O–Bн–Bк и ψ).
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
# ---- направляющая «после» = вариант Б (Корнеев 23:43): σэкв 920 → 60,7 МПа, масса 402,3 → 389,9 г
if os.environ.get("UKP_VAR", "B") == "B":
    cap = next(q for q in d.paragraphs if q.text.startswith("Рисунок 22 — Направляющая"))
    maths = cap._p.findall(".//m:oMath", NS)
    for t in maths[0].iter(f"{{{NS['m']}}}t"):
        if t.text == "136,2": t.text = "60,7"
    for m_ in maths[1:]: m_.getparent().remove(m_) if m_.getparent().tag != f"{{{NS['m']}}}oMathPara" else None
    rs = cap.runs
    rs[1].text = " МПа; полка с отверстием под шток, без планок"
    for r in rs[2:]: r._r.getparent().remove(r._r)
    tbl = next(t for t in d.tables if t.rows[0].cells[0].text == "Деталь" and "Масса" in t.rows[0].cells[-1].text)
    row = next(r for r in tbl.rows if r.cells[0].text == "Направляющая")
    for t in row._tr.iter(f"{{{NS['m']}}}t"):
        if t.text == "136,2": t.text = "60,7"
        if t.text == "597,2": t.text = "389,9"
    print("  направляющая: вариант Б —", cap.text, "|", [c.text for c in row.cells])
    for q in d.paragraphs:                       # текст под вариант Б (Корнеев 24.11 12:12)
        for r in q.runs:
            for old, new in ((" и направляющей (136,2 МПа) по МКЭ выше допускаемых для Ст3сп;", " по МКЭ выше допускаемых для Ст3сп (в направляющей — 60,7 МПа);"),
                             ("направляющая — отдельная деталь в выемке стойки, закреплена установочным винтом М10;",
                              "направляющая — отдельная деталь в выемке стойки, закреплена установочным винтом М10; шток ползуна проходит в отверстие Ø8,6 её полки;")):
                if old in r.text: r.text = r.text.replace(old, new); print("  Б:", new[:60])

# ---- п. 3.2: формулы контура в векторном виде, y_D (Корнеев 00:14)
import sys; sys.path.insert(0, HERE)
from omml_patch import fix_contour
fix_contour(d)

# ---- п. 3.2: векторный контур O → B → D + новый рисунок 3 (Корнеев 23.11 23:36); дальнейшие рисунки +1
import re, copy
from docx.text.paragraph import Paragraph
from docx.shared import Cm
paras = d.paragraphs
SHIFT = 2                                   # новые рис. 3 (контур) и рис. 4 (синтез)
# 1) перенумерация: подписи «Рисунок N …» и ссылки «рисунок/рисунке/рисунках N [и M]», N ≥ 3
cap_re = re.compile(r"^(Рисунок )(\d+)")
ref_re = re.compile(r"(рисун\w*\s+)(\d+)((?:\s*(?:и|,)\s*)(\d+))?")
def bump(m):
    n = int(m.group(2)); out = m.group(1) + str(n + SHIFT if n >= 3 else n)
    if m.group(3):
        k = int(m.group(4)); out += m.group(3)[:len(m.group(3)) - len(m.group(4))] + str(k + SHIFT if k >= 3 else k)
    return out
nb = 0
for para in paras:
    for ri, r in enumerate(para.runs):
        t = r.text
        if para.text.startswith("Рисунок") and ri == 0:
            t = cap_re.sub(lambda m: m.group(1) + str(int(m.group(2)) + SHIFT if int(m.group(2)) >= 3 else int(m.group(2))), t)
        t = ref_re.sub(bump, t)
        if t != r.text:
            r.text = t; nb += 1
print("  перенумерация рисунков: правок", nb)
# 2) текст п. 3.2
i32 = next(i for i, q in enumerate(paras) if q.text.startswith("Векторный контур O → D"))
rr = paras[i32].runs
assert [r.text for r in rr[:4]] == ["Векторный контур ", "O", " → ", "D"]
rr[3].text = "B"
new = copy.deepcopy(rr[2]._r); rr[3]._r.addnext(new)
new2 = copy.deepcopy(rr[3]._r); new.addnext(new2)
from docx.text.run import Run
Run(new2, paras[i32]).text = "D (рисунок 3)"
print("  п. 3.2:", paras[i32].text[:60])
# 3) рисунок 3 — после формул п. 3.2, перед «3.3.»
i33 = next(i for i, q in enumerate(paras) if q.text.startswith("3.3. Аналоги"))
fig_src = next(q for q in paras if q.text == "" and q._p.findall(f".//{{{NS['a']}}}blip"))   # абзац рис. 1 — образец оформления
cap_src = next(q for q in paras if q.text.startswith("Рисунок 2 —"))
pic_el = copy.deepcopy(fig_src._p)
for ch in list(pic_el):
    if not ch.tag.endswith("}pPr"): pic_el.remove(ch)
cap_el = copy.deepcopy(cap_src._p)
paras[i33]._p.addprevious(pic_el); paras[i33]._p.addprevious(cap_el)
pp = Paragraph(pic_el, paras[i33]._parent)
pp.add_run().add_picture(os.path.join(P, "вектор_контур.png"), width=Cm(8.5))
cp = Paragraph(cap_el, paras[i33]._parent)
for r in cp.runs[1:]: r._r.getparent().remove(r._r)
cp.runs[0].text = "Рисунок 3 — Векторный контур O → B → D (B — проекция D на ось x)"
print("  рисунок 3 вставлен")
# ---- п. 5.1: рисунок 4 — схема с крайними положениями, треугольник O–Bн–Bк и угол ψ (Корнеев 00:02: «и в РПЗ сразу»)
paras = d.paragraphs
i51 = next(i for i, q in enumerate(paras) if q.text.startswith("Минимизируется площадь треугольника"))
r51 = paras[i51].runs
k = next(j for j, r in enumerate(r51) if r.text.startswith(". При заданном ходе"))
r51[k].text = " (рисунок 4)" + r51[k].text
i52 = next(i for i, q in enumerate(paras) if q.text.startswith("5.2. Ограничения"))
pic_el = copy.deepcopy(fig_src._p)
for ch in list(pic_el):
    if not ch.tag.endswith("}pPr"): pic_el.remove(ch)
cap_el = copy.deepcopy(cap_src._p)
paras[i52]._p.addprevious(pic_el); paras[i52]._p.addprevious(cap_el)
Paragraph(pic_el, paras[i52]._parent).add_run().add_picture(os.path.join(P, "схема_синтез.png"), width=Cm(9.5))
cp = Paragraph(cap_el, paras[i52]._parent)
for r in cp.runs[1:]: r._r.getparent().remove(r._r)
base = cp.runs[0]; base.text = "Рисунок 4 — Треугольник O–B"
for txt, sub in (("н", True), ("–B", False), ("к", True), (" и угловой ход ψ на кинематической схеме", False)):
    el = copy.deepcopy(base._r); cp._p.append(el)
    rn = Run(el, cp); rn.text = txt; rn.font.subscript = sub or None
print("  рисунок 4 (синтез) вставлен")

# 24.11 (Корнеев 02:00): «nу = Fкр/Fук ≥ □□3» — пустой индекс, остаток от снятых скобок [nу] (21.11). Удаляем все
# пустые m:sSub/m:sSup/m:sSubSup (ни основания, ни индексов) во всём документе.
_M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
_empty = [el for tag in ("sSub", "sSup", "sSubSup") for el in d.element.body.iter(_M + tag)
          if not "".join(x.text or "" for x in el.iter(_M + "t")).strip()]
for el in _empty:
    el.getparent().remove(el)
print("  пустых индексов в формулах удалено:", len(_empty))

# Заключение по задачам (Корнеев 24.11 12:24; «исправляй и в РПЗ сразу»): добавлены пункты, которых не было
_z = next(i for i, q in enumerate(d.paragraphs) if q.text.strip() == "Заключение" and i > 100)
_b = [q for q in d.paragraphs[_z + 1:_z + 6]]
def _bullet(after, text):
    el = copy.deepcopy(_b[-1]._p); after._p.addnext(el); q = Paragraph(el, after._parent)
    for r in q.runs[1:]: r._r.getparent().remove(r._r)
    q.runs[0].text = text; return q
assert _b[-1].text.startswith("– Построены 3D-модели"), _b[-1].text
_bullet(_b[0], "– Сформулированы техническое задание, ограничения и критерии синтеза: сила руки не более 120 Н, рукоять не более 500 мм, "
               "минимум площади треугольника крайних положений и углового хода.")
_bullet(_b[-1], "– Детали напечатаны (FDM), прототип собран.")
print("  заключение: +2 пункта")

PAGES = os.environ.get("UKP_PAGES", "50")
# 24.11: объём в задании — после вставки формул п. 6.3 (rpz_kin_insert.py) 50 листов; презентация — 15 слайдов
for p in d.paragraphs:
    for r in p.runs:
        for a, b in (("48 листах", PAGES + " листах"), ("49 листах", PAGES + " листах"), ("на 13 слайдов", "на 15 слайдов")):
            if a in r.text:
                r.text = r.text.replace(a, b); print("  задание:", b)

d.save(os.path.join(HERE, "РПЗ_укупориватель.docx"))
print("сохранено")
