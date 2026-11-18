# -*- coding: utf-8 -*-
"""РПЗ к курсовому проекту по образцу курсовой/примеры/РПЗ.pdf (титул, задание, подписи, содержание, разделы расчёта,
3D-модели, МКЭ, прототип, заключение, источники) — на основе расчётной записки v30 (формулы, схемы, графики, таблицы
сохраняются как есть; убраны пояснения обозначений, «выводы»-пересказы, обсуждение источников, допущения и приложение А).
Поля, которые заполняет бригада (состав, руководитель), выделены жёлтым.
    python build_rpz.py   → РПЗ_укупориватель.docx (затем update_rpz.py: оглавление и PDF через Word)"""
import copy, os, re, sys
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
OUT = os.path.join(HERE, "РПЗ_укупориватель.docx")
GROUP, YEAR = "РК6-55Б", "2026"
STUDENTS = ["Броцман Р.А.", "Девяткин Д.А.", "Калугин С.А.", "Корнеев А.Е.", "Салихова Е.Д."]   # бригада №2 (как в 4 семестре)
HEAD = ""                                              # руководитель — заполнить
TOPIC = "Проектирование и исследование тангенсного механизма ручного укупоривателя бутылки"

d = Document(os.path.join(HERE, "v30.docx"))
body = d.element.body
EL = [e for e in body.iterchildren() if not e.tag.endswith("sectPr")]
txt = lambda e: "".join(x.text or "" for x in e.iter(qn("w:t")))

# ---------------------------------------------------------------- что оставить из v30 (номера элементов тела, см. v30_map.txt)
R = lambda a, b: list(range(a, b + 1))
KEEP = set(
    [10, 11, 12] +                                                                       # исходные данные
    [14, 16, 24, 25, 26, 27, 28, 30, 31, 33, 34, 35, 37, 38, 40] +                        # усилие укупоривания
    [46, 47, 48, 49, 50, 52, 53, 54, 55, 56, 57, 58, 61, 63, 64, 65, 66, 67, 68, 70, 71, 72, 77, 78, 80] +
    [81, 88, 89, 91, 92, 93] +                                                            # сила руки, длина рукояти
    [101, 102] + R(103, 110) + [112, 113, 114, 115, 116, 118, 119, 120, 121, 125, 126, 127, 132, 133,
     136, 137, 138, 139, 141, 142, 144, 146, 149, 150, 151, 152, 156, 157] +               # синтез
    [162, 163, 164, 165, 168, 169, 171, 173, 174, 175, 177, 178, 179, 180, 192, 199] + R(201, 209) +
    [214, 215, 218, 225, 228, 229, 238, 239] +                                            # кинематика
    [243, 245, 246, 247, 250] + R(251, 260) + [265, 266, 272, 273, 282, 283] + R(285, 297) +
    [301, 302, 303, 304, 307] + R(308, 312) + [315, 316, 317] + R(319, 324) + [327, 328, 329, 331, 332, 334] +
    [337, 338] + R(339, 345) + [348, 349, 352, 353, 356, 357, 358, 359, 362, 363, 364, 367, 368, 369, 370, 371, 372,
     375, 376, 377, 378, 379, 380, 381] + R(383, 387) + [390, 393, 394, 396, 397, 399, 400, 402, 403, 405, 406] +
    R(407, 411) + [415, 416, 417, 422, 423, 424, 426] + R(427, 432) + [435, 437, 438, 439, 445, 446, 448,
     454, 455, 456, 457, 460, 461, 462] +                                                 # прочность
    [464, 466, 467, 468, 469, 470, 472, 473, 475, 477, 478, 480] + R(481, 487) + [490, 491, 492, 495, 496, 499,
     500, 501, 506, 507, 508, 509] + R(510, 519) + [522, 523] + R(527, 532) + [543, 544, 545, 546, 548, 549, 552,
     553, 562, 563, 564, 566, 567, 579, 580, 581, 584] +                                  # уточнённый расчёт
    [585, 586, 587] + R(601, 622))                                                        # параметры, источники
H1, H2 = "1", "21"
HEADS = {10: ("1 Исходные данные", H1), 14: ("2 Усилие укупоривания", H1), 46: ("3 Структура механизма и функция положения", H1),
         47: ("3.1 Структура механизма", H2), 54: ("3.2 Функция положения", H2), 61: ("3.3 Аналоги скоростей и ускорений", H2),
         77: ("3.4 Ход ползуна и угол давления", H2), 81: ("4 Сила руки и длина рукояти", H1),
         101: ("5 Синтез: выбор окна качания кулисы", H1), 102: ("5.1 Целевая функция", H2), 113: ("5.2 Ограничения", H2),
         118: ("5.3 Результаты оптимизации", H2), 136: ("5.4 Выбор варианта", H2),
         146: ("5.5 Приведение размеров к ГОСТ 6636-69", H2), 162: ("6 Кинематика механизма", H1),
         171: ("6.1 Закон движения кулисы", H2), 199: ("6.2 Угловая скорость и времена фаз", H2),
         225: ("6.3 Скорости и ускорения точек", H2), 243: ("7 Первичный силовой расчёт", H1),
         250: ("7.1 Закон силы обжима", H2), 272: ("7.2 Расчётные схемы и уравнения равновесия", H2),
         301: ("7.3 Матричная форма и решение", H2), 315: ("7.4 Длина рукояти и реакции", H2),
         337: ("8 Прочностной расчёт", H1), 338: ("8.1 Материалы и допускаемые напряжения", H2),
         356: ("8.2 Опасные положения", H2), 367: ("8.3 Эпюры внутренних силовых факторов кулисы", H2),
         380: ("8.4 Сечение кулисы", H2), 406: ("8.5 Шток ползуна: прочность и устойчивость", H2),
         426: ("8.6 Кинематические пары: срез и смятие", H2), 454: ("8.7 Массы звеньев", H2), 460: ("8.8 Итоги", H2),
         464: ("9 Уточняющий силовой расчёт", H1), 480: ("9.1 Угловая скорость и ускорение кулисы", H2),
         490: ("9.2 Силы инерции", H2), 509: ("9.3 Уравнения и решение", H2), 543: ("9.4 Результаты", H2),
         566: ("9.5 Проверка прочности", H2), 585: ("10 Принятые параметры механизма", H1),
         601: ("Список использованных источников", H1)}
SEC = {"3": "2", "3.1": "2", "3.3": "2", "4": "3", "4.1": "3.1", "4.2": "3.2", "4.3": "3.3", "4.4": "3.4", "5": "4",
       "5.1": "4", "5.2": "4", "6": "5", "6.1": "5.1", "6.2": "5.2", "6.3": "5.3", "6.4": "5.3", "6.5": "5.3", "6.6": "5.4",
       "7": "5.5", "7.1": "5.5", "7.2": "5.5", "8": "6", "9": "6", "9.1": "6.1", "9.2": "6.1", "9.3": "6.2", "10": "6.3",
       "11": "7", "11.2": "7.1", "11.3": "7.2", "11.4": "7.2", "11.5": "7.3", "11.6": "7.3", "11.7": "7.4", "12": "8",
       "12.1": "8.1", "12.2": "8.2", "12.3": "8.3", "12.4": "8.4", "12.5": "8.5", "12.6": "8.6", "12.7": "8.7", "12.8": "8.8",
       "13": "9", "13.1": "9", "13.2": "9.1", "13.3": "9.2", "13.4": "9.3", "13.5": "9.3", "13.6": "9.4", "13.7": "9.5",
       "14": "10"}
# вставки перед элементами v30 (короткие связки после удаления пояснений)
INS_BEFORE = {16: "Рабочее напряжение жести:"}

# ---------------------------------------------------------------- удаление, заголовки
for i, e in enumerate(EL):
    if i not in KEEP:
        body.remove(e)


def set_style(p, sid):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr"); p.insert(0, ppr)
    ps = ppr.find(qn("w:pStyle"))
    if ps is None:
        ps = OxmlElement("w:pStyle"); ppr.insert(0, ps)
    ps.set(qn("w:val"), sid)


def set_text(p, text):
    ts = list(p.iter(qn("w:t")))
    ts[0].text = text
    for t in ts[1:]:
        t.text = ""


for i, (t, sid) in HEADS.items():
    set_text(EL[i], t); set_style(EL[i], sid)
for i in KEEP:                                       # «Вывод. …», «Вывод для … . …» — без этих слов (и через границы прогонов)
    ts = list(EL[i].iter(qn("w:t")))
    m = re.match(r"^Вывод[^.]{0,40}\.\s*", "".join(t.text or "" for t in ts))
    if m:
        n = len(m.group(0))
        for t in ts:
            k = min(n, len(t.text or "")); t.text = (t.text or "")[k:]; n -= k
            if n == 0:
                break
        t1 = next(t for t in ts if t.text)
        t1.text = t1.text[:1].upper() + t1.text[1:]
for t in EL[584].iter(qn("w:t")):                    # ссылка на удалённое приложение А
    t.text = t.text.replace(" Ограничения для перегрузки и соединений — в приложении А.", "")
for tr in EL[12].iter(qn("w:tr")):                   # исходные данные — без столбца «Статус» (рабочие пометки)
    tr.remove(tr.findall(qn("w:tc"))[-1])
_g = EL[12].find(qn("w:tblGrid")); _g.remove(_g.findall(qn("w:gridCol"))[-1])

# ---------------------------------------------------------------- новые абзацы
def heading(text, level=1):
    """заголовок — копия абзаца-заголовка v30 (то же оформление), с новым текстом"""
    e = copy.deepcopy(EL[14] if level == 1 else EL[47])
    set_text(e, text)
    return e


def para(text="", style=None, align=None, bold=False, italic=False, size=None, hl=False, after=None, before=None, indent=True):
    p = d.add_paragraph()
    body.remove(p._p)
    if style:
        set_style(p._p, style)
    if align is not None:
        p.alignment = align
    if text:
        r = p.add_run(text); r.bold, r.italic = bold, italic
        if size: r.font.size = Pt(size)
        if hl: r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    pf = p.paragraph_format
    if after is not None: pf.space_after = Pt(after)
    if before is not None: pf.space_before = Pt(before)
    if not indent:
        pf.first_line_indent = Cm(0); pf.line_spacing = 1.0
    return p


def run(p, text, bold=False, size=None, hl=False, underline=False):
    r = p.add_run(text); r.bold = bold; r.underline = underline
    if size: r.font.size = Pt(size)
    if hl: r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return r


def page_break(p):
    p.add_run().add_break(WD_BREAK.PAGE)
    return p


def picture(path, width_cm, caption=None):
    p = para(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
    p.add_run().add_picture(path, width=Cm(width_cm))
    p.paragraph_format.keep_with_next = True
    out = [p]
    if caption:
        c = para(caption, style="af5", indent=False)
        out.append(c)
    return out


def table(rows, widths_cm, header=True):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    body.remove(t._tbl)
    t.style = d.tables[0].style
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths_cm[j])
            c.paragraphs[0].paragraph_format.first_line_indent = Cm(0)
            r = c.paragraphs[0].add_run(str(val)); r.font.size = Pt(12); r.bold = header and i == 0
    return t


SIG = lambda: "_________________"
front = []
# титул
p = para(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=0)
p.add_run().add_picture(os.path.join(FIG, "герб.png"), width=Cm(1.8)); front.append(p)
for t in ("Министерство науки и высшего образования Российской Федерации",
          "Федеральное государственное бюджетное образовательное учреждение высшего образования",
          "«Московский государственный технический университет имени Н.Э. Баумана",
          "(национальный исследовательский университет)»", "(МГТУ им. Н.Э. Баумана)"):
    front.append(para(t, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, after=0, indent=False))
front.append(para("", after=6))
front.append(para("ФАКУЛЬТЕТ «Робототехника и комплексная автоматизация»", size=12, after=0, indent=False))
front.append(para("КАФЕДРА РК-6 «Системы автоматизированного проектирования»", size=12, indent=False))
front.append(para("", after=10, indent=False))
front.append(para("РАСЧЁТНО-ПОЯСНИТЕЛЬНАЯ ЗАПИСКА", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=20, indent=False))
front.append(para("К КУРСОВОМУ ПРОЕКТУ", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, italic=True, size=16, indent=False))
front.append(para("НА ТЕМУ:", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, italic=True, size=16, indent=False))
front.append(para(TOPIC, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=18, before=8, after=16, indent=False))


def sign_row(left, name):
    p = para(indent=False, after=2)
    run(p, f"{left}\t", size=12); run(p, f"{SIG()}\t", size=12)
    run(p, name if name else "________________", size=12, underline=bool(name), hl=not name)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(8.5)); p.paragraph_format.tab_stops.add_tab_stop(Cm(13.5))
    q = para("\t(Подпись, дата)\t(И.О. Фамилия)", size=8, indent=False, after=2)
    q.paragraph_format.tab_stops.add_tab_stop(Cm(9.3)); q.paragraph_format.tab_stops.add_tab_stop(Cm(13.8))
    return [p, q]


for k, s in enumerate(STUDENTS):
    front += sign_row(f"Студенты группы {GROUP}" if k == 0 else "", s)
front.append(para("", after=4, indent=False))
front += sign_row("Руководитель", HEAD)
front.append(para("", after=10, indent=False))
front.append(page_break(para(f"{YEAR} г.", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, indent=False)))
# задание
for t in ("Министерство науки и высшего образования Российской Федерации",
          "«Московский государственный технический университет имени Н.Э. Баумана»", "(МГТУ им. Н.Э. Баумана)"):
    front.append(para(t, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, after=0, indent=False))
front.append(para("УТВЕРЖДАЮ", align=WD_ALIGN_PARAGRAPH.RIGHT, size=12, before=10, after=0, indent=False))
front.append(para("Заведующий кафедрой ________", align=WD_ALIGN_PARAGRAPH.RIGHT, size=12, after=0, indent=False))
front.append(para(f"«____» ____________ {YEAR} г.", align=WD_ALIGN_PARAGRAPH.RIGHT, size=12, indent=False))
front.append(para("ЗАДАНИЕ", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, before=10, after=0, indent=False))
front.append(para("на выполнение курсового проекта", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, indent=False))
TASK = [("по дисциплине: ", "прикладная механика"),
        (f"Студенты группы {GROUP}, бригада №2: ", ", ".join(s for s in STUDENTS if s) + "."),
        ("Тема курсового проекта: ", TOPIC + "."),
        ("Направленность КП: ", "учебный."), ("Источник тематики: ", "кафедра."),
        ("График выполнения проекта: ", "25 % к 3 нед., 50 % к 8 нед., 75 % к 11 нед., 100 % к 14 нед.")]
for a, b in TASK:
    p = para(indent=False, after=2); run(p, a, bold=True, size=12); run(p, b, size=12, hl="______" in b); front.append(p)
front.append(para("Задание: для ручного укупоривателя бутылки Long Neck 0,33 л с тангенсным механизмом провести:",
                  size=12, bold=True, before=6, after=2, indent=False))
for a, b in (("Часть 1. Постановка ТЗ: ", "определить назначение, качественные и количественные критерии механизма."),
             ("Часть 2. Расчётная часть: ", "решить задачу синтеза, выполнить кинематический анализ, первичный силовой, "
                                             "прочностной и уточняющий силовой расчёты."),
             ("Часть 3. Конструкторская часть: ", "построить 3D-модели звеньев и сборку, провести расчёт МКЭ и доработать "
                                                    "геометрию деталей."),
             ("Часть 4. Испытания: ", "изготовить прототип на 3D-принтере, собрать и проверить механизм, подготовить "
                                       "инструкцию по сборке и эксплуатации.")):
    p = para(indent=False, after=2); run(p, a, bold=True, size=12); run(p, b, size=12); front.append(p)
p = para(indent=False, before=6, after=2); run(p, "Оформление курсового проекта: ", bold=True, size=12)
run(p, "расчётно-пояснительная записка на ___ листах формата А4; 3D-модели КОМПАС-3D, анимация сборки, инструкция по "
       "сборке и эксплуатации, презентация.", size=12); front.append(p)
front.append(para(f"Дата выдачи задания «____» сентября {YEAR} г.", size=12, before=6, indent=False))
for k, s in enumerate(STUDENTS):
    front += sign_row("Студенты" if k == 0 else "", s)
front += sign_row("Руководитель", HEAD)
front.append(page_break(para("", indent=False)))
# содержание
front.append(para("Содержание", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, indent=False))
p = para(indent=False)
for kind, val in (("begin", None), ("instr", ' TOC \\o "1-2" \\h \\z \\u '), ("separate", None), ("text", "Обновите оглавление (F9)"), ("end", None)):
    r = OxmlElement("w:r")
    if kind == "instr":
        it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = val; r.append(it)
    elif kind == "text":
        t = OxmlElement("w:t"); t.text = val; r.append(t)
    else:
        fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind); r.append(fc)
    p._p.append(r)
front.append(page_break(p))
# введение
front.append(heading("Введение"))
for t in ("Ручной настольный укупориватель надевает на горлышко стеклянной бутылки Long Neck 0,33 л металлическую "
          "кронен-крышку Ø26 мм и обжимает её юбку. Оператор нажимает на рукоять, сверху опускается головка с конической "
          "горловиной и обжимает крышку на венчике бутылки.",
          "Привод рабочего органа — тангенсный механизм: кулиса с рукоятью поворачивается вокруг оси O, камень скользит по "
          "кулисе и через палец D перемещает ползун строго вертикально, y = e·tg φ. Ход головки — 16 мм: 10 мм подход и "
          "6 мм обжим.",
          "Цель проекта — спроектировать и исследовать механизм: синтез, кинематика, силовой и прочностной расчёты, "
          "3D-модели, расчёт МКЭ, изготовление и испытание прототипа на 3D-принтере."):
    front.append(para(t))
front += picture(os.path.join(FIG, "01_без_кожуха.png"), 7.5, None)
front.append(para("Укупориватель без кожуха: стойка, кулиса с рукоятью, камень, ползун с головкой.", style="af5", indent=False))
first = next(e for e in body.iterchildren() if not e.tag.endswith("sectPr"))
for e in front:
    first.addprevious(e._p if hasattr(e, "_p") else e)
for i, t in INS_BEFORE.items():
    EL[i].addprevious(para(t)._p)

# ---------------------------------------------------------------- новые разделы перед «Источниками»
SRC = EL[601]
new = []
new.append(heading("11 Проектирование деталей и сборки"))
for t in ("По принятым размерам в КОМПАС-3D v25 построены модели всех деталей и сборка УКП.00.000 (29 сопряжений). "
          "Сборка повторяет кинематику: при повороте кулисы ползун движется по закону y = e·tg φ, угол кулисы ограничен "
          "упорами φк…φн.",
          "Конструктивные решения:"):
    new.append(para(t))
for t in ("стойка — лист с осью O, упорами рукояти и выемкой под направляющую;",
          "кулиса — полоса 8 × 18 мм со ступицей Ø16 и пазами облегчения;",
          "камень — замкнутая обойма, палец D запрессован в его стенку;",
          "палец D, гайка и установочный винт — резьба М10 × 1,5;",
          "направляющая — отдельная деталь в выемке стойки, закреплена установочным винтом М10;",
          "кожух закрывает механизм и держится на двух защёлках."):
    new.append(para("– " + t))
new.append(para("Пересечения тел проверены на всём ходе рукояти через 1° (40 положений) — пересечений нет."))
new += picture(os.path.join(FIG, "детали.png"), 16.5, "Рисунок 16 — Детали укупоривателя (КОМПАС-3D)")
new += picture(os.path.join(FIG, "ход.png"), 13.5, "Рисунок 17 — Крайние положения механизма")
new.append(heading("12 Расчёт методом конечных элементов"))
new.append(para("Детали рассчитаны в APM FEM при нагрузках положения φу = 41,63°. По картам эквивалентных напряжений "
                "материал добавлен в нагруженных зонах и убран в ненагруженных. Материал каждой детали — самый простой, "
                "который выдерживает полученное напряжение: Ст3сп ([σ] = 98 МПа), сталь 45 (142 МПа), сталь 40Х (314 МПа)."))
FEM = [("кулиса", "Рисунок 18 — Кулиса: 92,6 МПа; девять пазов облегчения, −22 % массы"),
       ("ползун", "Рисунок 19 — Ползун: 95,9 → 49,0 МПа; скругления R3, головка-колокол"),
       ("камень", "Рисунок 20 — Камень: 646 → 100 МПа; замкнутая обойма, R1,5"),
       ("направляющая", "Рисунок 21 — Направляющая: 920 → 136,2 МПа; планка 12 мм, скругления R10, R14")]
for name, cap in FEM:
    new += picture(os.path.join(FIG, f"apm_{name}.png"), 15.5, cap)
new.append(para("Таблица 20 — Результаты расчёта МКЭ", style="af5", indent=False))
new.append(table([("Деталь", "SVM max, МПа: до → после", "Материал", "[σ], МПа", "Масса, г"),
                  ("Кулиса", "92,6 → 92,6", "Ст3сп", "98", "577,6 → 449,7"),
                  ("Ползун", "95,9 → 49,0", "Ст3сп", "98", "418,7 → 320,8"),
                  ("Камень", "646 → 100", "сталь 45", "142", "30,7 → 34,6"),
                  ("Палец D", "192", "сталь 40Х", "314", "18,7"),
                  ("Направляющая", "920 → 136,2", "сталь 45", "142", "402,3 → 597,2")], [3.3, 4.6, 2.6, 2.0, 3.6]))
new.append(heading("13 Изготовление и испытание прототипа"))
for t in ("Прототип напечатан на FDM-принтере с соплом 0,4 мм. Резьбы М10 × 1,5 напечатаны: зазор 0,2 мм по виткам "
          "и 0,3–0,4 мм по диаметру.",
          "Испытание первой сборки: отверстие кулисы Ø10 на оси Ø10 без зазора после печати оказалось меньше оси — кулиса "
          "не проворачивалась и сломалась у оси. В модель введены зазоры в подвижных посадках: отверстия кулисы и ползуна — "
          "Ø10,6 на ось и палец Ø10 (0,3 мм на сторону).",
          "Сборка — 10 шагов (рисунок 22), к прототипу подготовлены инструкция по сборке и эксплуатации, 3D-анимация "
          "сборки и шестигранный ключ S5 для установочного винта."):
    new.append(para(t))
new += picture(os.path.join(FIG, "сборка.png"), 16.5, "Рисунок 22 — Основные шаги сборки прототипа")
new.append(heading("Заключение"))
for t in ("Спроектирован ручной укупориватель бутылки Long Neck 0,33 л на тангенсном механизме: ход головки 16 мм, "
          "усилие укупоривания 1974 Н, сила руки не более 112,8 Н при рукояти 500 мм.",
          "Решена задача синтеза: окно качания кулисы 59,47° → 22,72° (ψ = 36,75°), e = 12,53 мм.",
          "Выполнены кинематический анализ, первичный и уточняющий силовые расчёты; учёт масс и сил инерции снижает силу "
          "руки на 2,6 % (112,8 → 109,9 Н), реакции меняются менее чем на 1 %.",
          "По прочностному расчёту приняты кулиса 8 × 18 мм (Ст3сп), шток Ø8 мм, ось и палец Ø10 мм.",
          "Построены 3D-модели и сборка; расчётом МКЭ детали доработаны и облегчены, материалы выбраны по напряжениям.",
          "Изготовлен и испытан прототип; по результатам испытания введены зазоры в подвижных посадках."):
    new.append(para("– " + t))
for e in new:
    SRC.addprevious(e._p if hasattr(e, "_p") else e._tbl if hasattr(e, "_tbl") else e)
for e in body.iter(qn("w:pageBreakBefore")):         # разделы идут подряд, без полупустых страниц
    e.getparent().remove(e)

# ---------------------------------------------------------------- номера таблиц и ссылки
CAP_T = re.compile(r"^Таблица (\d+)")
old_t = [int(CAP_T.match(txt(e)).group(1)) for e in body.iterchildren() if e.tag.endswith("}p") and CAP_T.match(txt(e))]
TMAP = {o: k + 1 for k, o in enumerate(o for o in old_t if o != 20 or True)}
# таблица 20 (МКЭ) — новая, у неё уже свой номер: старая 20 (уточнённый расчёт) → 17, новая → 20
seq = []
for e in body.iterchildren():
    if e.tag.endswith("}p") and CAP_T.match(txt(e)):
        seq.append(e)
TMAP, num = {}, 0
for e in seq:
    num += 1
    o = int(CAP_T.match(txt(e)).group(1))
    ts_ = [t for t in e.iter(qn("w:t")) if t.text]
    if re.match(r"^Таблица\s*\d+", ts_[0].text):
        ts_[0].text = re.sub(r"^Таблица\s*\d+", f"Таблица {num}", ts_[0].text, count=1)
    else:                                            # «Таблица » и номер — в разных прогонах
        k = next(j for j, t in enumerate(ts_[1:], 1) if re.match(r"^\s*\d", t.text))
        ts_[k].text = re.sub(r"^(\s*)\d+", lambda m: m.group(1) + str(num), ts_[k].text, count=1)
    if e not in [n._p for n in new if hasattr(n, "_p")]:
        TMAP[o] = num
NEW_FEM_T = num
print("таблицы:", TMAP, "| МКЭ —", NEW_FEM_T)
missing = set()


def fix_refs(t):
    def tab(m):
        nums = re.sub(r"\d+", lambda q: str(TMAP.get(int(q.group(0)), q.group(0))), m.group(2))
        return m.group(1) + nums

    def sec(m):
        ctx_l, ctx_r = m.string[max(0, m.start() - 30):m.start()], m.string[m.end():m.end() + 12]
        if re.search(r"ТЗ|ГОСТ|ISO|EN |DIN|Фех|табл", ctx_l) or re.search(r"ГОСТ|ISO", ctx_r):
            return m.group(0)                        # пункт ТЗ или стандарта, не раздел записки
        def one(q):
            v = q.group(0)
            if v in SEC: return SEC[v]
            missing.add(v); return v
        return m.group(1) + re.sub(r"\d+(?:\.\d+)?", one, m.group(2))
    t = re.sub(r"(табл(?:\.|иц[а-я]*)\s+)(\d+(?:(?:,\s*|\s+и\s+)\d+)*)", tab, t)
    t = re.sub(r"(\b(?:пп?\.|раздел[а-я]*)\s*)(\d+(?:\.\d+)?(?:(?:,\s*|\s+и\s+)\d+(?:\.\d+)?)*)", sec, t)
    return t


for e in body.iter(qn("w:t")):
    if e.text and re.search(r"табл|п\.|раздел", e.text) and not CAP_T.match(e.text):
        e.text = fix_refs(e.text)
# «пп» и «. 12.3, 12.4» в соседних прогонах (так в таблице принятых параметров)
for pp in body.iter(qn("w:p")):
    ts = list(pp.iter(qn("w:t")))
    for x, y in zip(ts, ts[1:]):
        if x.text and y.text and re.search(r"(?:^|[\s;(])пп?$", x.text) and not re.search(r"ТЗ|ГОСТ", x.text)                 and re.match(r"\.\s*\d", y.text):
            y.text = re.sub(r"^(\.\s*)([\d.,\sи]+)", lambda m: m.group(1) + re.sub(
                r"\d+(?:\.\d+)?", lambda q: SEC.get(q.group(0), q.group(0)), m.group(2)), y.text)
for p in [n for n in new if hasattr(n, "_p")]:
    for t in p._p.iter(qn("w:t")):
        t.text = t.text.replace("Таблица 20 —", f"Таблица {NEW_FEM_T} —")
print("ссылки на разделы, которых нет:", sorted(missing) or "нет")
d.sections[0].different_first_page_header_footer = True
d.save(OUT)
print("сохранено:", OUT)
