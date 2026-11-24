# -*- coding: utf-8 -*-
r"""Движок документа «Объяснение с нуля»: python-docx + формулы Word (OMML) из короткой записи.
Запись формул: _{} ^{} \frac{}{} \sqrt{} \vec{} \p{} (скобки) \abs{} \int_{a}^{b} \sum_{a}^{b} \cases{a;;b;;c} \t{прямой текст},
функции \cos \sin \tg \ln \arctg \max \min; греческие буквы и знаки — обычными символами. В тексте: $формула$, **жирный**."""
import os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from xml.sax.saxutils import escape

MNS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
NAVY, GREY = RGBColor(0x1F, 0x38, 0x64), RGBColor(0x55, 0x55, 0x55)
FUNCS = {"cos", "sin", "tg", "ln", "arctg", "max", "min"}
SPACE = {"quad": " ", "q": "  "}


# ---------------------------------------------------------------- короткая запись → OMML
def run(t, upright):
    sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else ""
    return (f'<m:r>{sty}<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math" w:cs="Cambria Math"/></w:rPr>'
            f'<m:t xml:space="preserve">{escape(t)}</m:t></m:r>')


def group(s, i):
    assert s[i] == "{", (s, i)
    d, j = 0, i
    while True:
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
        j += 1


def seq(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        nary = None
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:]); name = m.group(1); i += len(m.group(0))
            if name == "frac":
                a, i = group(s, i); b, i = group(s, i)
                base = f"<m:f><m:num>{seq(a)}</m:num><m:den>{seq(b)}</m:den></m:f>"
            elif name == "sqrt":
                a, i = group(s, i)
                base = f'<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>{seq(a)}</m:e></m:rad>'
            elif name == "vec":
                a, i = group(s, i)
                base = f'<m:acc><m:accPr><m:chr m:val="&#x20D7;"/></m:accPr><m:e>{seq(a)}</m:e></m:acc>'
            elif name in ("p", "abs", "br"):
                a, i = group(s, i); l, r = {"p": "()", "abs": "||", "br": "[]"}[name]
                base = f'<m:d><m:dPr><m:begChr m:val="{l}"/><m:endChr m:val="{r}"/></m:dPr><m:e>{seq(a)}</m:e></m:d>'
            elif name == "cases":
                a, i = group(s, i)
                rows = "".join(f"<m:e>{seq(x.strip())}</m:e>" for x in a.split(";;"))
                base = f'<m:d><m:dPr><m:begChr m:val="{{"/><m:endChr m:val=""/></m:dPr><m:e><m:eqArr>{rows}</m:eqArr></m:e></m:d>'
            elif name == "t":
                a, i = group(s, i); base = run(a, True)
            elif name in ("int", "sum"):
                nary = "∫" if name == "int" else "∑"; base = ""
            elif name in FUNCS:
                base = run(name + " ", True) if not (i < len(s) and s[i] in "^_") else run(name, True)
            elif name in SPACE:
                base = run(SPACE[name], True)
            else:
                raise ValueError(name)
        elif c == "{":
            a, i = group(s, i); base = seq(a)
        else:
            if c.isalpha() and not ("а" <= c.lower() <= "я" or c == "ё"):
                base = run(c, False); i += 1
            else:                                              # цифры, знаки, кириллица — подряд одним прямым прогоном
                m = re.match(r"[0-9.,]+|[А-Яа-яЁё]+|.", s[i:], re.S)
                base = run(m.group(0), True); i += len(m.group(0))
        sub = sup = None
        while i < len(s) and s[i] in "_^":
            k = s[i]; i += 1
            if s[i] == "{": a, i = group(s, i)
            else: a, i = s[i], i + 1
            if k == "_": sub = a
            else: sup = a
        if nary:
            base = (f'<m:nary><m:naryPr><m:chr m:val="{nary}"/><m:limLoc m:val="{"subSup" if nary == "∫" else "undOvr"}"/>'
                    f'{"" if sub else "<m:subHide m:val=%s1%s/>" % (chr(34), chr(34))}{"" if sup else "<m:supHide m:val=%s1%s/>" % (chr(34), chr(34))}</m:naryPr>'
                    f'<m:sub>{seq(sub or "")}</m:sub><m:sup>{seq(sup or "")}</m:sup><m:e>')
            rest = seq(s[i:]); return "".join(out) + base + rest + "</m:e></m:nary>"
        if sub is not None and sup is not None:
            base = f"<m:sSubSup><m:e>{base}</m:e><m:sub>{seq(sub)}</m:sub><m:sup>{seq(sup)}</m:sup></m:sSubSup>"
        elif sub is not None:
            base = f"<m:sSub><m:e>{base}</m:e><m:sub>{seq(sub)}</m:sub></m:sSub>"
        elif sup is not None:
            base = f"<m:sSup><m:e>{base}</m:e><m:sup>{seq(sup)}</m:sup></m:sSup>"
        out.append(base)
    return "".join(out)


def omath(s):
    return parse_xml(f"<m:oMath {MNS}>{seq(s)}</m:oMath>")


def omath_para(s):
    return parse_xml(f'<m:oMathPara {MNS}><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr><m:oMath>{seq(s)}</m:oMath></m:oMathPara>')


# ---------------------------------------------------------------- документ
class Doc:
    def __init__(self, toc_pages=None):
        self.d = Document()
        s = self.d.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin, s.right_margin, s.top_margin, s.bottom_margin = Cm(2.2), Cm(2.0), Cm(2.0), Cm(2.0)
        n = self.d.styles["Normal"]
        n.font.name, n.font.size = "Calibri", Pt(11.5)
        n.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        n.paragraph_format.space_after, n.paragraph_format.line_spacing = Pt(6), 1.12
        for lv, sz, bf, af in ((1, 20, 0, 10), (2, 14.5, 14, 5), (3, 12.5, 10, 4)):
            h = self.d.styles[f"Heading {lv}"]
            h.font.name, h.font.size, h.font.bold, h.font.italic = "Calibri", Pt(sz), True, False
            h.font.color.rgb = NAVY
            h.element.rPr.rFonts.set(qn("w:ascii"), "Calibri"); h.element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                h.element.rPr.rFonts.attrib.pop(qn(a), None)
            h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(bf), Pt(af)
            h.paragraph_format.keep_with_next = True
        self.heads, self.toc_pages, self.fig, self.num1 = [], toc_pages or {}, 0, 0
        self._footer()

    def _footer(self):
        p = self.d.sections[0].footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for t, x in (("begin", None), (None, "PAGE"), ("end", None)):
            r = p.add_run()
            if t:
                e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
            else:
                e = OxmlElement("w:instrText"); e.text = x; r._r.append(e)
        self.d.sections[0].different_first_page_header_footer = True

    # текст с $формулами$ и **жирным**
    def rich(self, p, text, size=None, color=None, bold=False, italic=False):
        if re.fullmatch(r"\$[^$]+\$", text): p.add_run("​")      # одиночная формула в ячейке — в строку, а не по центру
        for part in re.split(r"(\$[^$]+\$|\*\*[^*]+\*\*)", text):
            if not part: continue
            if part[0] == "$":
                p._p.append(omath(part[1:-1])); continue
            b = part.startswith("**")
            r = p.add_run(part[2:-2] if b else part)
            r.bold = True if (b or bold) else None
            r.italic = True if italic else None
            if size: r.font.size = Pt(size)
            if color is not None: r.font.color.rgb = color
        return p

    def h1(self, t, brk=True):
        p = self.d.add_heading(t, 1)
        if brk: p.paragraph_format.page_break_before = True
        self.heads.append((1, t))

    def h2(self, t):
        self.d.add_heading(t, 2); self.heads.append((2, t))

    def h3(self, t):
        self.d.add_heading(t, 3)

    def p(self, t, **k):
        q = self.rich(self.d.add_paragraph(), t, **k)
        if t.rstrip().endswith((':', ', то')): q.paragraph_format.keep_with_next = True
        return q

    def ul(self, items, style="List Bullet"):
        for t in items:
            p = self.d.add_paragraph(style=style); p.paragraph_format.space_after = Pt(3); self.rich(p, t)

    def ol(self, items):
        for i, t in enumerate(items, 1):
            p = self.d.add_paragraph(); p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Cm(0.9), Cm(-0.7)
            p.paragraph_format.space_after = Pt(3); self.rich(p, f"{i}.  " + t)

    def f(self, *tex):
        for t in tex:
            p = self.d.add_paragraph(); p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(4), Pt(6)
            p.paragraph_format.keep_with_next = True
            p._p.append(omath_para(t))

    def _shade(self, cell, color):
        e = OxmlElement("w:shd"); e.set(qn("w:val"), "clear"); e.set(qn("w:color"), "auto"); e.set(qn("w:fill"), color)
        cell._tc.get_or_add_tcPr().append(e)

    def _borders(self, tbl, color="BFC5CE", inside=True):
        pr = tbl._tbl.tblPr; b = OxmlElement("w:tblBorders")
        for n in ("top", "left", "bottom", "right") + (("insideH", "insideV") if inside else ()):
            e = OxmlElement(f"w:{n}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), color); b.append(e)
        pr.append(b)

    def table(self, head, rows, widths, size=10, caption=None):
        if caption:
            c = self.d.add_paragraph(); c.paragraph_format.keep_with_next = True; c.paragraph_format.space_after = Pt(3)
            self.rich(c, caption, size=10, color=GREY, bold=True)
        t = self.d.add_table(rows=1 if head else 0, cols=len(widths)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
        self._borders(t)
        if head:
            for c, x in zip(t.rows[0].cells, head):
                self._shade(c, "E3E8F1"); pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(1); self.rich(pp, x, size=size, bold=True)
            trp = t.rows[0]._tr.get_or_add_trPr(); e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); trp.append(e)
        for r in rows:
            row = t.add_row()
            e = OxmlElement("w:cantSplit"); e.set(qn("w:val"), "true"); row._tr.get_or_add_trPr().append(e)
            for c, x in zip(row.cells, r):
                pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(1); pp.paragraph_format.line_spacing = 1.0; self.rich(pp, x, size=size)
        for row in t.rows:
            for c, w in zip(row.cells, widths): c.width = Cm(w)
        if len(rows) <= 14:                                     # небольшую таблицу не рвать между страницами
            for row in t.rows[:-1]:
                for c in row.cells:
                    for pp in c.paragraphs: pp.paragraph_format.keep_with_next = True
        for w, gc in zip(widths, t._tbl.tblGrid.findall(qn("w:gridCol"))): gc.set(qn("w:w"), str(int(w * 567)))
        g = self.d.add_paragraph(); g.paragraph_format.space_after = Pt(4); g.paragraph_format.line_spacing = 0.7
        return t

    def where(self, rows):
        """расшифровка формулы: (обозначение, что это, у нас)"""
        self.table(["Знак", "Что это", "У нас"], rows, [2.2, 10.4, 4.2], size=10)

    def box(self, kind, *paras):
        color, bar = {"Простыми словами": ("EAF2FB", "2F6FB5"), "Термин": ("F3F0FA", "6B4FA0"), "У нас": ("EEF6EC", "3F8F4F"),
                      "Зачем это нужно": ("FFF6E5", "C98A1B"), "Частая ошибка": ("FCECEC", "B83A3A"), "Вопрос": ("F1F3F5", "55606E")}[kind.split(":")[0]]
        t = self.d.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
        c = t.rows[0].cells[0]; c.width = Cm(16.8); self._shade(c, color)
        e = OxmlElement("w:cantSplit"); e.set(qn("w:val"), "true"); t.rows[0]._tr.get_or_add_trPr().append(e)
        b = OxmlElement("w:tcBorders"); l = OxmlElement("w:left")
        for k, v in (("val", "single"), ("sz", "24"), ("color", bar)): l.set(qn(f"w:{k}"), v)
        b.append(l); c._tc.get_or_add_tcPr().append(b)
        for i, x in enumerate(paras):
            p = c.paragraphs[0] if i == 0 else c.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            if i == 0: self.rich(p, kind + (" " if kind.endswith("?") else ". "), bold=True, color=RGBColor.from_string(bar), size=11)
            self.rich(p, x, size=11)
        g = self.d.add_paragraph(); g.paragraph_format.space_after = Pt(4); g.paragraph_format.line_spacing = 0.7

    def img(self, path, w, caption, maxh=None):
        from PIL import Image
        iw, ih = Image.open(path).size
        if maxh and w * ih / iw > maxh: w = maxh * iw / ih
        p = self.d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(path, width=Cm(w))
        self.d.inline_shapes[-1]._inline.docPr.set("descr", caption)
        self.fig += 1
        c = self.d.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self.rich(c, f"Рисунок {self.fig}. {caption}", size=10, color=GREY)

    def toc(self, entries):
        for lv, t in entries:
            p = self.d.add_paragraph(); p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.left_indent = Cm(0 if lv == 1 else 0.8)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(16.6), 2, 1)        # вправо, с точками
            p.add_run(t + "\t" + str(self.toc_pages.get(t, "")))
