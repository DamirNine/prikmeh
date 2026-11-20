# -*- coding: utf-8 -*-
"""РПЗ: в Word обновить содержание и поля, сохранить docx и PDF.  python to_pdf.py"""
import os, sys
import win32com.client as w
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "РПЗ_укупориватель.docx")
app = w.DispatchEx("Word.Application"); app.Visible = False; app.DisplayAlerts = 0
try:
    d = app.Documents.Open(src, False, False)
    for i in range(1, d.TablesOfContents.Count + 1):
        d.TablesOfContents(i).Update()
    d.Fields.Update()
    d.Save()
    print("страниц:", d.ComputeStatistics(2))
    d.ExportAsFixedFormat(src[:-5] + ".pdf", 17)
    d.Close(0)
finally:
    app.Quit()
