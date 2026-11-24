# -*- coding: utf-8 -*-
"""Вариант Б (Корнеев 24.11 12:12 — «два варианта РПЗ»): проверка штока и опоры при направляющей без планок — вставка в конец п. 8.5
(перед «8.6.»). Реакция R30 = 1671 Н на полке, середина полки на h = 11,14 + 46,75 = 57,9 мм ниже D (φу). Запуск после rpz_kin_insert.py."""
import os, win32com.client
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "Вариант Б направляющей (без планок)."
BLOCKS = [("t", MARK + " Реакцию направляющей воспринимает полка, её середина на h = 57,9 мм ниже пальца D (при φу), поэтому шток работает ещё и на изгиб:"),
          ("m", "M=R_30^N·h=1671·57,9=96,7·10^3 Н·мм,  W=(π d^3)/32=50,3 мм^3"),
          ("m", "σ=M/W=1924 МПа>[σ]=98 МПа"),
          ("t", "Условие прочности для штока Ø8 не выполняется; по изгибу со сжатием требуется диаметр не менее 22 мм (Ст3сп). Среднее давление в отверстии полки толщиной 6 мм:"),
          ("m", "p=R_30^N/(d·s)=1671/(8·6)=34,8 МПа>[p]=24 МПа"),
          ("t", "Проверка 3–0 в таблице 13 (p = 2,6 МПа) относится к направляющей с планками.")]
w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
try:
    doc = w.Documents.Open(os.path.join(HERE, "РПЗ_укупориватель.docx"), AddToRecentFiles=False)
    paras = doc.Paragraphs
    body = eq = anchor = None
    for i in range(1, paras.Count + 1):
        p = paras(i); t = p.Range.Text
        assert not t.startswith(MARK), "уже вставлено"
        if t.startswith("Максимальная угловая скорость"): body = p
        if eq is None and t.startswith("6.2. Угловая скорость"): eq = paras(i + 1)
        if t.startswith("8.6. Кинематические пары") and p.Range.Style.NameLocal.lower().find("toc") < 0 and body is not None:
            anchor = paras(i - 1); break
    assert body is not None and eq is not None and anchor is not None
    font = body.Range.Characters(1).Font
    for kind, txt in BLOCKS:
        anchor.Range.InsertParagraphAfter(); p = anchor.Next()
        src = body if kind == "t" else eq
        p.Style = src.Style; p.Format = src.Format
        r = p.Range; r.MoveEnd(1, -1); r.Text = txt; r.Font = font
        if kind == "m":
            r.OMaths.Add(r); p.Range.OMaths(1).BuildUp()
        anchor = p
    doc.Save(); print("вариант Б: вставлено абзацев", len(BLOCKS)); doc.Close(0)
finally:
    w.Quit()
