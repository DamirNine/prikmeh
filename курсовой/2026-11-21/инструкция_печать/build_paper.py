# -*- coding: utf-8 -*-
"""Бумажная инструкция по сборке и эксплуатации (как у мебели / конструкторов): А4, картинки крупно, текста минимум.
Обложка → комплект деталей и инструменты → 11 шагов сборки (номер, детали шага, картинка, 1–2 строки, ⚠ / ✓) →
закупоривание бутылки в 4 картинках → если что-то не так. Картинки — инструкция/img (кадры сборки КОМПАС: новая деталь
шага подсвечена жёлтым). Номера деталей — как у файлов «Детали для печати».
    python build_paper.py   → paper.html; затем node to_pdf.js → «Инструкция по сборке и эксплуатации.pdf»"""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "инструкция", "img")
OUT = os.path.join(HERE, "paper.html")


def uri(name, max_px=1100):
    im = Image.open(os.path.join(IMG, name + ".png")).convert("RGB")
    bb = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()
    im = im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), min(bb[2] + 10, im.width), min(bb[3] + 10, im.height)))
    im.thumbnail((max_px, max_px))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


PARTS = {1: ("Стойка", "p_stand"), 2: ("Кулиса (рукоять)", "p_kulisa"), 3: ("Камень", "p_kamen"), 4: ("Палец", "p_pin"),
         5: ("Направляющая", "p_guide"), 6: ("Ползун", "p_polzun"), "6а": ("Головка ползуна", "p_head"), 7: ("Шайба 10", "p_washer"),
         8: ("Гайка М10", "p_nut"), 9: ("Кожух", "p_cover"), 10: ("Винт М10", "p_screw"), 11: ("Ключ S5", "p_key")}
PIC = {k: uri(v[1], 500) for k, v in PARTS.items()}

# шаг: заголовок, детали шага, картинки, строки (✓ — проверка, ⚠ — внимание)
STEPS = [   # 21.11: направляющая с полкой под шток, ползун из двух частей — палец ставится после ползуна, головка клеится последней
    ("Стойка", [1], ["10_стойка"], ["Поставьте стойку основанием на стол, ось O — к себе.",
                                     "✓ На стойке: ось O, два упора, выемка под направляющую, два зацепа кожуха."]),
    ("Камень на кулису", [2, 3], ["12_камень_на_кулису"], ["Отверстие камня и втулка кулисы — в разные стороны.",
                                                           "✓ Камень скользит по кулисе свободно."]),
    ("Кулиса на ось O", [], ["13_кулиса_на_ось"], ["Втулкой к стойке — на ось O до упора. Рукоять — между упорами.",
                                                    "⚠ Надевается рукой. Туго — прогоните отверстие сверлом Ø10,5. Силой не надевать!"]),
    ("Направляющая", [5], ["135_направляющая"], ["Пластину — в выемку стойки до дна, полкой вниз, камень — между планками.",
                                                  "✓ Направляющая не качается в стороны."]),
    ("Винт М10", [10, 11], ["136_винт"], ["Вверните винт ключом через пластину направляющей в стойку до упора.",
                                           "✓ Торец винта вровень с площадкой."]),
    ("Ползун сверху", [6], ["14_ползун"], ["Сверху между планками, шток — в отверстие полки; брусок — напротив камня.",
                                           "✓ Ползун ходит вверх-вниз между планками."]),
    ("Палец через ползун", [4], ["145_палец"], ["Гладким концом — через брусок ползуна в камень, до упора.",
                                                 "⚠ Клей — только в отверстие камня, не на ползун."]),
    ("Шайба и гайка", [7, 8], ["15_шайба_гайка"], ["Шайбу — на палец, гайку — рукой до упора (дальше не пустит конец резьбы).",
                                                   "✓ Ползун свободно качается на пальце."]),
    ("Головка на клей", ["6а"], ["155_головка"], ["Клей — в гнездо головки, головку — снизу на шток до упора, конусом вниз.",
                                                  "⚠ Клеить последней: потом ползун не вынуть. До высыхания клея не нагружать."]),
    ("Проверка хода", [], ["02_рукоять_вверху", "03_рукоять_внизу"], ["Рукоять вверх до упора — вниз до упора, несколько раз.",
                                                                       "✓ Плавно, без заеданий; колокол проходит 16 мм."]),
    ("Кожух", [9], ["16_кожух_надевание", "17_кожух_на_месте"], ["Рукоять посередине хода. Надвиньте кожух до листа стойки — до щелчка защёлок.",
                                                               "✓ Кожух не снимается рывком. Снять: отжать оба язычка."]),
]
USE = [("02_рукоять_вверху", "Поднимите рукоять до упора"), ("18_бутылка", "Пробку — на горлышко, бутылку — под колокол"),
       ("03_рукоять_внизу", "Плавно нажмите до нижнего упора"), ("02_рукоять_вверху", "Поднимите рукоять, выньте бутылку")]
TROUBLE = [("Кулиса туго крутится на оси", "Снять, прогнать отверстие сверлом Ø10,5. Не крутить силой."),
           ("Гайка или винт не накручиваются", "Убрать ножом наплывы с витков, начинать ровно, без перекоса."),
           ("Направляющая не входит в выемку", "Подшкурить края пластины."),
           ("Ползун заедает в планках", "Подшкурить бока бруска ползуна."),
           ("Шток не проходит в полку", "Прогнать отверстие полки сверлом Ø8,5."),
           ("Кожух не защёлкивается", "Зачистить скосы крючков и зацепы стойки."),
           ("Пробка обжимается криво", "Ставить бутылку точно под колокол, по центру.")]


def mark(line):
    if line.startswith("✓"):
        return f'<p class="ok"><span class="i">✓</span>{line[1:].strip()}</p>'
    if line.startswith("⚠"):
        return f'<p class="warn"><span class="i">!</span>{line[1:].strip()}</p>'
    return f"<p>{line}</p>"


def step_html(n, title, parts, pics, lines):
    pl = "".join(f'<div class="pp"><img src="{PIC[k]}"><b>{k}</b><span>1×</span></div>' for k in parts)
    pics_html = "".join(f'<img src="{uri(p)}">' for p in pics)
    return f'''<section class="step">
  <div class="sh"><div class="num">{n}</div><h2>{title}</h2>{f'<div class="parts">{pl}</div>' if parts else ''}</div>
  <div class="pics n{len(pics)}">{pics_html}</div>
  <div class="txt">{"".join(mark(l) for l in lines)}</div>
</section>'''


pages = []
pages.append(f'''<div class="page cover">
  <div class="brand">УКП.00.000</div>
  <h1>Укупориватель<br>бутылок</h1>
  <div class="sub">Инструкция по сборке и эксплуатации</div>
  <img class="hero" src="{uri("00_общий_вид", 1400)}">
  <div class="facts"><div><b>11</b>шагов</div><div><b>≈ 25</b>минут</div><div><b>12</b>деталей</div><div><b>0,33 л</b>Long Neck</div></div>
</div>''')
grid = "".join(f'<div class="kit"><img src="{PIC[k]}"><div><b>{k}</b> {name}</div><span>1×</span></div>' for k, (name, _) in PARTS.items())
pages.append(f'''<div class="page">
  <h3>Комплект деталей</h3>
  <div class="kitgrid">{grid}</div>
  <h3>Понадобится</h3>
  <div class="tools">
    <div><b>Ключ S5</b>деталь 11 или металлический</div><div><b>Ключ 16</b>или рукой</div>
    <div><b>Сверло Ø10,5</b>если туго на оси</div><div><b>Наждачка</b>зерно 180–240</div>
  </div>
  <p class="note"><span class="i">!</span>Перед сборкой: уберите поддержки и наплывы, проверьте, что гайка и винт накручиваются рукой.</p>
</div>''')
for k in range(0, len(STEPS), 2):
    pages.append('<div class="page">' + "".join(step_html(i + 1, *STEPS[i]) for i in range(k, min(k + 2, len(STEPS)))) + "</div>")
use = "".join(f'<div class="u"><div class="num s">{i + 1}</div><img src="{uri(p)}"><p>{t}</p></div>' for i, (p, t) in enumerate(USE))
tr = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in TROUBLE)
pages.append(f'''<div class="page">
  <h3>Как закупорить бутылку</h3>
  <div class="use">{use}</div>
  <p class="note"><span class="i">!</span>Не держите пальцы под колоколом. Не давите, если бутылка стоит не по центру.</p>
</div>''')

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2328; }
.page { width: 210mm; height: 297mm; padding: 14mm 14mm 12mm; page-break-after: always; position: relative; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.cover { background: #1b3a6b; color: #fff; display: flex; flex-direction: column; }
.brand { font-size: 13pt; letter-spacing: .2em; color: #d4a72c; font-weight: 700; }
.cover h1 { font-size: 46pt; line-height: 1.02; margin: 8mm 0 4mm; }
.sub { font-size: 17pt; color: #cadcfc; }
.hero { background: #fff; border-radius: 6mm; padding: 6mm; margin: 10mm auto 0; max-height: 150mm; max-width: 150mm; object-fit: contain; }
.facts { display: flex; gap: 6mm; margin-top: auto; }
.facts div { flex: 1; background: rgba(255,255,255,.1); border-radius: 4mm; padding: 4mm; font-size: 11pt; color: #cadcfc; }
.facts b { display: block; font-size: 22pt; color: #fff; }
h3 { font-size: 20pt; color: #1b3a6b; margin: 0 0 5mm; }
.kitgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; margin-bottom: 9mm; }
.kit { border: 0.5mm solid #d7dce4; border-radius: 3mm; padding: 3mm; position: relative; text-align: center; font-size: 10pt; }
.kit img { height: 30mm; max-width: 100%; object-fit: contain; display: block; margin: 0 auto 2mm; }
.kit b, .pp b { display: inline-block; min-width: 6mm; height: 6mm; line-height: 6mm; border-radius: 3mm; background: #1b3a6b; color: #fff; font-size: 9pt; text-align: center; padding: 0 1.5mm; }
.kit span, .pp span { position: absolute; top: 2mm; right: 3mm; font-weight: 700; font-size: 12pt; color: #b45309; }
.tools { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; margin-bottom: 8mm; }
.tools div { background: #eef2f8; border-radius: 3mm; padding: 4mm; font-size: 9.5pt; color: #5b6573; }
.tools b { display: block; font-size: 13pt; color: #1b3a6b; margin-bottom: 1mm; }
.step { height: 130mm; display: flex; flex-direction: column; border-bottom: 0.5mm dashed #c5ccd6; padding-bottom: 4mm; margin-bottom: 4mm; }
.step:last-child { border-bottom: 0; }
.sh { display: flex; align-items: center; gap: 5mm; }
.num { width: 15mm; height: 15mm; border-radius: 50%; background: #d4a72c; color: #fff; font-weight: 700; font-size: 24pt; display: flex; align-items: center; justify-content: center; flex: none; }
.num.s { width: 10mm; height: 10mm; font-size: 15pt; }
h2 { font-size: 20pt; margin: 0; color: #1b3a6b; flex: 1; }
.parts { display: flex; gap: 3mm; border: 0.6mm solid #1b3a6b; border-radius: 3mm; padding: 2mm 3mm; }
.pp { width: 20mm; text-align: center; position: relative; }
.pp img { height: 14mm; max-width: 100%; object-fit: contain; display: block; margin: 0 auto 1mm; }
.pp span { top: -1mm; right: -1mm; font-size: 10pt; }
.pics { flex: 1; display: flex; gap: 6mm; align-items: center; justify-content: center; min-height: 0; padding: 3mm 0; }
.pics img { max-height: 88mm; max-width: 100%; object-fit: contain; }
.pics.n2 img { max-width: 48%; }
.txt p { margin: 1.2mm 0; font-size: 11.5pt; display: flex; gap: 2.5mm; align-items: flex-start; }
.i { flex: none; width: 5.5mm; height: 5.5mm; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 9.5pt; color: #fff; background: #2f8f5b; }
.warn .i, .note .i { background: #b03a2e; }
.warn { color: #8a2a1f; font-weight: 700; }
.note { background: #fbeceb; border-radius: 3mm; padding: 3mm 4mm; font-size: 11pt; display: flex; gap: 3mm; align-items: center; margin: 0 0 8mm; }
.use { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6mm; margin-bottom: 6mm; }
.u { border: 0.5mm solid #d7dce4; border-radius: 3mm; padding: 4mm; position: relative; text-align: center; }
.u .num { position: absolute; top: 3mm; left: 3mm; }
.u img { height: 52mm; max-width: 100%; object-fit: contain; }
.u p { margin: 2mm 0 0; font-size: 11.5pt; font-weight: 700; color: #1b3a6b; }
.tr { width: 100%; border-collapse: collapse; font-size: 10.5pt; }
.tr td { border-bottom: 0.4mm solid #d7dce4; padding: 2.3mm 2mm; vertical-align: top; }
.tr td:first-child { font-weight: 700; width: 42%; color: #1b3a6b; }
"""
html = f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Укупориватель — инструкция</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
open(OUT, "w", encoding="utf-8").write(html)
print(OUT, len(html) // 1024, "КБ, страниц:", len(pages))
