# -*- coding: utf-8 -*-
"""Список выносных формул документа: абзацы, набранные шрифтом Cambria Math (как FORM в сборках), и абзацы с OMML.
Текст с разметкой индексов: _{…} — нижний, ^{…} — верхний. Запуск: python list_formulas.py <docx> <out.txt>"""
import re, sys
from docx import Document
from docx.oxml.ns import qn

M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


def marked(p):
    out = []
    for r in p.iter(qn("w:r")):
        if r.getparent().tag.startswith(M):
            continue
        t = "".join(x.text or "" for x in r.iter(qn("w:t")))
        if not t:
            continue
        va = r.find(qn("w:rPr") + "/" + qn("w:vertAlign"))
        v = va.get(qn("w:val")) if va is not None else None
        out.append(("_{%s}" % t) if v == "subscript" else ("^{%s}" % t) if v == "superscript" else t)
    s = "".join(out)
    return re.sub(r"_\{([^{}]*)\}_\{([^{}]*)\}", r"_{\1\2}", s)


def is_formula(p):
    if list(p.iter(M + "oMath")):
        return "omml"
    fonts = {f.get(qn("w:ascii")) for f in p.iter(qn("w:rFonts"))}
    txt = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
    if txt and "Cambria Math" in fonts:
        return "text"
    return None


def collect(path):
    doc = Document(path)
    res, head = [], ""
    for p in doc.element.body.iterchildren(qn("w:p")):
        txt = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
        if re.match(r"^\d{1,2}\.(\d{1,2}\.)? \S", txt) and len(txt) < 110:
            head = txt
        k = is_formula(p)
        if k:
            res.append((k, head, marked(p) if k == "text" else "".join(x.text or "" for x in p.iter(M + "t")), p))
    return doc, res


if __name__ == "__main__":
    doc, res = collect(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        last = None
        for i, (k, head, s, _) in enumerate(res):
            if head != last:
                f.write("\n## " + head + "\n"); last = head
            f.write(f"{i:03d} [{k}] {s}\n")
    print(len(res), "формул;", sum(1 for r in res if r[0] == "omml"), "уже OMML")
