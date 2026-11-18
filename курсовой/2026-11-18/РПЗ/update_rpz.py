# -*- coding: utf-8 -*-
"""Word: обновить оглавление и поля, вписать число листов в задание, сохранить и выгрузить PDF.
    python update_rpz.py"""
import os, sys
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "РПЗ_укупориватель.docx")
PDF = os.path.join(HERE, "РПЗ_укупориватель.pdf")
w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
d = w.Documents.Open(DOCX)
try:
    d.Fields.Update(); d.TablesOfContents(1).Update(); d.Repaginate()
    n = d.ComputeStatistics(2)                                  # страниц
    f = d.Content.Find
    f.ClearFormatting(); f.Replacement.ClearFormatting()
    # Execute(FindText, MatchCase, MatchWholeWord, MatchWildcards, MatchSoundsLike, MatchAllWordForms, Forward, Wrap, Format,
    #         ReplaceWith, Replace) — именованные аргументы через COM не срабатывают
    ok = f.Execute("___ листах", False, False, False, False, False, True, 1, False, f"{n} листах", 2)
    print("число листов вписано:", ok)
    d.TablesOfContents(1).Update()
    d.Save()
    d.ExportAsFixedFormat(PDF, 17)
    print("страниц:", n, "→", PDF)
finally:
    d.Close(0); w.Quit()
