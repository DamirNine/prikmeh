# -*- coding: utf-8 -*-
"""Корнеев 24.11 01:29: «где у нас формулы для координаты, скорости и ускорения ползуна, каким образом мы построили
графики». В начало п. 6.3 вставляются формулы, по которым построены рисунки 7–8 и таблица 6: φ(t) по закону движения,
y_D, V_Dy, a_Dy через аналоги п. 3.3 и конец рукояти K. Формулы — объекты Word (линейная запись → BuildUp).
Запуск после edit_rpz23.py и перед finalize_rpz.py:  python rpz_kin_insert.py"""
import os, win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "Графики на рисунках 7 и 8 и значения таблицы 6 получены так."
NB = "▒"                                   # разделитель n-арного оператора в линейной записи Word
BLOCKS = [
    ("t", MARK + " Модуль угловой скорости ω и его производная ε заданы законом движения (п. 6.1–6.2); угол кулисы "
          "убывает от φн до φк:"),
    ("m", f"φ(t)=φ_н-∫_0^t{NB}〖ω dt〗"),
    ("t", "Координата, скорость и ускорение ползуна — через аналоги п. 3.3 (q = φн − φ, dq/dt = ω):"),
    ("m", "y_D=e·\"tg\" φ,  V_Dy=V_qDy·ω=-(e ω)/(\"cos\"^2 φ)"),
    ("m", "a_Dy=a_qDy·ω^2+V_qDy·ε=(2e ω^2 \"sin\" φ)/(\"cos\"^3 φ)-(e ε)/(\"cos\"^2 φ)"),
    ("t", "Конец рукояти K движется по окружности радиуса L:"),
    ("m", "V_K=ω L,  a_τK=ε L,  a_nK=ω^2 L"),
]

w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
try:
    doc = w.Documents.Open(os.path.join(HERE, "РПЗ_укупориватель.docx"), AddToRecentFiles=False)
    paras = doc.Paragraphs
    head = body = eq = None
    for i in range(1, paras.Count + 1):
        p = paras(i)
        t = p.Range.Text
        if t.startswith(MARK):
            raise SystemExit("уже вставлено")
        if t.startswith("Максимальная угловая скорость"):
            body = p                                   # образец обычного абзаца (п. 6.2)
        if eq is None and t.startswith("6.2. Угловая скорость"):
            eq = paras(i + 1)                          # образец абзаца с формулой (ω_max = v_max / L)
        if t.startswith("6.3. Скорости и ускорения точек"):
            head = p
            break
    assert head and body and eq and eq.Range.OMaths.Count == 1, (head, body, eq)
    anchor = head
    for kind, txt in BLOCKS:
        anchor.Range.InsertParagraphAfter()
        p = anchor.Next()
        src = body if kind == "t" else eq
        p.Style = src.Style
        p.Format = src.Format
        r = p.Range
        r.MoveEnd(1, -1)                               # без знака абзаца
        r.Text = txt
        r.Font = body.Range.Characters(1).Font
        if kind == "m":
            r.OMaths.Add(r)
            p.Range.OMaths(1).BuildUp()
        anchor = p
    doc.Save()
    print("вставлено абзацев:", len(BLOCKS))
    doc.Close(0)
finally:
    w.Quit()
