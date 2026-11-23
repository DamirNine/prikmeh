# -*- coding: utf-8 -*-
"""После edit_rpz23.py: обновить поле содержания (TOC/PAGEREF) отдельным экземпляром Word, сохранить docx и выгрузить
_check.pdf. Без этого в docx остаются старые номера страниц содержания (в PDF Word обновляет их сам).
    python finalize_rpz.py"""
import os, win32com.client
HERE = os.path.dirname(os.path.abspath(__file__))
w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
try:
    doc = w.Documents.Open(os.path.join(HERE, "РПЗ_укупориватель.docx"), AddToRecentFiles=False)
    for i in range(1, doc.TablesOfContents.Count + 1):
        doc.TablesOfContents(i).UpdatePageNumbers()
    doc.Save()
    doc.ExportAsFixedFormat(os.path.join(HERE, "_check.pdf"), 17)
    print("страниц:", doc.ComputeStatistics(2), "содержаний обновлено:", doc.TablesOfContents.Count)
    doc.Close(0)
finally:
    w.Quit()
