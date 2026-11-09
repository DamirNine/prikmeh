# -*- coding: utf-8 -*-
"""Расчёт v26 из v24 по замечаниям преподавателя (в оформлении v24: выносные формулы — картинки из LaTeX с исходником в описании,
символы в тексте — формулы Word, обозначения — 10 пт, рисунки — PNG с подписью «Рисунок N — …»):
  1) срез в одной плоскости: звенья лежат в параллельных плоскостях — число плоскостей среза i убрано из формул и текста;
  2) устойчивость штока: I → I_min — минимальный осевой момент инерции сечения; два способа обеспечить устойчивость
     (увеличить размер или сменить материал) и выбор;
  3) логика «рисунок → уравнения → матрица → решение» в разделах 11 и 13 (схемы перед уравнениями, итог о числе уравнений —
     в конце уравнений, «система решена…» — в разделе решения);
  4) головка: не плоское дно, а коническая горловина — новый рисунок 1 в п. 3.3 с распределённым давлением и его
     равнодействующей; остальные рисунки сдвинуты на +1.
Меняется только word/document.xml (+ новые картинки и связи к ним); остальные части файла копируются как есть.
    python -I build_v26.py v24.docx v26.docx fig_crimp.png"""
import copy, io, os, re, sys, zipfile
from lxml import etree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC, DST, FIG = sys.argv[1], sys.argv[2], sys.argv[3]
EQ_DIR = os.path.join(os.path.dirname(os.path.abspath(DST)), "eq_v26")
os.makedirs(EQ_DIR, exist_ok=True)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
W14 = "{http://schemas.microsoft.com/office/word/2010/wordml}"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
XS = "{http://www.w3.org/XML/1998/namespace}space"
NSDECL = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
          'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')

zin = zipfile.ZipFile(SRC)
root = etree.fromstring(zin.read("word/document.xml"))
rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
P = list(root.iter(W + "p"))                              # абзацы v24 по номерам; объекты сохраняются при перестановках
txt = lambda p: "".join(t.text or "" for t in p.iter(W + "t"))
new_media, log = {}, []


def expect(i, start):
    assert txt(P[i]).startswith(start), (i, txt(P[i])[:80], start)
    return P[i]


def replace(p, old, new):
    """заменить old в тексте абзаца (текст может быть разбит на несколько w:t; формулы Word не затрагиваются)"""
    nodes = list(p.iter(W + "t"))
    text = "".join(t.text or "" for t in nodes)
    start = text.find(old)
    assert start >= 0 and text.count(old) == 1, (old, text[:120])
    end, pos, done = start + len(old), 0, False
    for t in nodes:
        s = t.text or ""
        a, b = pos, pos + len(s)
        pos = b
        if b <= start or a >= end:
            continue
        t.text = s[:max(start - a, 0)] + ("" if done else new) + (s[max(end - a, 0):] if b > end else "")
        t.set(XS, "preserve")
        done = True
    log.append((old, new))


# ---------------------------------------------------------------- формулы Word в тексте
def omml_sub(base, sub, upright_sub=True):
    sub_r = (f'<m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:lang w:val="ru-RU"/></w:rPr><m:t>{sub}</m:t></m:r>' if upright_sub else
             f'<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>{sub}</m:t></m:r>')
    return etree.fromstring(
        f'<m:oMath {NSDECL}><m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
        f'</m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>{base}</m:t>'
        f'</m:r></m:e><m:sub>{sub_r}</m:sub></m:sSub></m:oMath>')


def strip_ids(el):
    for e in el.iter():
        for a in (W14 + "paraId", W14 + "textId"):
            e.attrib.pop(a, None)
    return el


def text_para(template, parts, run_rpr=None):
    """новый абзац с оформлением абзаца template: строки — обычный текст (rPr первого прогона template), кортежи — (основа, индекс)"""
    p = strip_ids(copy.deepcopy(template))
    ppr = p.find(W + "pPr")
    rpr = copy.deepcopy(run_rpr if run_rpr is not None else template.find(".//" + W + "r/" + W + "rPr"))
    for ch in list(p):
        if ch is not ppr:
            p.remove(ch)
    for part in parts:
        if isinstance(part, tuple):
            p.append(omml_sub(*part))
        else:
            r = etree.SubElement(p, W + "r")
            r.append(copy.deepcopy(rpr))
            t = etree.SubElement(r, W + "t")
            t.text = part
            t.set(XS, "preserve")
    return p


# ---------------------------------------------------------------- картинки: формулы и рисунок
def add_media(png, name):
    target = f"media/{name}"
    new_media[f"word/{target}"] = png
    rid = f"rIdV25{len(new_media)}"
    etree.SubElement(rels, "{%s}Relationship" % PR, Id=rid, Type=R[1:-1] + "/image", Target=target)
    return rid


DOCPR = [int(d.get("id")) for d in root.iter(WP + "docPr")]
next_id = iter(range(max(DOCPR) + 1, max(DOCPR) + 1000))


def set_picture(p, png, name, cx, descr=None):
    """заменить картинку в абзаце p: новая связь, размеры по пропорциям, описание"""
    im = Image.open(io.BytesIO(png))
    cy = round(cx * im.size[1] / im.size[0])
    rid = add_media(png, name)
    d = p.find(".//" + W + "drawing")
    d.find(".//" + A + "blip").set(R + "embed", rid)
    for e in (d.find(".//" + WP + "extent"), d.find(".//" + A + "xfrm/" + A + "ext")):
        e.set("cx", str(cx)); e.set("cy", str(cy))
    dp = d.find(".//" + WP + "docPr")
    dp.set("id", str(next(next_id)))
    dp.set("name", f"Picture {dp.get('id')}")
    if descr is not None:
        dp.set("descr", descr)
    d.find(".//" + PIC + "cNvPr").set("name", name)


matplotlib.rcParams["mathtext.fontset"] = "cm"


def render(latex, name):
    """формула в стиле v24: шрифт Computer Modern, кириллица — шрифтом-заменителем, 12 пт, 600 dpi, дроби — выносные"""
    s = re.sub(r"\\operatorname\{(\w+)\}", r"\\mathrm{\1}", latex)
    s = s.replace(r"\text{", r"\mathrm{").replace(r"\lbrack", "[").replace(r"\rbrack", "]").replace(r"\frac", r"\dfrac")
    fig = plt.figure()
    fig.text(0, 0, "$" + s + "$", fontsize=12)
    buf = io.BytesIO()
    fig.savefig(buf, dpi=600, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    png = buf.getvalue()
    open(os.path.join(EQ_DIR, name), "wb").write(png)
    return png, Image.open(io.BytesIO(png)).size[0] * 1524        # 600 dpi: 1 пиксель = 1524 EMU


def set_formula(p, latex, name):
    png, cx = render(latex, name)
    set_picture(p, png, name, cx, "LaTeX: " + latex)


def formula_descr(p):
    return p.find(".//" + WP + "docPr").get("descr")[len("LaTeX: "):]


def edit_formula(p, old, new, name):
    latex = formula_descr(p)
    assert latex.count(old) == 1, (old, latex)
    set_formula(p, latex.replace(old, new), name)
    log.append((old, new))


def formula_para(latex, name):
    p = strip_ids(copy.deepcopy(P[1250]))                  # абзац формулы: по центру, отступы как у остальных
    set_formula(p, latex, name)
    return p


def after(anchor, *new):
    for el in reversed(new):
        anchor.addnext(el)
    return new[-1]


# ================================================================ 0. абзацы v24, с которыми работаем (проверка текста)
H33 = expect(184, "3.3. Расчётная схема: обжим юбки крышки")
expect(185, "Обжим уменьшает наружный диаметр юбки")
FIG_T, CAP_T, NOTE_T, BODY_T = P[250], P[251], P[178], P[185]
assert P[250].find(".//" + W + "drawing") is not None and txt(P[251]).startswith("Рисунок 1 —")

# ================================================================ 1. рисунки: подписи и ссылки +1 (до вставки нового рисунка 1)
caps = [p for p in P if re.match(r"Рисунок (\d+) —", txt(p))]
assert [int(re.match(r"Рисунок (\d+)", txt(p)).group(1)) for p in caps] == list(range(1, 15))
for p in reversed(caps):
    n = int(re.match(r"Рисунок (\d+)", txt(p)).group(1))
    replace(p, f"Рисунок {n} —", f"Рисунок {n + 1} —")
for i, old, new in ((334, "на рисунке 2;", "на рисунке 3;"), (340, "На рисунке 3 ", "На рисунке 4 "),
                    (702, "рисунка 6)", "рисунка 7)"), (718, "На рисунке 7 ", "На рисунке 8 "),
                    (881, "на рисунке 9 ", "на рисунке 10 "), (1067, "на рисунках 10 и 11", "на рисунках 11 и 12"),
                    (1527, "на рисунке 14 (первичного — на рисунке 9)", "на рисунке 15 (первичного — на рисунке 10)")):
    replace(P[i], old, new)

# ================================================================ 4. головка: коническая горловина, новый рисунок 1 в п. 3.3
fig_p = strip_ids(copy.deepcopy(FIG_T))
for br in fig_p.iter(W + "lastRenderedPageBreak"):
    br.getparent().remove(br)
set_picture(fig_p, open(FIG, "rb").read(), "fig_crimp_v26.png", 5760000)          # 16 см, как рисунки схем
cap_rpr = CAP_T.find(".//" + W + "r/" + W + "rPr")
cap_p = text_para(CAP_T, ["Рисунок 1 — Обжим крышки конической горловиной головки: а) половина осевого сечения в процессе "
                          "обжима; б) давление на элемент юбки. q — давление горловины на юбку; ", ("F", "ук"),
                          " — его осевая равнодействующая."], cap_rpr)
body_rpr = BODY_T.find(".//" + W + "r/" + W + "rPr")
note_rpr = NOTE_T.find(".//" + W + "r/" + W + "rPr")
after(H33,
      text_para(BODY_T, ["Головка обжимает крышку не плоским дном, а конической горловиной (рисунок 1). Образующая конуса "
                         "наклонена к оси под углом α = 16,3° (п. 9.2). При ходе головки вниз горловина прижимает юбку к "
                         "горлышку; давление q распределено по поверхности контакта и направлено по нормали к образующей."],
                body_rpr),
      fig_p, cap_p,
      text_para(BODY_T, ["Радиальные составляющие давления q·cos α обжимают юбку и по окружности взаимно уравновешиваются. "
                         "Осевые составляющие q·sin α складываются в силу сопротивления обжиму, приложенную к головке снизу "
                         "вверх:"], body_rpr),
      formula_para(r"F_{\text{ук}} = \int_{A_{\text{к}}} q \cdot \sin\alpha \, dA", "eq_v26_crimp.png"),
      text_para(NOTE_T, ["Обозначения: q — давление горловины на юбку; α — угол конуса горловины; ", ("A", "к"),
                         " — площадь контакта горловины с юбкой; dA — её элемент. На цилиндрическом участке горловины давление "
                         "направлено радиально и осевой силы не создаёт. Величина ", ("F", "ук"),
                         " оценивается ниже по деформации юбки."], note_rpr))
replace(expect(691, "Внешние силы: сопротивление крышки"), "действует на ползун снизу вверх;",
        "действует на ползун снизу вверх (осевая равнодействующая давления горловины на юбку, рисунок 1);")

# ================================================================ 3. логика «рисунок → уравнения → матрица → решение»
# раздел 11: схемы (рис. 8) остаются в конце п. 11.3 — перед уравнениями; уравнения ссылаются на них
expect(718, "На рисунке 8 показаны звенья"), expect(728, "Рисунок 8 —")
replace(expect(730, "Для каждого звена записываются"), "Для каждого звена записываются",
        "По расчётным схемам рисунка 8 для каждого звена записываются")
p859 = expect(859, "Вывод. Три уравнения равновесия")
replace(p859, " Строки сил и моментов имеют разные физические размерности.", "")
after(expect(744, ""), p859)                            # итог о числе уравнений — в конце п. 11.4
assert txt(P[744]).startswith("[") or "моменты реакций поступательных пар" in txt(P[744])
note_matrix = expect(858, "Обозначения: A — матрица коэффициентов")
replace(note_matrix, "P — сила руки.", "P — сила руки. Строки сил и моментов имеют разные физические размерности.")
p860 = expect(860, "Система решена для 40 001 положения")
after(expect(861, "11.6. Решение через угол φ"), p860)  # численное решение — в разделе решения
# раздел 13: схемы с силами тяжести и инерции — в конце п. 13.3, после сил инерции и таблицы 19, прямо перед уравнениями
fig13, cap13 = P[1413], expect(1414, "Рисунок 14 —")
assert fig13.find(".//" + W + "drawing") is not None
p1493 = expect(1493, "Уравнения равновесия звеньев записываются так же")
intro13 = text_para(p1493, ["Расчётные схемы звеньев с силами тяжести и инерции показаны на рисунке 14; обозначения и "
                            "направления составляющих заданы выше в этом пункте."], p1493.find(".//" + W + "r/" + W + "rPr"))
after(expect(1491, "Это малые величины относительно рабочих сил"), intro13, fig13, cap13)
assert txt(cap13.getnext()).startswith("13.4. Уравнения равновесия")
replace(p1493, "Уравнения равновесия звеньев записываются так же", "По схемам рисунка 14 уравнения равновесия звеньев записываются так же")
p1509 = expect(1509, "Система решена для тех же 40 001")
after(expect(1510, "13.5. Решение через угол φ"), p1509)

# ================================================================ 1. срез в одной плоскости
replace(expect(1249, "Расчётные реакции при"), "В формулах i — число плоскостей среза, l — длина отверстия",
        "Звенья механизма лежат в параллельных плоскостях, поэтому ось O и палец D срезаются в одной плоскости. "
        "В формулах l — длина отверстия")
edit_formula(P[1250], r"\frac{4R}{i\,\pi d^{2}}", r"\frac{4R}{\pi d^{2}}", "eq_v26_shear.png")
replace(expect(1251, "Обозначения: R — нагрузка на проверяемое соединение"), "i — число плоскостей среза; ", "")
replace(expect(1255, "Диаметр оси и пальца — из условия среза"), "(i = 1):", "в одной плоскости:")
for i in (1272, 1307):
    replace(expect(i, "срез, i = 1"), "срез, i = 1", "срез")
replace(expect(1341, "Обозначения: R — нагрузка пары"), "i — число плоскостей среза; ", "")
p1889 = expect(1889, "Результаты п. 12.6")
om = [o for o in p1889.iter(M + "oMath") if "".join(t.text for t in o.iter(M + "t")) == "i=1"]
assert len(om) == 1
om[0].getparent().remove(om[0])
replace(p1889, " мм, число плоскостей среза ", " мм, срез — в одной плоскости")
edit_formula(P[1890], r"\frac{4R}{i\pi d^{2}}", r"\frac{4R}{\pi d^{2}}", "eq_v26_shear_over.png")

# ================================================================ 2. устойчивость штока: минимальный момент инерции сечения
replace(expect(965, "Обозначения: N — продольная сила"), "I — осевой момент инерции площади", "I — осевой момент инерции сечения")
edit_formula(P[1148], r"\sqrt{\frac{I}{A}}", r"\sqrt{\frac{I_{\min}}{A}}", "eq_v26_lambda.png")
edit_formula(P[1149], r"E \cdot I}", r"E \cdot I_{\min}}", "eq_v26_euler.png")
p1153 = expect(1153, "E — модуль упругости; I — момент инерции площади;")
n_rpr = p1153.find(".//" + W + "r/" + W + "rPr")
new1153 = text_para(p1153, [
    "E — модуль упругости; ", ("I", "min"), " — минимальный осевой момент инерции сечения: стержень теряет устойчивость, "
    "изгибаясь относительно той главной центральной оси, для которой момент инерции наименьший; для круга ", ("I", "min"),
    " = πd⁴/64. ", ("F", "кр"), " и ", ("σ", "кр"), " — критические сила и напряжение; ", ("σ", "т"),
    " — предел текучести; a и b — коэффициенты формулы Ясинского. Здесь b не означает толщину полосы."], n_rpr)
after(p1153, new1153)
p1153.getparent().remove(p1153)
p1239 = expect(1239, "По рабочей нагрузке достаточно штока диаметром 6 мм")
after(p1239, text_para(p1239, [
    "Если условие устойчивости не выполняется, его обеспечивают одним из двух способов: увеличивают размер сечения или "
    "применяют другой материал. Увеличение диаметра действует при любой гибкости: ", ("I", "min"),
    " растёт пропорционально d⁴, а гибкость λ = 4μl/d уменьшается. Замена материала повышает критическое напряжение только "
    "при гибкости меньше предельной, где действует формула Ясинского с коэффициентами a и b данной марки; при λ ≥ ",
    ("λ", "пред"), " критическую силу по формуле Эйлера определяет модуль упругости E, практически одинаковый у углеродистых "
    "сталей. Для штока выбран первый способ — увеличение диаметра при том же материале (Ст3)."],
    p1239.find(".//" + W + "r/" + W + "rPr")))

# ================================================================ запись
data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
rels_data = etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True)
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, data)
        elif item.filename == "word/_rels/document.xml.rels":
            zout.writestr(item, rels_data)
        else:
            zout.writestr(item, zin.read(item.filename))
    for name, png in new_media.items():
        zout.writestr(name, png)
print(f"замен текста и формул: {len(log)}, новых картинок: {len(new_media)} → {DST}")
