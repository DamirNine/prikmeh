# -*- coding: utf-8 -*-
"""LaTeX → MathML (latex2mathml) → OMML (MML2OMML.XSL из Office) → абзац Word с формулой.
Десятичная запятая: 1,05 в LaTeX пишется как есть — соседние mn и запятая склеиваются в одно число."""
import copy, re
import latex2mathml.converter as L2M
from lxml import etree
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

XSL = etree.XSLT(etree.parse(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"))
MNS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MMLNS = "http://www.w3.org/1998/Math/MathML"


FUNCS = {"cos", "sin", "tg", "ln", "arctg", "tan", "arctan", "max", "min"}
SPACES = {"1em": " ", "2em": "  ", "0.167em": " ", "0.222em": " ", "0.278em": " "}
UPRIGHT = set("ΓΔΘΛΞΠΣΥΦΨΩФ")


def _fix_mathml(mml):
    t = etree.fromstring(mml.encode("utf-8"))
    mi_tag, mo_tag = "{%s}mi" % MMLNS, "{%s}mo" % MMLNS
    # пробелы \quad, \, и т. п. → символы пробела (mspace конвертер в OMML теряет)
    for sp in list(t.iter("{%s}mspace" % MMLNS)):
        w = sp.get("width", "")
        txt = etree.Element("{%s}mtext" % MMLNS); txt.text = SPACES.get(w, " "); txt.tail = sp.tail
        sp.getparent().replace(sp, txt)
    # \operatorname{tg} даёт <mo>tg</mo> — делаем обычным именем функции
    for mo in list(t.iter(mo_tag)):
        if mo.text in FUNCS:
            mo.tag = mi_tag
            for a in list(mo.attrib):
                del mo.attrib[a]
    # матрица: ( mtable ) → mfenced, иначе конвертер путает пары скобок
    for tb in list(t.iter("{%s}mtable" % MMLNS)):
        pv, nx = tb.getprevious(), tb.getnext()
        if pv is not None and nx is not None and pv.tag == nx.tag == mo_tag and (pv.text, nx.text) in (("(", ")"), ("[", "]")):
            fe = etree.Element("{%s}mfenced" % MMLNS); fe.set("open", pv.text); fe.set("close", nx.text); fe.set("separators", "")
            fe.tail = nx.tail
            par = tb.getparent(); par.replace(pv, fe); par.remove(nx); fe.append(tb)
    # cos φ, sin φ … — функция с аргументом: знак применения функции после имени (после степени, если cos³),
    # тонкий пробел перед именем, если перед ним множитель
    SCR = {"{%s}%s" % (MMLNS, k) for k in ("msup", "msub", "msubsup")}
    for mi in list(t.iter(mi_tag)):
        if mi.text in FUNCS:
            mi.set("mathvariant", "normal")
            base = mi.getparent() if (mi.getparent().tag in SCR and mi.getparent().index(mi) == 0) else mi
            nxt = base.getnext()
            if nxt is not None and not (nxt.tag == mo_tag and nxt.text == "⁡"):
                ap = etree.Element(mo_tag); ap.text = "⁡"; ap.tail = base.tail; base.tail = None
                base.addnext(ap)
            pv = base.getprevious()
            if pv is not None and (pv.tag in ({mi_tag, "{%s}mn" % MMLNS} | SCR) or (pv.tag == mo_tag and pv.text == ")")):
                sp = etree.Element("{%s}mtext" % MMLNS); sp.text = " "
                base.addprevious(sp)
        elif mi.text and len(mi.text) == 1 and mi.text in UPRIGHT:
            mi.set("mathvariant", "normal")
    # склейка 1 , 05 → 1,05 и 17 300 (через \,) не трогаем
    changed = True
    while changed:
        changed = False
        for mo in t.iter("{%s}mo" % MMLNS):
            if mo.text != ",":
                continue
            prev, nxt = mo.getprevious(), mo.getnext()
            if prev is not None and nxt is not None and prev.tag == nxt.tag == "{%s}mn" % MMLNS:
                prev.text = prev.text + "," + nxt.text
                par = mo.getparent(); par.remove(mo); par.remove(nxt)
                changed = True
                break
    return t


def latex_to_omath(tex, sz=28):
    mml = L2M.convert(tex)
    om = XSL(_fix_mathml(mml)).getroot()
    if om.tag != "{%s}oMath" % MNS:
        om = om.find(".//{%s}oMath" % MNS)
    # система с фигурной скобкой (cases): столбцы — по левому краю
    m = lambda tag: "{%s}%s" % (MNS, tag)
    for d in om.iter(m("d")):
        beg = d.find(m("dPr") + "/" + m("begChr"))
        if beg is None or beg.get(m("val")) != "{":
            continue
        for mat in d.iter(m("m")):
            ncol = max(len(r.findall(m("e"))) for r in mat.findall(m("mr")))
            mpr = mat.find(m("mPr"))
            if mpr is None:
                mpr = etree.Element(m("mPr")); mat.insert(0, mpr)
            for old in mpr.findall(m("mcs")):
                mpr.remove(old)
            mcs = etree.SubElement(mpr, m("mcs")); mc = etree.SubElement(mcs, m("mc")); mcpr = etree.SubElement(mc, m("mcPr"))
            etree.SubElement(mcpr, m("count")).set(m("val"), str(ncol))
            etree.SubElement(mcpr, m("mcJc")).set(m("val"), "left")
    for r in om.iter("{%s}r" % MNS):
        rpr = etree.SubElement(r, "{%s}rPr" % WNS)
        f = etree.SubElement(rpr, "{%s}rFonts" % WNS)
        for a in ("ascii", "hAnsi", "eastAsia", "cs"):
            f.set("{%s}%s" % (WNS, a), "Cambria Math")
        etree.SubElement(rpr, "{%s}sz" % WNS).set("{%s}val" % WNS, str(sz))
        etree.SubElement(rpr, "{%s}szCs" % WNS).set("{%s}val" % WNS, str(sz))
        # порядок в m:r: m:rPr, w:rPr, m:t
        mrpr = r.find("{%s}rPr" % MNS)
        r.remove(rpr)
        r.insert(1 if mrpr is not None else 0, rpr)
    return om


def math_paragraph(tex, sz=28, keep_next=False, before=80, after=80):
    om = latex_to_omath(tex, sz)
    kn = "<w:keepNext/>" if keep_next else ""
    p = parse_xml(f'<w:p {nsdecls("w")}><w:pPr>{kn}<w:spacing w:before="{before}" w:after="{after}"/><w:jc w:val="center"/></w:pPr></w:p>')
    para = etree.SubElement(p, "{%s}oMathPara" % MNS)
    ppr = etree.SubElement(para, "{%s}oMathParaPr" % MNS)
    etree.SubElement(ppr, "{%s}jc" % MNS).set("{%s}val" % MNS, "center")
    para.append(om)
    return p


def replace_with_math(p, tex, sz=28):
    """заменить содержимое абзаца формулой, сохранив его свойства (keepNext, отступы)"""
    new = math_paragraph(tex, sz)
    ppr_old = p.find(qn("w:pPr"))
    for ch in list(p):
        if ch is not ppr_old:
            p.remove(ch)
    if ppr_old is not None:
        jc = ppr_old.find(qn("w:jc"))
        if jc is None:
            jc = etree.Element(qn("w:jc"))
            rpr = ppr_old.find(qn("w:rPr"))
            if rpr is not None:
                rpr.addprevious(jc)
            else:
                ppr_old.append(jc)
        jc.set(qn("w:val"), "center")
    for ch in list(new):
        if ch.tag != qn("w:pPr"):
            p.append(ch)
    return p
