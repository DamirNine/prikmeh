# -*- coding: utf-8 -*-
"""23.11 — правка презентации Корнеева (его файл с комментариями) по его комментариям и замечаниям преподавателя.
Вход:  ../Презентация_Корнеева_комментарии.pptx (14 слайдов, его правки и комментарии в тексте слайдов/примечаниях PPT)
Выход: Презентация_укупориватель_23-11.pptx
  3  — слайд с крышкой: заголовок, его картинка обжима, рисунок 1 ГОСТ 32624-2020 с размерами, формула усилия;
  6  — новый слайд «Кинематический анализ: векторный контур» (контур O–B–D, уравнение замкнутости, проекции, y_D,
       дифференцирование), на следующем — графики; пример Корнеева и его текст-комментарий убраны;
  7  — расчётные схемы звеньев с белыми кружками; пример Корнеева убран;
  8  — эпюры с выделенным опасным сечением D, белые кружки; критерии для сечения;
  9  — критерии и формулы: изгиб со сжатием, устойчивость, срез, смятие; сечения с выносными линиями; таблица → итоги;
  10 — схемы с силами тяжести и инерции — белые кружки;
  11 — σэкв (Мизес) вместо σmax; крупные карты напряжений APM до/после;
  12 — кулиса «после» светлая (видны отверстия), направляющая «после» — нынешняя (вариант без планок, отверстие в полке).
Комментарии PPT (modern comments) удаляются вместе с исправленными местами.
    python edit_pres23.py"""
import copy, os, re
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Emu
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
KURS = os.path.join(HERE, "..", "..")
SRC = os.path.join(HERE, "..", "Презентация_Корнеева_комментарии.pptx")
OUT = os.path.join(HERE, "Презентация_укупориватель_23-11.pptx")
APM = os.path.join(KURS, "2026-11-16", "apm", "_для_отчёта")
GOST = os.path.join(HERE, "..", "гост_32624", "рис1_контролируемые_параметры.png")
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"a": A, "p": P}
I = lambda x: int(Inches(x))

prs = Presentation(SRC)
S = list(prs.slides)                       # исходная нумерация (1-based → S[n-1])


def shape(slide, name):
    return next(sh for sh in slide.shapes if sh.name == name)


def remove(sh):
    sh._element.getparent().remove(sh._element)


def fit(path, box, valign="ctr"):
    l, t, w, h = box
    iw, ih = Image.open(path).size
    k = min(w / iw, h / ih)
    nw, nh = iw * k, ih * k
    top = t + (h - nh) / 2 if valign == "ctr" else t
    return l + (w - nw) / 2, top, nw, nh


def add_pic(slide, path, box, before=None, valign="ctr"):
    l, t, w, h = fit(path, box, valign)
    pic = slide.shapes.add_picture(path, I(l), I(t), I(w), I(h))
    if before is not None:
        before._element.addprevious(pic._element)
    return pic


def replace_pic(slide, old, path, box=None, valign="ctr"):
    if box is None:
        box = (old.left / 914400, old.top / 914400, old.width / 914400, old.height / 914400)
    pic = add_pic(slide, path, box, before=old, valign=valign)
    remove(old)
    return pic


def run_xml(text, b=False, size=1300, color="tx1", base=None, i=False):
    r = etree.SubElement(etree.Element("dummy"), f"{{{A}}}r")
    rpr = etree.SubElement(r, f"{{{A}}}rPr", lang="ru-RU", sz=str(size), dirty="0")
    if b:
        rpr.set("b", "1")
    if i:
        rpr.set("i", "1")
    if base:
        rpr.set("baseline", str(base))
    fill = etree.SubElement(rpr, f"{{{A}}}solidFill")
    if color.startswith("#"):
        etree.SubElement(fill, f"{{{A}}}srgbClr", val=color[1:])
    else:
        etree.SubElement(fill, f"{{{A}}}schemeClr", val=color)
    t = etree.SubElement(r, f"{{{A}}}t"); t.text = text
    return r


def rich(segs, size=1300, color="tx1", b=False):
    """'R_{12} = 2515' → прогоны с нижними индексами (_{..}) и верхними (^{..})"""
    out = []
    for m in re.finditer(r"_\{([^}]*)\}|\^\{([^}]*)\}|([^_^]+|[_^])", segs):
        if m.group(1) is not None:
            out.append(run_xml(m.group(1), b, size, color, base=-25000))
        elif m.group(2) is not None:
            out.append(run_xml(m.group(2), b, size, color, base=30000))
        else:
            out.append(run_xml(m.group(3), b, size, color))
    return out


def set_paras(sh, paras, algn=None, space=None):
    """paras: [(строка с _{}/^{}, dict(b=, size=, color=))] — заменить весь текст фигуры"""
    txb = sh._element.find(".//p:txBody", NS)
    if txb is None:
        txb = sh._element.find(".//{%s}txBody" % P)
    for p in txb.findall(f"{{{A}}}p"):
        txb.remove(p)
    for text, opt in paras:
        p = etree.SubElement(txb, f"{{{A}}}p")
        ppr = etree.SubElement(p, f"{{{A}}}pPr", marL="0", indent="0")
        if algn:
            ppr.set("algn", algn)
        if space:
            sb = etree.SubElement(ppr, f"{{{A}}}spcBef"); etree.SubElement(sb, f"{{{A}}}spcPts", val=str(space))
        etree.SubElement(ppr, f"{{{A}}}buNone")
        for r in rich(text, opt.get("size", 1300), opt.get("color", "tx1"), opt.get("b", False)):
            p.append(r)


def move(sh, box):
    l, t, w, h = box
    sh.left, sh.top, sh.width, sh.height = I(l), I(t), I(w), I(h)


def label_para(lab, text):
    return [(lab, dict(b=True)), (text, {})]


def duplicate_slide(src_slide, index_after):
    """копия слайда (фигуры и картинки) сразу после index_after (0-based в текущем списке)"""
    new = prs.slides.add_slide(src_slide.slide_layout)
    for sh in list(new.shapes):
        remove(sh)
    for el in src_slide.shapes._spTree.iterchildren():
        if el.tag.endswith("}nvGrpSpPr") or el.tag.endswith("}grpSpPr"):
            continue
        new.shapes._spTree.append(copy.deepcopy(el))
    for el in new.shapes._spTree.iter(f"{{{A}}}blip"):
        rid = el.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        part = src_slide.part.related_part(rid)
        el.set("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed", new.part.relate_to(part, RT.IMAGE))
    lst = prs.slides._sldIdLst
    ids = list(lst)
    lst.remove(ids[-1]); lst.insert(index_after + 1, ids[-1])
    return new


def drop_comments(slide):
    for rel in list(slide.part.rels.values()):
        if "comments" in rel.reltype:
            slide.part.drop_rel(rel.rId)
    ext = slide._element.find(".//p:extLst", NS)
    if ext is not None:
        for e in list(ext):
            if b"modernComment" in etree.tostring(e) or b"commentRel" in etree.tostring(e):
                ext.remove(e)


# =============================================================== 3 — крышка
s = S[2]
title = shape(s, "Заголовок 1")
title_ref = shape(S[3], "Text 1")                    # оформление заголовка — как у остальных слайдов
el = copy.deepcopy(title_ref._element); title._element.addprevious(el); remove(title)
t3 = next(sh for sh in s.shapes if sh._element is el)
t3.text_frame.paragraphs[0].runs[0].text = "Укупоривание: обжим кронен-крышки"
for r in t3.text_frame.paragraphs[0].runs[1:]:
    r._r.getparent().remove(r._r)
crimp = shape(s, "Рисунок 4")
frame_ref = shape(S[5], "рамка_43")                  # рамки и подписи — как на остальных слайдах
cap_ref = shape(S[5], "подпись_45")
lbl_ref = shape(S[5], "строка_39")
res_box, res_txt = shape(S[5], "вывод_49"), shape(S[5], "текст_вывода_50")


def copy_to(slide, sh, box, paras=None, algn=None, back=False):
    el = copy.deepcopy(sh._element)
    if back:                                          # под всеми фигурами (сразу за свойствами группы)
        slide.shapes._spTree.insert(2, el)
    else:
        slide.shapes._spTree.append(el)
    new = next(x for x in slide.shapes if x._element is el)
    move(new, box)
    if paras is not None:
        set_paras(new, paras, algn=algn)
    return new


copy_to(s, frame_ref, (0.6, 1.25, 7.55, 4.48), back=True)
# картинка Корнеева — вынуть blob и вписать в рамку
blob = crimp.image.blob
cp = os.path.join(FIG, "обжим_корнеев.png"); open(cp, "wb").write(blob)
replace_pic(s, crimp, cp, (0.72, 1.33, 7.31, 3.95))
copy_to(s, cap_ref, (0.6, 5.77, 7.55, 0.28), [("Обжим юбки коническим входом головки: Ø32,10 → Ø28,6 мм (α = 16,3°)",
                                                 dict(size=1100, color="accent2"))], algn="ctr")
copy_to(s, frame_ref, (8.35, 1.25, 4.38, 2.75), back=True)
add_pic(s, GOST, (8.5, 1.33, 4.08, 2.59))
copy_to(s, cap_ref, (8.35, 4.03, 4.38, 0.28), [("ГОСТ 32624-2020, рисунок 1 — контролируемые параметры",
                                                 dict(size=1100, color="accent2"))], algn="ctr")
# усилие укупоривания — формулой (Корнеев 23:58: «напиши формулу нормально, а не просто текстом»)
add_pic(s, os.path.join(FIG, "ф_укупоривание.png"), (8.4, 5.2, 4.3, 0.95))
copy_to(s, lbl_ref, (8.35, 4.36, 4.38, 0.85), [
    ("Тип I, венчик 26 H 180 (табл. 1 ГОСТ)", dict(b=True, size=1200)),
    ("h = 6,00 ± 0,15 мм;  d = 26,75^{+0,15} мм", dict(size=1200)),
    ("D = 32,10 ± 0,20 мм;  z = 21;  жесть 0,16…0,30 мм", dict(size=1200))])
copy_to(s, res_box, (0.6, 6.25, 12.13, 0.55))
copy_to(s, res_txt, (0.8, 6.25, 11.73, 0.55), [
    ("Результат: ", dict(b=True, size=1500, color="tx2"))])
rt = s.shapes[-1]
p0 = rt._element.find(f".//{{{A}}}p")
for r in rich("усилие укупоривания F_{ук} = 1974 Н", 1500):
    p0.append(r)

# =============================================================== 6 — кинематика: новый слайд «векторный контур» перед графиками
s6 = S[5]
drop_comments(s6)
remove(shape(s6, "Рисунок 17"))
k = duplicate_slide(s6, 5)                     # новый слайд после исходного 6 — сделаем его «графиками», а 6 — контуром
# --- s6: векторный контур
shape(s6, "Text 1").text_frame.paragraphs[0].runs[0].text = "Кинематический анализ: векторный контур"
set_paras(shape(s6, "строка_39"), label_para("Что делаем", "составляем векторный контур O → B → D, проецируем его на оси, "
                                                            "выражаем сторону y_{D} и дифференцируем по времени"))
move(shape(s6, "строка_39"), (0.82, 1.85, 3.21, 1.25))
set_paras(shape(s6, "строка_41"), label_para("Известно", "e = 12,5 мм — постоянная сторона; φ(t), ω(t), ε(t) — закон "
                                                          "движения кулисы; l_{OD} — переменная сторона"))
move(shape(s6, "строка_41"), (0.82, 3.25, 3.21, 1.3))
remove(shape(s6, "рис_40"))
remove(shape(s6, "рис_44")); remove(shape(s6, "рис_47"))
move(shape(s6, "рамка_43"), (4.45, 1.25, 3.85, 4.48))
add_pic(s6, os.path.join(FIG, "вектор_контур.png"), (4.6, 1.4, 3.55, 4.15))
set_paras(shape(s6, "подпись_45"), [("Векторный контур O → B → D (B — проекция D на x)", dict(size=1100, color="accent2"))],
          algn="ctr")
move(shape(s6, "подпись_45"), (4.45, 5.77, 3.85, 0.28))
move(shape(s6, "рамка_46"), (8.5, 1.25, 4.23, 4.48))
add_pic(s6, os.path.join(FIG, "ф_контур.png"), (8.7, 1.45, 3.83, 4.1))
set_paras(shape(s6, "подпись_48"), [("Уравнение замкнутости, проекции, производные", dict(size=1100, color="accent2"))],
          algn="ctr")
move(shape(s6, "подпись_48"), (8.5, 5.77, 4.23, 0.28))
set_paras(shape(s6, "текст_вывода_50"), [("", {})])
p0 = shape(s6, "текст_вывода_50")._element.find(f".//{{{A}}}p")
p0.append(run_xml("Результат: ", True, 1500, "tx2"))
for r in rich("функция положения y_{D} = e·tg φ; скорость v_{D} и ускорение a_{D} — её производные по времени", 1500):
    p0.append(r)
# --- k: графики (бывший слайд 6 без комментариев)
shape(k, "Text 1").text_frame.paragraphs[0].runs[0].text = "Кинематический анализ: графики движения"
set_paras(shape(k, "строка_41"), label_para("Закон движения", "трапеция угловой скорости кулисы: разгон, постоянная "
                                                               "скорость, торможение при обжиме; скорость руки ≤ 0,7 м/с → "
                                                               "ω_{max} = 1,4 рад/с"))
# Корнеев 24.11 01:29: на слайде графиков — не формулы слайда 6, а закон движения кулисы (три слагаемых), ω, ε и формулы,
# по которым построены графики ползуна (fig/ф_кинематика7.png, make_kin7.py)
move(shape(k, "строка_39"), (0.82, 1.82, 3.21, 0.62))
# 01:43: блок «Закон движения» убран, список формул — на всю ширину панели
remove(shape(k, "строка_41"))
replace_pic(k, shape(k, "рис_40"), os.path.join(FIG, "ф_кинематика7.png"), (0.68, 2.6, 3.5, 3.3))
# результат — проверен пересчётом (ход 16,0 мм за 0,913 с; |vD|max 31,85 мм/с при t = 0,39 с; |aD|max 155,3 мм/с² при t = 0)
set_paras(shape(k, "текст_вывода_50"), [("", {})])
p0 = shape(k, "текст_вывода_50")._element.find(f".//{{{A}}}p")
p0.append(run_xml("Результат: ", True, 1500, "tx2"))
for r in rich("ход ползуна 16 мм за 0,9 с;  ω_{max} = 1,4 рад/с;  |v_{D}|_{max} = 31,9 мм/с;  |a_{D}|_{max} = 155,3 мм/с^{2}", 1500):
    p0.append(r)

# =============================================================== 7 — схемы звеньев (белые кружки)
s7 = S[6]
drop_comments(s7)
remove(shape(s7, "Рисунок 19"))
# один масштаб для всех трёх звеньев (как на общем рисунке)
LNK = [("рис_55", "звено1_v23.png", 0.75), ("рис_59", "звено2_v23.png", 4.88), ("рис_63", "звено3_v23.png", 9.01)]
for nm, f, x in LNK:                                # каждое звено — по своей рамке; камень не крупнее 2,1 дюйма
    hmax = 2.1 if "звено2" in f else 2.55
    replace_pic(s7, shape(s7, nm), os.path.join(FIG, f), (x, 2.05 + (2.55 - hmax) / 2, 3.58, hmax))
# Корнеев 24.11 01:51: при каком φ достигается P_max — φ_у = 41,63° (РПЗ п. 7.4), до десятых
NBS = " "
set_paras(shape(s7, "текст_вывода_66"), [("", {})])
p0 = shape(s7, "текст_вывода_66")._element.find(f".//{{{A}}}p")
p0.append(run_xml("Результат: ", True, 1500, "tx2"))
for r in rich(f"P_{{max}}{NBS}={NBS}112,8{NBS}Н{NBS}<{NBS}120{NBS}Н при φ{NBS}={NBS}φ_{{у}}{NBS}={NBS}41,6° (начало "
              f"пластической деформации), длина рукояти L{NBS}={NBS}500{NBS}мм", 1500):
    p0.append(r)

# =============================================================== 8 — эпюры: опасные сечения, критерии
s8 = S[7]
# Корнеев 24.11 02:00: заголовок «Прочностной расчёт: эпюры кулисы»; карточки 40,8 / 2430,5 убраны (они в результате);
# в постановке без «Схемы» и формулы; эпюры для обоих опасных положений — φу и φк (как рис. 13 и 14 РПЗ)
NBS = " "
shape(s8, "Text 1").text_frame.paragraphs[0].runs[0].text = "Прочностной расчёт: эпюры кулисы"
for n in ("значение_76", "число_77", "значение_78", "число_79", "число_81", "строка_70", "рис_71"):
    remove(shape(s8, n))
# Корнеев 02:09: постановку задачи убрать полностью — на слайде только эпюры (во всю ширину) и критерии для сечения
for n in ("постановка_67", "метка_68", "строка_69", "строка_72"):
    remove(shape(s8, n))
fr_u, cap_u = shape(s8, "рамка_73"), shape(s8, "подпись_75")
move(fr_u, (0.6, 1.25, 6.0, 3.55))
replace_pic(s8, shape(s8, "рис_74"), os.path.join(FIG, "эпюры_фи_у.png"), (0.68, 1.3, 5.84, 3.45))
move(cap_u, (0.6, 4.83, 6.0, 0.28))
set_paras(cap_u, [(f"Эпюры N, Q, M при φ_{{у}}{NBS}={NBS}41,6° — начало пластической деформации", dict(size=1100, color="accent2"))],
          algn="ctr")
copy_to(s8, fr_u, (6.73, 1.25, 6.0, 3.55))
add_pic(s8, os.path.join(FIG, "эпюры_фи_к_кружки.png"), (6.81, 1.3, 5.84, 3.45))
copy_to(s8, cap_u, (6.73, 4.83, 6.0, 0.28), [(f"Эпюры N, Q, M при φ_{{к}}{NBS}={NBS}22,7° — конец хода", dict(size=1100, color="accent2"))],
        algn="ctr")
move(shape(s8, "значение_80"), (0.6, 5.18, 12.13, 0.9))             # критерии — строкой под эпюрами (make_crit9.py)
copy_to(s8, lbl_ref, (0.75, 5.2, 2.0, 0.85), [("Критерии для сечения", dict(b=True, size=1300, color="tx2"))])
copy_to(s8, lbl_ref, (2.75, 5.2, 1.75, 0.85), [("Изгиб со сжатием (сечение D):", dict(size=1150))])
add_pic(s8, os.path.join(FIG, "ф_крит_изгиб.png"), (4.5, 5.24, 3.0, 0.78))
copy_to(s8, lbl_ref, (7.75, 5.2, 1.8, 0.85), [("Срез на участке O–D (Журавский):", dict(size=1150))])
add_pic(s8, os.path.join(FIG, "ф_крит_срез.png"), (9.6, 5.24, 2.4, 0.78))
set_paras(shape(s8, "текст_вывода_83"), [("", {})])
p0 = shape(s8, "текст_вывода_83")._element.find(f".//{{{A}}}p")
p0.append(run_xml("Результат: ", True, 1400, "tx2"))
for r in rich("опасное положение φ_{у}: сечение D — |M_{D}| = 40,8 Н·м (изгиб со сжатием), участок O–D — |Q| = 2430,5 Н (срез); "
              "при φ_{к} меньше: 28,3 Н·м и 2081,4 Н", 1400):
    p0.append(r)

# =============================================================== 9 — критерии, формулы, сечения
s9 = S[8]
shape(s9, "Text 1").text_frame.paragraphs[0].runs[0].text = "Прочностной расчёт: сечения звеньев"   # Корнеев 02:00
move(shape(s9, "постановка_84"), (0.6, 1.25, 3.65, 4.8))
remove(shape(s9, "рис_87"))
set_paras(shape(s9, "строка_86"), label_para("Условие прочности", "по пределу текучести, коэффициент запаса n = 2,5; "
                                                                   "допускаемые — [σ] = σ_{т}/n"))
move(shape(s9, "строка_86"), (0.82, 1.85, 3.21, 0.95))
set_paras(shape(s9, "строка_89"), [
    ("Опасные сечения и критерии", dict(b=True)),
    ("Кулиса — сечение D под камнем: изгиб со сжатием (|M|_{max}); участок O–D — срез (|Q|_{max})", {}),
    ("Шток — сжатие и устойчивость (конец хода, F_{ук})", {}),
    ("Ось O, палец D — срез по одной плоскости", {}),
    ("Отверстия кулисы и ползуна — смятие", {})], space=300)
move(shape(s9, "строка_89"), (0.82, 2.95, 3.21, 3.0))
# формулы — в середине, сечения и итоги — справа
move(shape(s9, "рамка_90"), (4.45, 1.25, 3.75, 4.5))
remove(shape(s9, "рис_91"))
add_pic(s9, os.path.join(FIG, "ф_проверки.png"), (4.57, 1.32, 3.51, 4.36))
cap9 = shape(s9, "подпись_92")
set_paras(cap9, [("Расчётные формулы", dict(size=1100, color="accent2"))], algn="ctr")
move(cap9, (4.45, 5.79, 3.75, 0.25))
copy_to(s9, frame_ref, (8.35, 1.25, 4.38, 1.95))
add_pic(s9, os.path.join(FIG, "сечения_v23.png"), (8.43, 1.32, 4.22, 1.62))
copy_to(s9, cap_ref, (8.35, 2.95, 4.38, 0.25), [("Принятые сечения (размеры в мм)", dict(size=1100, color="accent2"))],
        algn="ctr")
remove(shape(s9, "проверки"))                       # таблицу — убрать (замечание), итоги проверок — текстом
copy_to(s9, frame_ref, (8.35, 3.3, 4.38, 2.45))
copy_to(s9, lbl_ref, (8.48, 3.4, 4.15, 2.3), [
    ("Итоги проверок", dict(b=True, size=1300, color="tx2")),
    ("Кулиса 8 · 18: σ = 94,8 ≤ 98 МПа; τ = 25,3 ≤ 49 МПа", dict(size=1150)),
    ("Шток Ø8: λ = 60, F_{кр} = 12 144 Н, n_{у} = 6,2 ≥ 3", dict(size=1150)),
    ("Ось O / палец D Ø10: τ_{ср} = 31,0 / 32,0 ≤ 50 МПа", dict(size=1150)),
    ("Отверстие кулисы (ступица): σ_{см} = 12,2 ≤ 24 МПа", dict(size=1150)),
    ("Отверстие ползуна: σ_{см} = 15,7 ≤ 24 МПа", dict(size=1150))])

# =============================================================== 10 — схемы с силами тяжести и инерции
s10 = S[9]
replace_pic(s10, shape(s10, "рис_102"), os.path.join(FIG, "схемы_уточняющий_v23.png"), (4.52, 1.33, 3.61, 4.37))
set_paras(shape(s10, "строка_100"), label_para("Критерий", "изменение силы руки и реакций; проверка принятых сечений"))

# =============================================================== 11 — МКЭ: σэкв, крупные карты напряжений
s11 = S[10]
set_paras(shape(s11, "строка_112"), [("Критерий", dict(b=True)),
                                     ("σ_{экв} ≤ [σ] материала детали", {}),
                                     ("σ_{экв} — эквивалентные напряжения по энергетической теории прочности "
                                      "(Мизес), в APM — SVM", dict(size=1200))])
move(shape(s11, "строка_112"), (0.82, 2.71, 3.21, 1.6))
for n in ("рамка_114", "рис_115", "подпись_116", "рамка_117", "рис_118", "подпись_119", "рамка_120", "рис_121",
          "подпись_122", "рамка_123", "рис_124", "подпись_125", "значение_126", "число_127"):
    remove(shape(s11, n))
# Корнеев 23.11 23:22: без шкалы SVM — только деталь (fig/apm_*.png, crop_apm.py), под каждой картинкой max и min
# Корнеев 24.11 01:29: все значения — до десятых
MM = {"кулиса_2_тест": ("92,6", "0,0"), "кулиса_4_тест_новой_2": ("92,6", "0,0"),
      "ползун_2_тест": ("95,9", "0,0"), "ползун_4_тест_нового": ("49,0", "0,0"),
      "камень_2_тест": ("646,0", "0,0"), "камень_4_тест_итог": ("100,1", "0,0"),
      "направляющая_Б_тест": ("60,7", "0,0"),   # вариант Б: скрин Корнеева 23:22 — это направляющая «после», не камень
      "направляющая_2_тест": ("920,0", "0,0"), "направляющая_6_тест_с_винтом": ("136,2", "0,0")}   # значения со шкал APM
cards = [("Кулиса: σ_{экв} 92,6 → 92,6 МПа, масса −22 %", "кулиса_2_тест", "кулиса_4_тест_новой_2", True),
         ("Ползун: σ_{экв} 95,9 → 49,0 МПа", "ползун_2_тест", "ползун_4_тест_нового", False),
         ("Камень: σ_{экв} 646,0 → 100,1 МПа", "камень_2_тест", "камень_4_тест_итог", False),
         ("Направляющая: σ_{экв} 920,0 → 60,7 МПа", "направляющая_2_тест", "направляющая_Б_тест", False)]


def apm_pic(slide, name, box, tag):
    x, y, w, h = box
    LH = 0.21
    add_pic(slide, os.path.join(FIG, "apm_" + name + ".png"), (x, y, w, h - LH))
    mx, mn = MM[name]
    txt = f"{tag}: max {mx}, min {mn} МПа" if mx else tag
    copy_to(slide, cap_ref, (x - 0.05, y + h - LH, w + 0.1, LH), [(txt, dict(size=850, color="tx1"))], algn="ctr")


for i, (cap, a, b, stack) in enumerate(cards):
    x, y = 4.45 + (i % 2) * 4.19, 1.25 + (i // 2) * 2.45
    w, h = 4.09, 2.12
    copy_to(s11, frame_ref, (x, y, w, h))
    if stack:                                       # кулиса длинная — «до» над «после»
        apm_pic(s11, a, (x + 0.08, y + 0.05, w - 0.16, (h - 0.1) / 2), "до")
        apm_pic(s11, b, (x + 0.08, y + 0.05 + (h - 0.1) / 2, w - 0.16, (h - 0.1) / 2), "после")
    else:
        apm_pic(s11, a, (x + 0.06, y + 0.06, w / 2 - 0.09, h - 0.12), "до")
        apm_pic(s11, b, (x + w / 2 + 0.03, y + 0.06, w / 2 - 0.09, h - 0.12), "после")
    copy_to(s11, cap_ref, (x, y + h + 0.03, w, 0.26), [(cap, dict(size=1100, color="accent2"))], algn="ctr")
copy_to(s11, lbl_ref, (0.82, 4.45, 3.21, 1.4), [("Как читать", dict(b=True)),
                                                ("в каждой паре: слева/сверху — до доработки, справа/снизу — после; "
                                                 "под картинкой — наибольшее и наименьшее σ_{экв}", dict(size=1200))])
set_paras(shape(s11, "текст_вывода_129"), [("", {})])
p0 = shape(s11, "текст_вывода_129")._element.find(f".//{{{A}}}p")
p0.append(run_xml("Результат: ", True, 1500, "tx2"))
for r in rich("после доработки σ_{экв} ≤ [σ] у всех деталей", 1500):
    p0.append(r)

# =============================================================== 12 — до/после: кулиса светлая, направляющая нынешняя
s12 = S[11]
drop_comments(s12)
replace_pic(s12, shape(s12, "рис_136"), os.path.join(FIG, "фэм_после_кулиса_светл.png"), (0.68, 3.98, 2.69, 1.78))
replace_pic(s12, shape(s12, "рис_142"), os.path.join(FIG, "фэм_после_ползун_светл.png"), (3.78, 3.98, 2.69, 1.78))
replace_pic(s12, shape(s12, "рис_154"), os.path.join(FIG, "фэм_после_направляющая_Б.png"), (9.97, 3.98, 2.69, 1.78))
set_paras(shape(s12, "подпись_155"), [("Направляющая: полка с отверстием под шток, без планок", dict(size=1100,
                                                                                                    color="accent2"))],
          algn="ctr")
set_paras(shape(s12, "подпись_137"), [("Кулиса: облегчена: 577,6 → 449,7 г", dict(size=1100, color="accent2"))],
          algn="ctr")

# =============================================================== 4 и выводы — новые кинематические схемы (стиль образца)
s4 = S[3]
replace_pic(s4, shape(s4, "рис_3"), os.path.join(FIG, "схема_постановка.png"), (0.68, 1.31, 4.34, 4.36))
for n in ("Прямая со стрелкой 23", "Прямая со стрелкой 25", "Прямая со стрелкой 29"):   # набросок контура Корнеева —
    remove(shape(s4, n))                                                                 # контур теперь на слайде 6
s13 = S[12]
# слайд «Выводы»: Корнеев 23.11 23:04 — «верни на 14 слайд скрин сборки, а не схемы» → его картинка рис_161 остаётся
set_paras(shape(s13, "подпись_160"), [("Итоговый вид сборки укупоривателя", dict(size=1100, color="accent2"))], algn="ctr")

# =============================================================== 5 — синтез: схема с треугольником O–Bн–Bк (Корнеев 23:56:
# «вставь на 5 слайд, убери постановку задачи и напиши её снизу, но результат не удаляй»)
s5 = S[4]
def fit_shape(sh, box):
    l, t, w, h = box
    k = min(w / (sh.width / 914400), h / (sh.height / 914400))
    nw, nh = sh.width / 914400 * k, sh.height / 914400 * k
    move(sh, (l + (w - nw) / 2, t + (h - nh) / 2, nw, nh))
TOP, HT = 1.25, 3.38
copy_to(s5, shape(s5, "рамка_29"), (0.6, TOP, 3.0, HT))
add_pic(s5, os.path.join(FIG, "схема_синтез.png"), (0.68, TOP + 0.06, 2.84, HT - 0.12))
copy_to(s5, shape(s5, "подпись_31"), (0.6, TOP + HT + 0.03, 3.0, 0.28),
        [("Треугольник O–B_{н}–B_{к} и угол ψ", dict(size=1100, color="accent2"))], algn="ctr")
move(shape(s5, "рамка_29"), (3.75, TOP, 5.05, HT)); fit_shape(shape(s5, "рис_30"), (3.83, TOP + 0.06, 4.89, HT - 0.12))
move(shape(s5, "подпись_31"), (3.75, TOP + HT + 0.03, 5.05, 0.28))
move(shape(s5, "рамка_32"), (8.95, TOP, 3.78, HT)); fit_shape(shape(s5, "рис_33"), (9.03, TOP + 0.06, 3.62, HT - 0.12))
move(shape(s5, "подпись_34"), (8.95, TOP + HT + 0.03, 3.78, 0.28))
# постановка задачи — полосой снизу, над «Результатом»
move(shape(s5, "постановка_22"), (0.6, 5.0, 12.13, 1.15))
move(shape(s5, "метка_23"), (0.78, 5.02, 3.5, 0.3))
# 24.11 Корнеев 01:09: белую рамку с формулами (рис_25) убрать — формула S перенесена на схему слева (make_synth.py);
# четыре колонки — на всю ширину синей полосы
for n, box, lab, txt in (("строка_24", (0.78, 5.32, 2.9, 0.8), "Что делаем", "выбираем окно качания φ_{н} → φ_{к} и расстояние e"),
                         ("строка_26", (3.78, 5.32, 3.1, 0.8), "Критерии", "минимум площади треугольника O–B_{н}–B_{к} и углового хода ψ"),
                         ("строка_27", (6.98, 5.32, 2.7, 0.8), "Ограничения", "P ≤ 120 Н, L ≤ 500 мм, e ≥ 10 мм"),
                         ("строка_28", (9.78, 5.32, 2.85, 0.8), "Метод", "компромисс — точка равных относительных уступок")):
    sh_ = shape(s5, n); move(sh_, box)
    set_paras(sh_, [(lab, dict(b=True, size=1150)), (txt, dict(size=1100))])
remove(shape(s5, "рис_25"))
# результат синтеза — найденные величины (Корнеев 24.11 01:09: «φк = …, φн = …, e = …, угол = 36,8»)
set_paras(shape(s5, "текст_вывода_36"), [("", {})])
p0 = shape(s5, "текст_вывода_36")._element.find(f".//{{{A}}}p")
p0.append(run_xml("Результат: ", True, 1500, "tx2"))
for r in rich("φ_{к} = 22,7°,  φ_{н} = 59,5°,  e = 12,5 мм,  ψ = φ_{н} − φ_{к} = 36,8°", 1500):   # до десятых (Корнеев 01:29)
    p0.append(r)

# =============================================================== 2 — цель: «повысить», а не «повышение» (Корнеев 23:58)
for sh_ in S[1].shapes:
    if sh_.has_text_frame:
        for para in sh_.text_frame.paragraphs:
            rs = para.runs
            for k, r in enumerate(rs):
                if r.text == "Повышение" and k + 1 < len(rs) and rs[k + 1].text.startswith(" производительности"):
                    r.text = "Повысить"
                    rs[k + 1].text = rs[k + 1].text.replace(" производительности", " производительность", 1)

# =============================================================== 4 — убрать результат и формулу F_ук (они на слайде 3) — Корнеев 23:59
for n in ("рис_19", "вывод_20", "текст_вывода_21"):
    remove(shape(S[3], n))

prs.save(OUT)
print("сохранено:", OUT, "слайдов:", len(prs.slides))
