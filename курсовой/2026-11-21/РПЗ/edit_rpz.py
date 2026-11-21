# -*- coding: utf-8 -*-
"""21.11 — правки РПЗ v13 (Корнеев А.Е.) по замечаниям преподавателя; исходник — РПЗ_v13_исходник.docx, результат —
РПЗ_укупориватель.docx (оформление v13 сохраняется: новые абзацы — копии соседних):
  1) в начало введения — исходная схема кулисно-рычажного (тангенсного) механизма из справочника Артоболевского (картинка
     из образца РПЗ РК6-52Б-1, тот же механизм) со ссылкой на источник;
  2) ссылки на источники [N] там, где взяты данные (ГОСТы и т. д.);
  3) эргономика — по требованиям промышленной безопасности (ССБТ): ГОСТ 12.2.064-81 п. 1.5, ГОСТ 12.2.049-80 п. 4.3;
     в список источников добавлены они и Артоболевский;
  4) n — без квадратных скобок (коэффициент запаса — не допускаемая величина): формула [σ] = σт/n и подпись таблицы 8;
  5) рисунок 2 — кинематическая схема без численных значений и без e, S, штриховка неподвижного звена в одну сторону (ЕСКД);
     схема с размерами по результатам расчёта — новый рисунок 16 в разделе 10, следующие рисунки 16…22 → 17…23.
    python edit_rpz.py"""
import copy, io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import docx
from docx.oxml.ns import qn
from docx.shared import Emu
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "РПЗ_v13_исходник.docx"), os.path.join(HERE, "РПЗ_укупориватель.docx")
FIG = os.path.join(HERE, "..", "Презентация", "fig")
ARTOB = os.path.join(HERE, "артоболевский_тангенсный.jpg")   # 21.11: картинка от Корнеева А.Е. (вместо схемы из образца 52Б)
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

d = docx.Document(SRC)
body = d.element.body
tx = lambda el: "".join((x.text or "") for x in el.iter() if x.tag in (qn("w:t"), M + "t"))
paras = lambda: list(body.iterchildren(qn("w:p")))


def find(prefix, n=1):
    r = [p for p in paras() if tx(p).startswith(prefix)]
    assert len(r) == n, (prefix, len(r))
    return r[0] if n == 1 else r


def append_text(p, s):
    """дописать текст в конец абзаца — новым прогоном с форматом последнего текстового прогона"""
    runs = [r for r in p.iterchildren(qn("w:r")) if r.find(qn("w:t")) is not None]
    nr = copy.deepcopy(runs[-1]) if runs else p.makeelement(qn("w:r"), {})
    for t in nr.findall(qn("w:t")):
        nr.remove(t)
    t = nr.makeelement(qn("w:t"), {})
    t.text = s
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    nr.append(t)
    p.append(nr)


def replace_in(p, old, new):
    for t in p.iter(qn("w:t"), M + "t"):
        if t.text and old in t.text:
            t.text = t.text.replace(old, new)
            return True
    return False


def clone_text_par(proto, after, text):
    """новый абзац с оформлением proto (без рисунков и формул), вставляется после after"""
    np_ = copy.deepcopy(proto)
    for ch in list(np_):
        if ch.tag != qn("w:pPr"):
            np_.remove(ch)
    r = np_.makeelement(qn("w:r"), {})
    rpr = proto.find(".//" + qn("w:r") + "/" + qn("w:rPr"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = r.makeelement(qn("w:t"), {})
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    np_.append(r)
    after.addnext(np_)
    return np_


def picture_par(proto_pic, after, img_path, width_emu):
    """абзац-рисунок: копия proto_pic (рисунок по центру), картинка заменена на img_path, ширина width_emu"""
    np_ = copy.deepcopy(proto_pic)
    rid, _ = d.part.get_or_add_image(img_path)
    w, h = Image.open(img_path).size
    blip = np_.find(".//" + A + "blip")
    blip.set(qn("r:embed"), rid)
    cy = int(width_emu * h / w)
    for ext in np_.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent", A + "ext"):
        ext.set("cx", str(int(width_emu))); ext.set("cy", str(cy))
    docpr = np_.find(".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr")
    if docpr is not None:
        docpr.set("id", str(9000 + len(paras())))
        docpr.set("name", os.path.basename(img_path))
    after.addnext(np_)
    return np_


def pic_par_before(caption_par):
    p = caption_par.getprevious()
    assert p.find(".//" + A + "blip") is not None, tx(caption_par)
    return p


def extent_cx(pic_p):
    return int(pic_p.find(".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent").get("cx"))


# ------------------------------------------------------------- 5) рисунки: схема без чисел вместо рис. 2, схема с размерами в разд. 10
cap2 = find("Рисунок 2 —")
pic2 = pic_par_before(cap2)
wide = extent_cx(pic2)
new2 = picture_par(pic2, pic2, os.path.join(FIG, "схема_постановка.png"), int(wide * 0.62))
body.remove(pic2)
# перенумерация рисунков 16…22 → 17…23 (подписи; ссылок на них в тексте нет — проверено)
for p in paras():
    m = re.match(r"Рисунок (\d+)", tx(p))
    if m and 16 <= int(m.group(1)) <= 22:
        assert replace_in(p, m.group(1), str(int(m.group(1)) + 1)), tx(p)
refs = [tx(p) for p in paras() if re.search(r"рисун\w*\s+(1[6-9]|2[0-3])\b", tx(p))]
assert not refs, refs
t18 = find("Таблица 18 —").getnext()                     # таблица 18
assert t18.tag == qn("w:tbl")
lead = clone_text_par(find("Сила руки и реакции показаны"), t18,
                      "Схема механизма с размерами, полученными в расчётах, приведена на рисунке 16.")
pres_pic = picture_par(new2, lead, os.path.join(FIG, "схема_результат.png"), int(wide * 0.55))
clone_text_par(cap2, pres_pic, "Рисунок 16 — Кинематическая схема механизма с принятыми размерами")

# ------------------------------------------------------------- 1) Артоболевский — в начало введения
intro = next(p for p in paras() if tx(p) == "Введение")
cap0 = find("Укупориватель без кожуха")
pic0 = pic_par_before(cap0)
lead_a = clone_text_par(find("Укупориватель предназначен"), intro,
                        "Исходная схема проекта — тангенсный механизм из справочника И.И. Артоболевского [24]: кулиса качается "
                        "на неподвижном шарнире, палец ползуна скользит в её прорези, ползун движется в направляющих; перемещение "
                        "ползуна пропорционально тангенсу угла поворота кулисы. В проекте ползун движется вертикально, а вместо "
                        "прорези по кулисе скользит камень, шарнирно связанный с ползуном (раздел 3).")
pa = picture_par(pic0, lead_a, ARTOB, int(extent_cx(pic2) * 0.42))
cap_a = clone_text_par(cap0, pa, "Тангенсный механизм по [24]")
cap_a.replace(cap_a.find(qn("w:pPr")), copy.deepcopy(cap2.find(qn("w:pPr"))))   # подпись — как у рисунков: по центру
# 21.11 (Корнеев А.Е.): рендер «Укупориватель без кожуха…» во введении (стр. 6) убрать
body.remove(pic0)
body.remove(cap0)

# ------------------------------------------------------------- 3) эргономика по ССБТ
perg = find("Допустимая сила руки")
clone_text_par(find("Укупориватель предназначен"), perg,
               "Требования промышленной безопасности к органам управления: усилия на органах управления устанавливают с учётом "
               "способа перемещения, частоты использования и положения человека (ГОСТ 12.2.049-80, п. 4.3 [23]); они не должны "
               "превышать допустимые нагрузки на двигательный аппарат человека, а их значения задаются для оборудования "
               "конкретного вида (ГОСТ 12.2.064-81, п. 1.5 [22]). Численные ориентиры: ГОСТ 21753-76, табл. 2 [5] — 39 Н "
               "(всей рукой, 17–240 раз в смену) и 137 Н (двумя руками, реже 5 раз в смену); ГОСТ Р ЕН 1005-3-2010, табл. 1 [4] — "
               "44 / 75 Н (одной рукой вниз, бытовое / профессиональное применение). Принято Pдоп = 120 Н — по замеру силы руки "
               "на серийном ручном укупоривателе [12]; это не больше 137 Н по ГОСТ 21753-76.")

# ------------------------------------------------------------- 2) ссылки на источники
append_text(find("Объект проектирования"), " [1, 7]")
# 21.11 (Корнеев А.Е.): у основных требований и исходных данных — столбец «Источник» по каждой строке (как в v30)
def add_column(tbl, values, frac=0.2):
    grid = tbl.find(qn("w:tblGrid"))
    cols = grid.findall(qn("w:gridCol"))
    tot = sum(int(c.get(qn("w:w"))) for c in cols)
    new_w = int(tot * frac)
    for c in cols:
        c.set(qn("w:w"), str(int(int(c.get(qn("w:w"))) * (1 - frac))))
    nc = copy.deepcopy(cols[-1]); nc.set(qn("w:w"), str(new_w)); grid.append(nc)
    rows = tbl.findall(qn("w:tr"))
    assert len(rows) == len(values), (len(rows), len(values))
    for tr, v in zip(rows, values):
        tcs = tr.findall(qn("w:tc"))
        for tc in tcs:
            w = tc.find(qn("w:tcPr") + "/" + qn("w:tcW"))
            if w is not None and w.get(qn("w:type")) in (None, "dxa"):
                w.set(qn("w:w"), str(int(int(w.get(qn("w:w"))) * (1 - frac))))
        nt = copy.deepcopy(tcs[-1])
        w = nt.find(qn("w:tcPr") + "/" + qn("w:tcW"))
        if w is not None:
            w.set(qn("w:w"), str(new_w)); w.set(qn("w:type"), "dxa")
        ps = nt.findall(qn("w:p"))
        for extra in ps[1:]:
            nt.remove(extra)
        p0 = ps[0]
        for ch in list(p0):
            if ch.tag != qn("w:pPr"):
                p0.remove(ch)
        r = p0.makeelement(qn("w:r"), {})
        src_r = tcs[-1].find(".//" + qn("w:r") + "/" + qn("w:rPr"))
        if src_r is not None:
            r.append(copy.deepcopy(src_r))
        t = r.makeelement(qn("w:t"), {}); t.text = v
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); r.append(t); p0.append(r)
        tr.append(nt)


t_req = find("Основные требования").getnext()
assert t_req.tag == qn("w:tbl")
add_column(t_req, ["Источник", "ISO 12821 [7]; ТЗ", "ГОСТ 32624-2020 [1]", "ГОСТ 13345-85 [2]; EN 10202 [9]",
                   "ССБТ [22, 23]; [4, 5, 12]", "ТЗ", "ТЗ; STLB [8]", "принято: 1,5 диаметра бутылки", "принято (габарит)",
                   "принято; ГОСТ 6636-69 [3]"], 0.24)
t_dat = find("Таблица 1 —").getnext()
assert t_dat.tag == qn("w:tbl")
add_column(t_dat, ["Источник", "EN 10202 [9] (допущение)", "указание преподавателя", "ГОСТ 32624-2020, табл. 1 [1]",
                   "STLB, прил. 6 [8]", "ГОСТ 13345-85 [2]", "формула силы штамповки [10]", "ГОСТ 32624-2020, табл. 1 [1]",
                   "замер [12]; [4, 5, 22, 23]", "принято; ГОСТ 6636-69 [3]", "принято (≤ hk)", "ГОСТ 6636-69 [3]",
                   "принято (габарит)", "принято (конструктивно)", "принято", "результат синтеза (п. 5.4)", "ТЗ",
                   "Фех А.И., с. 46 [6]", "справочное значение [20]"], 0.26)
append_text(find("Рисунок 1 —"), " (размеры крышки и венчика — по ГОСТ 32624-2020 [1] и ISO 12821 [7])")
append_text(find("Обжим уменьшает наружный диаметр"), " [1, 8]")
append_text(find("Коэффициент n"), " [10]")
append_text(find("Расчётное усилие обжима 1974"), " Значение согласуется с опубликованными данными о силе укупоривания [11, 12].")
append_text(find("Таблица 4 —"), " [3]")
append_text(find("Первичный расчёт выполнен"), " [13]")
append_text(find("Условие прочности при сжатии"), " [20]")
append_text(find("Толщину листа выбирают"), " [14, 15]")
append_text(find("Таблица 8 —"), " [16–19]")
append_text(find("Для Ст3 приняты"), " [20]")
p_aut = find("Ось O выполнена из стали 45")
assert replace_in(p_aut, "(Autodesk Inventor Help)", "[21]") or replace_in(p_aut, "Autodesk Inventor Help", "[21]"), tx(p_aut)
append_text(find("Уточнение выполняется методом кинетостатики"), " [13]")

# 21.11 (Корнеев А.Е.): «пазов облегчения» нет — убрать термин
p_k = find("– кулиса — полоса")
assert replace_in(p_k, " и пазами облегчения", ""), tx(p_k)
p_c = next(p for p in paras() if "Кулиса: 92,6" in tx(p))
assert replace_in(p_c, "девять пазов облегчения, ", ""), tx(p_c)
assert not any("паз" in tx(p) and "облегч" in tx(p) for p in paras())
# рис. 13 (продолжение): метки сечений Б–Б и В–В разнесены (fix_fig13.py)
cap13 = find("Рисунок 13 (продолжение)")
blip13 = pic_par_before(cap13).find(".//" + A + "blip")
d.part.related_parts[blip13.get(qn("r:embed"))]._blob = open(os.path.join(HERE, "рисунки", "рис13_продолжение.png"), "rb").read()

# ------------------------------------------------------------- 4) n без скобок
for prefix in ("[σ]=σт[n]", "Таблица 8 —"):
    p = find(prefix)
    for t in p.iter(qn("w:t"), M + "t"):
        if t.text and "[n]" in t.text:
            t.text = t.text.replace("[n]", "n")
    assert "[n]" not in tx(p), tx(p)

# запас устойчивости nу — тоже без скобок (в скобках — только допускаемые величины): «nу = Fкр/Fук ≥ [nу] = 3» → «… ≥ 3»,
# в таблице 17 «[nу] = 3» → «nу ≥ 3»
fixed = 0
for p in body.iter(qn("w:p")):
    ts = [t for t in p.iter(qn("w:t"), M + "t") if t.text]
    for i in range(len(ts) - 3):
        if ts[i].text.endswith("[") and ts[i + 1].text == "n" and ts[i + 2].text == "у" and ts[i + 3].text.startswith("]=3"):
            if ts[i].text.endswith("≥["):                 # в формуле: оставить «≥ 3»
                ts[i].text = ts[i].text[:-1]; ts[i + 1].text = ""; ts[i + 2].text = ""; ts[i + 3].text = ts[i + 3].text[2:]
            else:                                         # в таблице: «nу ≥ 3»
                ts[i].text = ts[i].text[:-1]; ts[i + 3].text = "≥3" + ts[i + 3].text[3:]
            fixed += 1
assert fixed == 2 and "[nу]" not in "".join(t.text or "" for t in body.iter(qn("w:t"), M + "t")), fixed
print("nу без скобок:", fixed)

# ------------------------------------------------------------- новые источники (22–24) — копии последнего пункта списка
last = find("Autodesk Inventor Help.")
srcs = ["ГОСТ 12.2.064-81 «ССБТ. Органы управления производственным оборудованием. Общие требования безопасности» — п. 1.5. "
        "meganorm.ru/Data2/1/4294839/4294839117.htm",
        "ГОСТ 12.2.049-80 «ССБТ. Оборудование производственное. Общие эргономические требования» — п. 4.3. "
        "meganorm.ru/Data1/17/17568/index.htm",
        "Артоболевский И.И. Механизмы в современной технике: справочное пособие. В 7 т. Т. 2: Кулисно-рычажные и "
        "кривошипно-ползунные механизмы. — 2-е изд., перераб. — М.: Наука, 1979."]
prev = last
for s in srcs:
    prev = clone_text_par(last, prev, s)
# список источников в v13 без номеров — ссылкам [N] нужны номера: «N. » в начало каждого пункта
head = find("Список использованных источников", 2)[1]
items = []
p = head.getnext()
while p is not None:
    if p.tag == qn("w:p") and tx(p).strip():
        items.append(p)
    p = p.getnext()
for i, p in enumerate(items, 1):
    t = next(t for t in p.iter(qn("w:t")) if t.text)
    t.text = f"{i}. " + t.text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
assert tx(items[20]).startswith("21. Autodesk") and len(items) == 24, (len(items), tx(items[20])[:30])
print("пунктов в списке источников:", len(items))
# задание: объём РПЗ и число слайдов (страниц — после пересчёта в Word, 47)
pz = find("Расчётно-пояснительная записка на")
assert replace_in(pz, "45", "47") and replace_in(pz, "12 слайдов", "13 слайдов") or "13 слайдов" in tx(pz), tx(pz)
print("задание:", tx(pz))
d.save(OUT)
print("сохранено:", OUT)
