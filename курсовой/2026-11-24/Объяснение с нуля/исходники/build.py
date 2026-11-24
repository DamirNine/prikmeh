# -*- coding: utf-8 -*-
"""Сборка «Объяснение с нуля»: docx + pdf (Word). Содержание — обычный текст с настоящими номерами страниц: первый проход
меряет страницы заголовков Word'ом, второй подставляет.      python figs.py && python build.py"""
import json, os, sys
import win32com.client
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor
import lib, part1, part2, part3

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..")
KURS = os.path.join(HERE, "..", "..", "..")
FIG = os.path.join(KURS, "2026-11-23", "Презентация", "fig")
MEDIA = os.path.join(KURS, "2026-11-23", "РПЗ", "_media")
DOCX = os.path.abspath(os.path.join(OUT, "Объяснение укупоривателя с нуля.docx"))
G = lambda n: os.path.join(OUT, "рисунки", n)
EXT = {"РПЗ_камень": os.path.join(MEDIA, "image24_мкэ.png"),
       "схемы_первичный.png": os.path.join(KURS, "2026-11-23", "fbd", "fig7_fbd_v24.png")}
from PIL import Image
_k = Image.open(os.path.join(FIG, "ползун_кинематика.png")).convert("RGB")       # без строки «увеличен на рисунке …»: она про РПЗ
_k = _k.crop((0, int(_k.height * 0.045), _k.width, _k.height)); _k.save(os.path.join(OUT, "рисунки", "ползун_кинематика.png"))
EXT["ползун_кинематика.png"] = os.path.join(OUT, "рисунки", "ползун_кинематика.png")
def R(n):
    return EXT.get(n) or os.path.join(FIG, n if n.endswith(".png") else n + ".png")


def make(pages, entries):
    D = lib.Doc(pages)
    for t, sz, sp in (("Ручной укупориватель бутылок", 30, 150), ("Как мы его рассчитали: объяснение с нуля", 18, 6)):
        p = D.d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(sp)
        r = p.add_run(t); r.bold = True; r.font.size = Pt(sz); r.font.color.rgb = lib.NAVY
    p = D.d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(18); p.paragraph_format.space_after = Pt(24)
    r = p.add_run("Для тех, кто не изучал прикладную механику:\nкаждый шаг, каждая формула и каждый термин"); r.font.size = Pt(13); r.font.color.rgb = lib.GREY
    p = D.d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(R("01_без_кожуха"), height=Cm(10.5))
    p = D.d.add_paragraph("Содержание"); p.paragraph_format.page_break_before = True
    p.runs[0].bold = True; p.runs[0].font.size = Pt(20); p.runs[0].font.color.rgb = lib.NAVY
    D.toc(entries)
    for m in (part1, part2, part3): m.build(D, G, R)
    D.d.core_properties.title = "Ручной укупориватель: объяснение с нуля"; D.d.core_properties.author = ""
    D.d.save(DOCX)
    return D.heads


heads = make({}, [])
entries = heads
w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
try:
    pages = {}
    for k in range(2):                                # второй проход — с содержанием нужной длины
        make(pages, [(1, t) if lv == 1 else (lv, t) for lv, t in entries])
        doc = w.Documents.Open(DOCX, AddToRecentFiles=False)
        want = {t for _, t in entries}; pages = {}
        for p in doc.Paragraphs:
            if p.OutlineLevel in (1, 2):
                t = p.Range.Text.strip()
                if t in want: pages[t] = p.Range.Information(3)
        doc.Close(0)
        assert set(pages) == want, want - set(pages)
    make(pages, entries)
    doc = w.Documents.Open(DOCX, AddToRecentFiles=False)
    chk = {p.Range.Text.strip(): p.Range.Information(3) for p in doc.Paragraphs if p.OutlineLevel in (1, 2)}
    assert all(chk[t] == n for t, n in pages.items()), [(t, n, chk[t]) for t, n in pages.items() if chk[t] != n]
    doc.ExportAsFixedFormat(DOCX[:-5] + ".pdf", 17)
    print("страниц:", doc.ComputeStatistics(2), "заголовков в содержании:", len(entries))
    doc.Close(0)
finally:
    w.Quit()
