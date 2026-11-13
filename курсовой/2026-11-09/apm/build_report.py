# -*- coding: utf-8 -*-
"""Отчёт «Прочностной анализ деталей в APM FEM»: по каждой детали — исходная деталь, карта напряжений, доработанная деталь,
её карта (картинки деталей — экспорт КОМПАС, карты — скрины APM FEM пользователя), нагрузки и итоговая таблица.
    python build_report.py"""
import os
from PIL import Image
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
PIC, SCR, TMP = (os.path.join(HERE, n) for n in ("Картинки", "Скрины", "_для_отчёта"))
os.makedirs(TMP, exist_ok=True)
OUT = os.path.join(HERE, "Прочностной анализ деталей в APM FEM.docx")


def prep(path, crop_top=0):
    """копия картинки для отчёта: обрезка панели инструментов сверху и серого фона — по цветным и тёмным пикселям
    (модель, стрелки, шкала)"""
    im = Image.open(path).convert("RGB")
    if crop_top:
        im = im.crop((0, crop_top, im.width, im.height))
    px = im.load()
    mask = Image.new("L", im.size, 0)
    mp = mask.load()
    for y in range(0, im.height):
        for x in range(0, im.width):
            r, g, b = px[x, y]
            if max(r, g, b) - min(r, g, b) > 30 or (r + g + b) < 420:
                mp[x, y] = 255
    box = mask.getbbox()
    if box:
        pad = 14
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    out = os.path.join(TMP, os.path.basename(path))
    im.save(out)
    return out


PARTS = [
    dict(name="Кулиса УКП.01.001", mat="Ст3сп ГОСТ 380-2005 (E = 2·10⁵ МПа, ν = 0,3, σт = 245 МПа)",
         loads=["закрепление: отверстие Ø10 ступицы (ось O), перемещения X, Y, Z;",
                "сила от камня R12N = 2515 Н — на участке 20 × 8 мм нижней грани полосы, где при φу стоит камень (16,76 мм от оси O), "
                "по нормали к полосе;",
                "сила руки P = 112,8 Н — на скруглённом торце рукояти, вертикально вниз (в осях детали X = −74,9 Н, Y = −84,3 Н)."],
         mesh="10-узловые тетраэдры, шаг 3 мм",
         pics=[(os.path.join(PIC, "кулиса_1_деталь.png"), 0, "исходная деталь"),
               (os.path.join(SCR, "кулиса_2_тест.png"), 0, "эквивалентные напряжения (SVM), исходная деталь"),
               (os.path.join(PIC, "кулиса_3_новая_2.png"), 0, "доработанная деталь: 9 пазов 30 × 8 мм по средней линии полосы"),
               (os.path.join(SCR, "кулиса_4_тест_новой_2.png"), 45, "эквивалентные напряжения (SVM), доработанная деталь")],
         before="Красная зона — кромки полосы сразу за камнем: изгиб от силы руки, 92,6 МПа (ручной расчёт — 94,6 МПа). По средней "
                "линии полосы (нейтральная ось), в ступице и на конце рукояти материал почти не нагружен.",
         change="В красной зоне размеры полосы изменить нельзя: по ней ходит камень, рядом упоры стойки и паз кожуха; напряжение "
                "92,6 МПа не превышает допускаемого [σ] = 98 МПа (запас по текучести 2,65). Синяя средняя часть полосы облегчена: "
                "девять продолговатых пазов 30 × 8 мм с перемычками 10 мм на участке 125…475 мм от оси O; конец рукояти под руку "
                "оставлен сплошным.",
         after="Наибольшее напряжение не изменилось — 92,6 МПа у камня; по кромкам над пазами не более 81 МПа. Масса уменьшилась "
               "с 577,6 до 449,7 г (на 22 %)."),
    dict(name="Ползун УКП.03.001", mat="Ст3сп ГОСТ 380-2005 (E = 2·10⁵ МПа, ν = 0,3, σт = 245 МПа)",
         loads=["закрепление: отверстие Ø10 под палец D, перемещения X, Y, Z;",
                "сила обжима Fук = 1880 Н — на конической грани горловины головки, вдоль оси штока вверх (распределена по конусу);",
                "реакция направляющей R30N = 1671 Н — на боковой грани направляемой части, поперёк оси штока (горизонтальная "
                "составляющая силы пальца Fук·tg φу)."],
         mesh="10-узловые тетраэдры, шаг 2 мм",
         pics=[(os.path.join(PIC, "ползун_1_деталь.png"), 0, "исходная деталь (вид снизу на горловину)"),
               (os.path.join(SCR, "ползун_2_тест.png"), 0, "эквивалентные напряжения (SVM), исходная деталь"),
               (os.path.join(PIC, "ползун_3_новый.png"), 0, "доработанная деталь: головка-колокол, скругления R3"),
               (os.path.join(SCR, "ползун_4_тест_нового.png"), 0, "эквивалентные напряжения (SVM), доработанная деталь")],
         before="Шток сжат силой обжима: 36–42 МПа (ручной расчёт — 37 МПа). Пик 95,9 МПа — острый угол в переходе штока в головку. "
                "Головка над полостью и направляемая часть почти не нагружены.",
         change="В переходах шток–головка и шток–направляемая часть добавлены скругления R3. Сплошной диск головки Ø40 над полостью "
                "заменён конусом от Ø40 к штоку (головка-колокол); цилиндр Ø40 оставлен на высоте горловины. Диаметр штока Ø8 не "
                "уменьшается — он выбран по устойчивости.",
         after="Пик у штока снизился с 95,9 до 49,0 МПа, шток — 38–40 МПа. Масса уменьшилась с 418,7 до 320,8 г (на 23 %)."),
    dict(name="Камень УКП.02.001",
         mat="сталь 45 ГОСТ 1050-2013 (исходная деталь), сталь 40Х ГОСТ 4543-2016 с улучшением (доработанная; σт = 785 МПа, "
             "[σ] = 314 МПа); E = 2·10⁵ МПа, ν = 0,3",
         loads=["закрепление: отверстие Ø10 под палец D, перемещения X, Y, Z;",
                "сила от полосы кулисы R21N = 2515 Н — на внутренней грани нижней стенки обоймы, по нормали к полосе."],
         mesh="10-узловые тетраэдры, шаг 1 мм",
         pics=[(os.path.join(PIC, "камень_1_деталь.png"), 0, "исходная деталь (обойма с губками)"),
               (os.path.join(SCR, "камень_2_тест.png"), 0, "эквивалентные напряжения (SVM), исходная деталь"),
               (os.path.join(PIC, "камень_3_новый_2.png"), 0, "доработанная деталь: замкнутая обойма, R1,5, фаски"),
               (os.path.join(SCR, "камень_4_тест_нового_2.png"), 0, "эквивалентные напряжения (SVM), доработанная деталь")],
         before="Нижняя стенка 4 мм, на которую давит полоса, работала консолью от перемычки с отверстием: 646 МПа во "
                "внутреннем углу стенка–перемычка — больше предела текучести стали 45.",
         change="Обойма замкнута сплошной задней стенкой 2,5 мм за полосой (у ступицы кулисы оставлены губки), стенки опираются "
                "с двух сторон. Во внутренних углах — скругления R1,5, на отверстии под палец — фаски 0,5 × 45° (заход для "
                "запрессовки). Материал — сталь 40Х с улучшением: толщину перемычки увеличить нельзя (0,5 мм до полосы, 1 мм "
                "до ползуна).",
         after="Напряжения снизились: в стенках — с 646 до 70 МПа и ниже, в перемычке вокруг пальца — 100–230 МПа, что меньше "
               "допускаемого 314 МПа для 40Х. Местный пик на кромке отверстия у фаски — край закрепления в расчётной модели, он "
               "ниже предела текучести 40Х. Масса — 34,6 г (было 30,7 г)."),
]


def set_cell_border_none(table):
    tbl = table._tbl
    pr = tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}"); x.set(qn("w:val"), "nil"); b.append(x)
    pr.append(b)


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(1.5), Cm(2), Cm(2)
st = doc.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(14)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(4)
st.paragraph_format.line_spacing = 1.15


def para(text, bold=False, size=None, align=None, after=None):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = bold
    if size: r.font.size = Pt(size)
    if align is not None: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p


para("Прочностной анализ деталей в APM FEM", True, 16, WD_ALIGN_PARAGRAPH.CENTER, 10)
para("Детали укупоривателя рассчитаны методом конечных элементов в APM FEM (КОМПАС-3D v25): линейный статический расчёт, "
     "нагрузки — наибольшие рабочие, в положении начала пластической деформации φу = 41,63° (раздел 11 расчёта). Силы на "
     "каждой детали уравновешены, закрепление принимает реакцию сопрягаемой детали. По карте эквивалентных напряжений (SVM) "
     "в красных зонах добавлен материал, в синих — убран; доработанная деталь рассчитана повторно с теми же нагрузками.")
para("Итог: после доработки напряжения в деталях снизились (у кулисы наибольшее напряжение не выросло) и не превышают "
     "допускаемых; кулиса стала легче на 22 %, ползун — на 23 %. Результаты по деталям — в таблице в конце.", True)
fig = 0
for k, part in enumerate(PARTS, 1):
    para(f"{k}. {part['name']}", True, 15, after=6)
    para(f"Материал: {part['mat']}. Сетка: {part['mesh']}. Нагрузки:")
    for l in part["loads"]:
        p = para("— " + l); p.paragraph_format.left_indent = Cm(0.6)
    wide = part["name"].startswith("Кулиса")                     # кулиса длинная — по одной картинке в строку во всю ширину
    rows, cols = (8, 1) if wide else (4, 2)
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_cell_border_none(table)
    for r_ in table.rows:
        trPr = r_._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
    for i, (path, crop, cap) in enumerate(part["pics"]):
        fig += 1
        row, col = (2 * i, 0) if wide else ((i // 2) * 2, i % 2)
        cell = table.cell(row, col)
        img = prep(path, crop)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].paragraph_format.keep_with_next = True
        if wide:
            cell.paragraphs[0].add_run().add_picture(img, width=Cm(15.5))
        else:
            cell.paragraphs[0].add_run().add_picture(img, height=Cm(9.0))
        c = table.cell(row + 1, col).paragraphs[0]
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run(f"Рисунок {fig} — {part['name'].split()[0]}: {cap}"); r.font.size = Pt(11)
    para("Исходная деталь. " + part["before"])
    para("Доработка. " + part["change"])
    para("Доработанная деталь. " + part["after"])

para("Итоги", True, 15, after=6).paragraph_format.keep_with_next = True
t = doc.add_table(rows=1, cols=5)
t.style = "Table Grid"
hdr = ["Деталь", "Масса, г: было → стало", "SVM max, МПа: было → стало", "[σ], МПа", "Что изменено"]
for c, s in zip(t.rows[0].cells, hdr):
    c.paragraphs[0].add_run(s).bold = True
for row in (("Кулиса", "577,6 → 449,7", "92,6 → 92,6", "98", "9 пазов 30 × 8 по нейтральной оси"),
            ("Ползун", "418,7 → 320,8", "95,9 → 49,0", "98", "скругления R3, головка-колокол"),
            ("Камень", "30,7 → 34,6", "646 → 230 (перемычка)", "142 → 314", "замкнутая обойма, R1,5, фаски, сталь 40Х")):
    cells = t.add_row().cells
    for c, s in zip(cells, row):
        c.paragraphs[0].add_run(s)
for r_ in t.rows:
    trPr = r_._tr.get_or_add_trPr(); trPr.append(OxmlElement("w:cantSplit"))
    for c in r_.cells:
        c.paragraphs[0].paragraph_format.keep_with_next = True
        for p in c.paragraphs:
            for run in p.runs:
                run.font.size = Pt(12)
doc.save(OUT)
print(OUT)
