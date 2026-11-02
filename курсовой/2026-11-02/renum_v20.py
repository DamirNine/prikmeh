# -*- coding: utf-8 -*-
"""Перенумерация в v20 после удаления пользователем п. 12.6 и таблицы 17 (правится сам v20 по просьбе пользователя):
таблицы 18–22 → 17–21; пп. 12.7, 12.8 → 12.6, 12.7; ссылки на удалённый п. 12.6 — на пункты, где эти величины получены."""
import os, re
from docx import Document
from docx.oxml.ns import qn

SP = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(SP, "Расчет_силовой_и_кинематический_тангенсный_механизм_v20.docx")
doc = Document(PATH)
body = doc.element.body
log = []


def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def replace_spans(p, edits):
    """edits: [(i, j, new)] по полному тексту абзаца; замена с конца, форматирование — первого затронутого w:t"""
    ts = list(p.iter(qn("w:t")))
    for i, j, new in sorted(edits, reverse=True):
        pos, first = 0, True
        for t in ts:
            s0, e0 = pos, pos + len(t.text or ""); pos = e0
            if e0 <= i or s0 >= j:
                if not (i == j and s0 <= i < e0):
                    continue
            txt = t.text or ""
            t.text = txt[:max(0, i - s0)] + (new if first else "") + (txt[j - s0:] if e0 > j else "")
            t.set(qn("xml:space"), "preserve"); first = False


TBL = re.compile(r"([Тт]аблиц[аеуыи]\s+)(\d+)((?:\s*(?:,|и)\s*\d+)*)")


def renum_tables(text):
    edits = []
    for m in TBL.finditer(text):
        for g in (2, 3):
            if not m.group(g):
                continue
            for n in re.finditer(r"\d+", m.group(g)):
                k = int(n.group())
                if k >= 18:
                    a = m.start(g) + n.start(); edits.append((a, a + len(n.group()), str(k - 1)))
    return edits


paras = list(body.iter(qn("w:p")))
for p in paras:
    t = ptext(p)
    edits = renum_tables(t)
    in_cell = p.getparent().tag == qn("w:tc")
    # ссылки на удалённый п. 12.6
    for m in re.finditer(r"п\. 12\.6\b", t):
        if "в 1,90 раза" in t:
            edits.append((m.start(), m.end(), "п. 12.5"))
        elif in_cell and t.strip() == "п. 12.6":
            edits.append((m.start(), m.end(), "пп. 12.4, 12.5"))
        else:
            raise SystemExit("неучтённая ссылка на п. 12.6: " + t[:120])
    for m in re.finditer(r"п\. 12\.7\b", t):
        edits.append((m.start(), m.end(), "п. 12.6"))
    if t.startswith("12.7. Массы"):
        edits.append((0, 4, "12.6"))
    if t.startswith("12.8. Итоги"):
        edits.append((0, 4, "12.7"))
    if edits:
        before = t
        replace_spans(p, edits)
        log.append((before[:110], ptext(p)[:110]))
doc.save(PATH)
for a, b in log:
    print("-", a); print("+", b)
print(len(log), "абзацев изменено")
