# -*- coding: utf-8 -*-
"""п. 3.2 РПЗ (Корнеев 24.11 00:14): «векторный контур записан не в векторном виде и у y нет индекса D» —
формулы-объекты Word (OMML): l_OD = e + y → вектора l⃗_OD = e⃗ + y⃗_D; «= y» → y_D; «y = e·tg φ» → y_D = e·tg φ."""
import copy
from lxml import etree
MNS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
M = "{%s}" % MNS


def _mt(el):
    return [t.text for t in el.iter(M + "t")]


def fix_contour(doc):
    eq = [p for p in doc.paragraphs if _mt(p._p) == ["l", "OD", "=e+y"]]
    eq2 = [p for p in doc.paragraphs if _mt(p._p)[-1:] == ["\u2061φ=y"] and "x:" in _mt(p._p)]
    eq3 = [p for p in doc.paragraphs if _mt(p._p)[:1] == ["y=e·"]]
    assert len(eq) == len(eq2) == len(eq3) == 1, (len(eq), len(eq2), len(eq3))
    # 1) векторная запись
    om = eq[0]._p.find(".//" + M + "oMath")
    ssub = om.find(M + "sSub")                       # l_OD
    r_tail = om.find(M + "r")                       # «=e+y»
    def mr(text):
        r = copy.deepcopy(r_tail); r.find(M + "t").text = text; return r
    def sub(base, s):
        x = copy.deepcopy(ssub); ts = list(x.iter(M + "t")); ts[0].text = base; ts[1].text = s; return x
    def vec(child):
        acc = etree.Element(M + "acc"); pr = etree.SubElement(acc, M + "accPr")
        etree.SubElement(pr, M + "chr").set(M + "val", "\u20d7")
        e = etree.SubElement(acc, M + "e"); e.append(child); return acc
    for ch in list(om):
        om.remove(ch)
    for el in (vec(sub("l", "OD")), mr("="), vec(mr("e")), mr("+"), vec(sub("y", "D"))):
        om.append(el)
    # 2) «… sin φ = y» → «… = y_D»
    t_last = [t for t in eq2[0]._p.iter(M + "t")][-1]
    t_last.text = "\u2061φ="
    t_last.getparent().addnext(sub("y", "D"))
    # 3) «y = e·tg φ» → «y_D = e·tg φ»
    t_first = [t for t in eq3[0]._p.iter(M + "t")][0]
    t_first.text = "=e·"
    t_first.getparent().addprevious(sub("y", "D"))
    print("  п. 3.2: векторный контур, y_D —", ["".join(_mt(p._p)) for p in (eq[0], eq2[0], eq3[0])])
