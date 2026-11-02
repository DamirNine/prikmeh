# -*- coding: utf-8 -*-
"""Сборка v18 (02.11) поверх v17: все выносные формулы — формулами Word (LaTeX → OMML, omml.py, formulas_latex.py);
вместо таблицы 20 — матричная запись системы 9 уравнений уточнённого расчёта (таблицы 21–23 → 20–22);
рис. 14 — 9 графиков неизвестных, первичный и уточнённый расчёты (figs_v18.py); индексы R10x → R10 с верхним x, как в разд. 11."""
import copy, os, re
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from lxml import etree

from omml import math_paragraph, replace_with_math
from formulas_latex import FORMULAS, MATRIX, MATRIX_B3
from list_formulas import collect, marked

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v17.docx")
DST = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v18.docx")

doc, found = collect(SRC)
body = doc.element.body


def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def find_p(prefix):
    for el in body.iterchildren(qn("w:p")):
        if ptext(el).startswith(prefix):
            return el
    raise KeyError(prefix)


def add_keep_next(p):
    ppr = p.find(qn("w:pPr"))
    if ppr is None or ppr.find(qn("w:keepNext")) is not None:
        return
    kn = parse_xml(f'<w:keepNext {nsdecls("w")}/>')
    st = ppr.find(qn("w:pStyle"))
    if st is not None:
        st.addnext(kn)
    else:
        ppr.insert(0, kn)


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


# ================================================================ 1. формулы
assert len(found) == len(FORMULAS), (len(found), len(FORMULAS))
n_conv = n_split = n_del = 0
for (kind, head, text, p), (prefix, tex) in zip(found, FORMULAS):
    assert text.startswith(prefix), f"не совпало: {text!r} / {prefix!r}"
    if tex is None:
        p.getparent().remove(p); n_del += 1
        continue
    lines = tex if isinstance(tex, list) else [tex]
    replace_with_math(p, lines[0]); n_conv += 1
    cur = p
    for extra in lines[1:]:
        q = copy.deepcopy(p)                       # те же свойства абзаца
        replace_with_math(q, extra)
        cur.addnext(q); cur = q; n_split += 1
    if len(lines) > 1:                             # строки, кроме последней, держим с последующей
        k = p
        for _ in lines[:-1]:
            add_keep_next(k); k = k.getnext()

# ================================================================ 2. индексы R10x → R10 с верхним x (как в разд. 11 и на рисунках)
n_idx = 0
for r in list(body.iter(qn("w:r"))):
    rpr = r.find(qn("w:rPr"))
    va = rpr.find(qn("w:vertAlign")) if rpr is not None else None
    if va is None or va.get(qn("w:val")) != "subscript":
        continue
    t = r.find(qn("w:t"))
    if t is None or not re.fullmatch(r"(10|23|32)[xy]", t.text or ""):
        continue
    num, ax = t.text[:2], t.text[2]
    t.text = num
    r2 = copy.deepcopy(r); r2.find(qn("w:t")).text = ax
    r2.find(qn("w:rPr")).find(qn("w:vertAlign")).set(qn("w:val"), "superscript")
    r.addnext(r2); n_idx += 1

# ================================================================ 3. таблица 20 → матричная запись системы
cap20 = find_p("Таблица 20 — Столбец свободных членов")
tbl20 = cap20.getnext(); assert tbl20.tag == qn("w:tbl")
intro = find_p("Силы тяжести и инерции в каждом положении известны")
sub_any(intro, "а меняется только столбец свободных членов B(φ) — таблица 20. Система решена для тех же 40 001 положения кулисы.",
        "а меняется только столбец свободных членов B(φ) — в первичном расчёте (п. 11.5) в нём были отличны от нуля только два последних элемента. "
        "Полная система 9 уравнений уточнённого расчёта в матричной форме A(φ)·X = B(φ):")
add_keep_next(intro)
mat = math_paragraph(MATRIX, sz=22, keep_next=True, before=120, after=60)
b3 = math_paragraph(MATRIX_B3, sz=24, before=60, after=60)
after_txt = copy.deepcopy(intro)
for t in after_txt.iter(qn("w:t")):
    t.text = ""
after_txt.find(qn("w:pPr")).remove(after_txt.find(qn("w:pPr")).find(qn("w:keepNext")))
list(after_txt.iter(qn("w:t")))[0].text = "Система решена для тех же 40 001 положения кулисы."
cap20.addprevious(mat); mat.addnext(b3); b3.addnext(after_txt)
cap20.getparent().remove(tbl20); cap20.getparent().remove(cap20)

# ================================================================ 4. перенумерация таблиц 21–23 → 20–22 и ссылок
for prefix, old, new in [("В точках смены фаз", "(таблицы 19, 21)", "(таблицы 19, 20)"),
                         ("Сила руки и поправки уточнённого расчёта", "в таблице 21.", "в таблице 20."),
                         ("Таблица 21 — Сила руки и реакции", "Таблица 21", "Таблица 20"),
                         ("Вес и силы инерции участка D–K", "Результаты — в таблице 22.", "Результаты — в таблице 21."),
                         ("Таблица 22 — Проверка прочности", "Таблица 22", "Таблица 21"),
                         ("Принятые параметры механизма и пункты расчёта", "в таблице 23.", "в таблице 22."),
                         ("Таблица 23 — Принятые параметры механизма", "Таблица 23", "Таблица 22")]:
    sub_any(find_p(prefix), old, new)
sub_any(find_p("Внутренние силы в сечении под камнем"), " (интегралы — от lOD до L):", ":")

# таблицы раздела 13 — не разрывать по страницам
for cap in ("Таблица 19 — Силы инерции", "Таблица 20 — Сила руки", "Таблица 21 — Проверка прочности"):
    tbl = find_p(cap).getnext(); assert tbl.tag == qn("w:tbl")
    rows = tbl.findall(qn("w:tr"))
    for tr in rows[:-1]:
        for cp in tr.iter(qn("w:p")):
            add_keep_next(cp)

# ================================================================ 5. рисунок 14 — 9 графиков
from PIL import Image
cap14 = find_p("Рисунок 14 — ")
pic = cap14.getprevious()
blip = next(pic.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))
png = os.path.join(SP, "fig14_unknowns_v18.png")
doc.part.related_parts[blip.get(qn("r:embed"))]._blob = open(png, "rb").read()
w, h = Image.open(png).size
ext = next(pic.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent"))
cx = int(ext.get("cx")); cy = int(round(cx * h / w)); ext.set("cy", str(cy))
for a_ext in pic.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}ext"):
    if a_ext.get("cx"):
        a_ext.set("cx", str(cx)); a_ext.set("cy", str(cy))
for r in cap14.findall(qn("w:r"))[1:]:
    cap14.remove(r)
t0 = cap14.find(qn("w:r")).find(qn("w:t"))
t0.text = ("Рисунок 14 — Неизвестные системы 9 уравнений в первичном (штриховые линии) и уточнённом (сплошные) силовых расчётах "
           "в зависимости от угла кулисы φ (L = 500 мм); оранжевым по правой шкале — разность уточнённого и первичного значений; "
           "серым — пластическая деформация")
sub_any(find_p("Сила руки и поправки уточнённого расчёта"), "Сила руки и поправки уточнённого расчёта к реакциям показаны на рисунке 14",
        "Все девять неизвестных системы в первичном и уточнённом расчётах показаны на рисунке 14 (как на рисунке 9)")

doc.save(DST)
print(f"saved {DST}\nформул: {n_conv} заменено, {n_split} строк добавлено, {n_del} абзацев объединено в систему; индексов R: {n_idx}")
