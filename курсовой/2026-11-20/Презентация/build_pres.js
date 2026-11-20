// Презентация к защите курсового проекта «Тангенсный механизм ручного укупоривателя» — 12 слайдов, 16:9.
// Содержание — РПЗ v13 (Корнеев А.Е., 20.11), порядок разделов — образец курсовой/примеры/Презентация.pptx (1).pdf.
// Картинки — fig/ (prep_figs.py). Сборка:  NODE_PATH=<папка с pptxgenjs> PPTX_SKILL=<папка навыка pptx> node build_pres.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const FIG = path.join(__dirname, "fig");
const SIZES = JSON.parse(fs.readFileSync(path.join(FIG, "sizes.json"), "utf8"));
const OUT = path.join(__dirname, "Презентация_укупориватель.pptx");

// графит + латунь (цвет кронен-крышки)
const INK = "17212E", BRASS = "C8902E", STEEL = "566579", TINT = "F0F2F5", LINE = "D6DBE2", PALE = "B9C3CF", GREY = "9AA5B2";
const THEME = {
  name: "Укупориватель", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "1E2630", lt1: "FFFFFF", dk2: INK, lt2: TINT, accent1: BRASS, accent2: STEEL, accent3: GREY,
            accent4: "2E7D6B", accent5: "A8432F", accent6: "6E8FB3", hlink: STEEL, folHlink: GREY },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                       // 13,333 × 7,5″
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Тангенсный механизм ручного укупоривателя бутылки";
pres.author = "РК6-55Б, бригада №2";
pres.subject = "Курсовой проект по прикладной механике";
const C = pres.SchemeColor;
const EMBLEM = path.join(FIG, "герб.png");
const W = 13.333, M = 0.6;

pres.defineSlideMaster({
  title: "DARK", background: { color: INK },
  objects: [{ image: { path: EMBLEM, x: M, y: 0.45, w: 0.8, h: 0.9 } }],
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  objects: [
    { image: { path: EMBLEM, x: W - M - 0.56, y: 0.32, w: 0.56, h: 0.63 } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.3, w: 10.8, h: 0.75, fontSize: 32, bold: true,
                                color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Тангенсный механизм ручного укупоривателя  ·  РК6-55Б, бригада №2",
              options: { x: M, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent3, margin: 0, valign: "middle" } } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.accent3, align: "right" },
});

// ------------------------------------------------------------------ помощники
const ratio = (f) => SIZES[f][0] / SIZES[f][1];
let objN = 0;
// неразрывные пробелы: число не отрывается от единицы, знаки ≤ = × · — от операндов
const nb = (t) => typeof t !== "string" ? t : t.replace(/ ([≤≥=×·]) /g, " $1 ").replace(/ →/g, " →")
  .replace(/([≤≥]) /g, "$1 ").replace(/(\d) /g, "$1 ");
const nm = (s) => `${s}_${++objN}`;

// картинка, вписанная в рамку (x, y, w, h) по центру; card — белая карточка с рамкой
function pic(slide, f, x, y, w, h, { card = true, pad = 0.08, caption = null, capH = 0.32 } = {}) {
  const ih = caption ? h - capH : h;
  if (card) slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: ih, rectRadius: 0.06,
    fill: { color: "FFFFFF" }, line: { color: LINE, width: 0.75 }, objectName: nm("рамка") });
  const bw = w - 2 * pad, bh = ih - 2 * pad, r = ratio(f);
  let pw = bw, ph = bw / r;
  if (ph > bh) { ph = bh; pw = bh * r; }
  slide.addImage({ path: path.join(FIG, f), x: x + (w - pw) / 2, y: y + (ih - ph) / 2, w: pw, h: ph,
                   altText: caption || f, objectName: nm("рис") });
  if (caption) slide.addText(nb(caption), { x, y: y + ih + 0.04, w, h: capH - 0.04, fontSize: 11, color: C.accent2,
    align: "center", valign: "top", margin: 0, isTextBox: true, objectName: nm("подпись") });
}
// плашка с крупным числом
function stat(slide, x, y, w, h, big, small, { dark = false, bigSize = 26 } = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08,
    fill: { color: dark ? INK : TINT }, line: { type: "none" }, objectName: nm("плашка") });
  slide.addText([
    { text: nb(big), options: { fontSize: bigSize, bold: true, color: dark ? C.accent1 : C.text2, breakLine: true } },
    { text: nb(small), options: { fontSize: 13, color: dark ? "D9DEE5" : C.accent2 } },
  ], { x: x + 0.2, y: y + 0.08, w: w - 0.4, h: h - 0.16, valign: "middle", margin: 0, paraSpaceAfter: 2,
       isTextBox: true, objectName: nm("число") });
}
// вывод слайда — тёмная плашка внизу с латунной меткой
function result(slide, text, y = 6.18) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M, h: 0.62, rectRadius: 0.1,
    fill: { color: INK }, line: { type: "none" }, objectName: nm("вывод") });
  slide.addShape(pres.shapes.OVAL, { x: M + 0.16, y: y + 0.13, w: 0.36, h: 0.36, fill: { color: BRASS },
    line: { type: "none" }, objectName: nm("метка") });
  slide.addText("✓", { x: M + 0.16, y: y + 0.13, w: 0.36, h: 0.36, fontSize: 14, bold: true, color: INK,
    align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: nm("галочка") });
  slide.addText(nb(text), { x: M + 0.68, y, w: W - 2 * M - 0.85, h: 0.62, fontSize: 16, bold: true, color: "FFFFFF",
    valign: "middle", margin: 0, isTextBox: true, objectName: nm("текст_вывода") });
}
// номер в латунном круге
function badge(slide, x, y, n, d = 0.5) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: BRASS }, line: { type: "none" }, objectName: nm("круг") });
  slide.addText(String(n), { x, y, w: d, h: d, fontSize: 18, bold: true, color: "FFFFFF", align: "center",
    valign: "middle", margin: 0, isTextBox: true, objectName: nm("номер") });
}
const content = (title) => { const s = pres.addSlide({ masterName: "CONTENT" }); s.addText(title, { placeholder: "title" }); return s; };
const txt = (s, t, o) => s.addText(nb(t), Object.assign({ fontSize: 15, color: C.text1, margin: 0, valign: "top", isTextBox: true,
                                                      objectName: nm("текст") }, o));

// ------------------------------------------------------------------ 1. Титул
{
  const s = pres.addSlide({ masterName: "DARK" });
  txt(s, "КУРСОВОЙ ПРОЕКТ  ·  ПРИКЛАДНАЯ МЕХАНИКА", { x: M, y: 1.75, w: 7.2, h: 0.35, fontSize: 14, bold: true,
      color: C.accent1, charSpacing: 2 });
  s.addText("Проектирование и исследование тангенсного механизма ручного укупоривателя бутылки",
    { x: M, y: 2.2, w: 7.3, h: 2.1, fontSize: 36, bold: true, color: "FFFFFF", valign: "top", margin: 0,
      fontFace: THEME.headFontFace, isTextBox: true, objectName: "заголовок" });
  txt(s, "РК6-55Б  ·  бригада №2", { x: M, y: 4.55, w: 7.2, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
  txt(s, "Броцман Р.А., Девяткин Д.А., Калугин С.А., Корнеев А.Е., Салихова Е.Д.",
      { x: M, y: 5.0, w: 7.2, h: 0.65, fontSize: 15, color: "FFFFFF" });
  txt(s, "Руководитель: Подчасов Е.О.", { x: M, y: 5.7, w: 7.2, h: 0.35, fontSize: 15, color: "FFFFFF" });
  txt(s, "МГТУ им. Н.Э. Баумана  ·  кафедра РК6 «Системы автоматизированного проектирования»  ·  2026",
      { x: M, y: 6.65, w: 7.6, h: 0.3, fontSize: 11, color: PALE });
  pic(s, "00_общий_вид.png", 8.55, 0.6, 4.18, 6.3, { pad: 0.12 });
  s.addNotes("Здравствуйте. Наша бригада представляет курсовой проект — ручной укупориватель бутылки на тангенсном механизме. " +
    "Устройство надевает кронен-крышку на бутылку и обжимает её юбку на венчике горлышка.");
}

// ------------------------------------------------------------------ 2. Цели и задачи
{
  const s = content("Цели и задачи");
  s.addText([
    { text: "Цель: ", options: { bold: true, color: C.accent1 } },
    { text: "спроектировать, рассчитать и изготовить ручной настольный укупориватель бутылки Long Neck 0,33 л " +
            "под кронен-крышку Ø26 мм на основе тангенсного механизма." },
  ], { x: M, y: 1.3, w: W - 2 * M, h: 0.75, fontSize: 18, color: C.text1, margin: 0, valign: "top", isTextBox: true,
       objectName: "цель" });
  const parts = [
    ["Постановка ТЗ", "Назначение механизма, качественные и количественные критерии, исходные данные"],
    ["Расчётная часть", "Синтез, кинематический анализ, первичный силовой, прочностной и уточняющий силовой расчёты"],
    ["Конструкторская часть", "Геометрия и 3D-модели деталей, сборка, расчёт МКЭ и доработка геометрии"],
    ["Испытания", "Прототип на 3D-принтере, сборка и проверка механизма, инструкция по сборке и эксплуатации"],
  ];
  const cw = (W - 2 * M - 3 * 0.3) / 4;
  parts.forEach(([h, t], i) => {
    const x = M + i * (cw + 0.3), y = 2.25;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: 3.65, rectRadius: 0.08, fill: { color: TINT },
      line: { type: "none" }, objectName: nm("карточка") });
    badge(s, x + 0.3, y + 0.3, i + 1, 0.6);
    txt(s, h, { x: x + 0.3, y: y + 1.1, w: cw - 0.6, h: 0.75, fontSize: 19, bold: true, color: C.text2, valign: "bottom" });
    txt(s, t, { x: x + 0.3, y: y + 2.0, w: cw - 0.6, h: 1.5, fontSize: 14, color: C.text1 });
  });
  result(s, "Результат: РПЗ, 3D-модели и сборка в КОМПАС-3D, анимация работы, прототип и инструкция по сборке");
  s.addNotes("Цель проекта — спроектировать, рассчитать и изготовить ручной укупориватель. Работа состояла из четырёх частей: " +
    "постановка технического задания, расчётная часть, конструкторская часть с моделями и расчётом МКЭ, и испытания на прототипе.");
}

// ------------------------------------------------------------------ 3. Устройство и принцип работы
{
  const s = content("Устройство и принцип работы");
  pic(s, "без_кожуха.png", M, 1.3, 3.55, 4.7, { caption: "Механизм без кожуха" });
  pic(s, "кин_схема.png", 4.4, 1.3, 5.0, 4.7, { caption: "Кинематическая схема" });
  const x = 9.75, w = W - M - x;
  txt(s, "Звенья", { x, y: 1.3, w, h: 0.35, fontSize: 16, bold: true, color: C.accent1 });
  s.addText([
    { text: "0 — стойка", options: { breakLine: true } },
    { text: "1 — кулиса с рукоятью", options: { breakLine: true } },
    { text: "2 — камень (обойма на кулисе)", options: { breakLine: true } },
    { text: "3 — ползун с головкой" },
  ], { x, y: 1.7, w, h: 1.3, fontSize: 15, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 3, isTextBox: true,
       objectName: "звенья" });
  s.addText([
    { text: "Поворот кулисы через камень и палец D превращается в вертикальный ход ползуна:", options: { breakLine: true } },
    { text: "y", options: { bold: true, color: C.text2, fontSize: 18 } },
    { text: "D", options: { bold: true, color: C.text2, fontSize: 18, subscript: true } },
    { text: " = e · tg φ", options: { bold: true, color: C.text2, fontSize: 18 } },
  ], { x, y: 3.05, w, h: 1.05, fontSize: 14, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true,
       objectName: "формула" });
  stat(s, x, 4.4, w, 1.05, "16 = 10 + 6 мм", "ход головки: подход + обжим", { bigSize: 24 });
  result(s, "Формула строения I(0, 1) + II ПВП(2, 3): пары O и D вращательные, 1–2 и 3–0 поступательные, все V класса");
  s.addNotes("Механизм состоит из стойки, кулисы с рукоятью, камня и ползуна. Оператор опускает рукоять, кулиса поворачивается вокруг оси O, " +
    "камень скользит по ней и через палец D двигает ползун строго вертикально. Ход головки — 16 миллиметров: 10 на подход и 6 на обжим крышки.");
}

// ------------------------------------------------------------------ 4. Условия проектирования
{
  const s = content("Условия проектирования");
  const tiles = [
    ["0,33 л", "бутылка Long Neck, Ø60,4 × 226,5 мм"], ["Ø26 мм", "кронен-крышка тип I, жесть 0,22 мм"],
    ["≤ 120 Н", "сила руки на рукояти"], ["≤ 500 мм", "длина рукояти"],
    ["≥ 6 бут./мин", "производительность"], ["0,7 МПа", "внутреннее давление, которое держит укупорка"],
  ];
  const tw = 2.85, th = 1.3;
  tiles.forEach(([b, t], i) => stat(s, M + (i % 2) * (tw + 0.25), 1.3 + Math.floor(i / 2) * (th + 0.25), tw, th, b, t));
  pic(s, "обжим.png", 6.85, 1.3, W - M - 6.85, 4.45,
      { caption: "Обжим юбки крышки коническим входом головки: Ø32,10 → 28,6 мм" });
  result(s, "Расчётное усилие укупоривания Fук = 1974 Н — по сечению юбки, пределу текучести жести 415 МПа и упрочнению");
  s.addNotes("Исходные данные взяты из ГОСТов на бутылку, кронен-крышку и эргономику: сила руки не более 120 ньютонов, рукоять не длиннее 500 миллиметров. " +
    "Головка обжимает юбку крышки с 32,1 до 28,6 миллиметра. Расчётное усилие укупоривания получилось 1974 ньютона.");
}

// ------------------------------------------------------------------ 5. Синтез
{
  const s = content("Синтез: выбор окна качания кулисы");
  txt(s, "Критерии: минимальная площадь треугольника O–Bн–Bк (компактность) и минимальный угловой ход кулисы. " +
         "Ограничения: сила руки ≤ 120 Н, рукоять ≤ 500 мм, e ≥ 10 мм.", { x: M, y: 1.25, w: W - 2 * M, h: 0.7, fontSize: 15 });
  pic(s, "синтез_площадь.png", M, 2.05, 6.6, 3.95, { caption: "Площадь треугольника при разных окнах качания" });
  pic(s, "синтез_уступки.png", 7.45, 2.05, W - M - 7.45, 3.95, { caption: "Минимальная площадь и относительные уступки" });
  result(s, "Принято: ψ = 36,75°, окно 59,47° → 22,72°, e = 12,53 мм — точка K равных уступок 25,3 %");
  s.addNotes("Для синтеза минимизировали площадь треугольника, который занимает механизм, и угловой ход кулисы. " +
    "Эти критерии противоречат друг другу, поэтому выбрали компромисс — точку равных относительных уступок, 25,3 процента. " +
    "Получили угловой ход 36,75 градуса и расстояние от оси кулисы до оси ползуна 12,53 миллиметра.");
}

// ------------------------------------------------------------------ 6. Кинематика
{
  const s = content("Кинематический анализ");
  pic(s, "омега.png", M, 1.3, 5.05, 4.65, { caption: "Трапецеидальный закон угловой скорости кулисы" });
  pic(s, "ползун_кинематика.png", 5.95, 1.3, 4.05, 4.65, { caption: "Координата, скорость и ускорение ползуна" });
  const x = 10.3, w = W - M - x;
  stat(s, x, 1.3, w, 1.3, "1,40 рад/с", "максимальная угловая скорость", { bigSize: 24 });
  stat(s, x, 2.75, w, 1.3, "0,913 с", "рабочий ход рукояти", { bigSize: 24 });
  stat(s, x, 4.2, w, 1.3, "+3,20 / −2,97", "ε разгона / торможения, рад/с²", { bigSize: 24 });
  result(s, "Аналоги скоростей и ускорений — дифференцированием функции положения; касание крышки при t = 0,438 с");
  s.addNotes("Закон движения кулисы — трапеция угловой скорости: разгон на холостом ходе, постоянная скорость на упругом участке и торможение при обжиме. " +
    "Максимальная угловая скорость 1,4 радиана в секунду, весь рабочий ход занимает 0,913 секунды. " +
    "Скорости и ускорения точек получены через аналоги — производные функции положения по углу.");
}

// ------------------------------------------------------------------ 7. Первичный силовой расчёт
{
  const s = content("Первичный силовой расчёт");
  pic(s, "схемы_первичный.png", M, 1.3, 4.8, 4.65, { caption: "Расчётные схемы кулисы, камня и ползуна" });
  pic(s, "реакции_первичный.png", 5.65, 1.3, 4.35, 4.65, { caption: "Сила руки и реакции от угла φ" });
  const x = 10.3, w = W - M - x;
  stat(s, x, 1.3, w, 1.3, "112,8 Н", "максимум силы руки, φу = 41,63°", { bigSize: 24, dark: true });
  stat(s, x, 2.75, w, 1.3, "2515 Н", "реакция кулиса — камень R12", { bigSize: 24 });
  stat(s, x, 4.2, w, 1.3, "470 → 500 мм", "требуемая и принятая длина рукояти", { bigSize: 24 });
  result(s, "9 уравнений равновесия в матричной форме решены для 40 001 положения: P ≤ 112,8 Н < 120 Н");
  s.addNotes("Первичный расчёт выполнен без масс и трения. Для трёх звеньев записали девять уравнений равновесия и решили систему в матричной форме для 40 тысяч положений. " +
    "Наибольшая сила руки — 112,8 ньютона в начале пластической деформации крышки, это меньше допустимых 120. Требуемая длина рукояти — 470 миллиметров, приняли 500.");
}

// ------------------------------------------------------------------ 8. Прочностной расчёт
{
  const s = content("Прочностной расчёт");
  pic(s, "эпюры_фи_у.png", M, 1.3, 5.75, 4.65, { caption: "Эпюры N, Q, M кулисы в опасном положении φу" });
  const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: INK } } });
  const ok = (t) => ({ text: t, options: { bold: true, color: C.text2 } });
  const rows = [
    [hdr("Элемент"), hdr("Проверка"), hdr("МПа"), hdr("Допуск")],
    ["Кулиса 8 × 18, Ст3сп", "изгиб", ok("94,8"), "98"],
    ["Шток Ø8, Ст3сп", "сжатие", ok("39,3"), "98"],
    ["", "устойчивость", ok("nу = 6,15"), "≥ 3"],
    ["Ось O Ø10, сталь 45", "срез", ok("31,0"), "50"],
    ["Палец D Ø10, 40Х", "срез", ok("32,0"), "50"],
    ["Отверстие кулисы со ступицей", "смятие", ok("12,2"), "24"],
    ["Отверстие ползуна", "смятие", ok("15,7"), "24"],
  ];
  s.addTable(rows, { x: 6.7, y: 1.3, w: W - M - 6.7, colW: [2.85, 1.3, 1.05, 0.83], rowH: 0.42, fontSize: 14,
    color: C.text1, border: { type: "solid", pt: 0.75, color: LINE }, fill: { color: "FFFFFF" }, valign: "middle",
    margin: [0, 0.08, 0, 0.08], objectName: "проверки" });
  txt(s, "[σ] = σт / n, n = 2,5; сечения — по сортаменту ГОСТ 19903-2015 (лист) и ГОСТ 2590-2006 (пруток)",
      { x: 6.7, y: 4.85, w: W - M - 6.7, h: 0.7, fontSize: 13, color: C.accent2 });
  result(s, "Без ступицы смятие отверстия кулисы 30,4 МПа > 24 МПа — поэтому у оси O введена ступица Ø16 × 12");
  s.addNotes("По нагрузкам первичного расчёта подобрали сечения. Кулиса — полоса 8 на 18 из стали Ст3сп, напряжение 94,8 мегапаскаля при допускаемых 98. " +
    "Шток ползуна диаметром 8 миллиметров имеет запас устойчивости 6,15. Ось и палец диаметром 10 проходят по срезу. " +
    "Без ступицы отверстие кулисы не проходило по смятию, поэтому ввели ступицу.");
}

// ------------------------------------------------------------------ 9. Уточняющий силовой расчёт
{
  const s = content("Уточняющий силовой расчёт");
  pic(s, "схемы_уточняющий.png", M, 1.3, 4.65, 4.65, { caption: "Схемы с силами тяжести и инерции" });
  const x = 5.55, w = W - M - x;
  s.addChart(pres.charts.BAR, [
    { name: "Первичный", labels: ["Начало обжима", "Промежуточное", "Конец хода"], values: [112.8, 74.9, 63.0] },
    { name: "Уточнённый", labels: ["Начало обжима", "Промежуточное", "Конец хода"], values: [109.9, 71.7, 59.9] },
  ], { x, y: 1.25, w, h: 2.95, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60,
       chartColors: [GREY, BRASS], showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt",
       legendColor: "1E2630",
       showTitle: true, title: "Сила руки P, Н", titleFontSize: 14, titleFontFace: "+mn-lt", titleColor: "1E2630",
       showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
       dataLabelColor: "1E2630", dataLabelFormatCode: "0.0",
       catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: "566579",
       valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 130, valGridLine: { style: "none" },
       catGridLine: { style: "none" }, objectName: "сила_руки" });
  const tw = (w - 2 * 0.25) / 3;
  [["2515 → 2511 Н", "R12 кулиса — камень"], ["2432 → 2426 Н", "R10 ось O"], ["1671 → 1668 Н", "R30 направляющая"]]
    .forEach(([b, t], i) => stat(s, x + i * (tw + 0.25), 4.45, tw, 1.15, b, t, { bigSize: 18 }));
  result(s, "Учёт масс и инерции: сила руки −2,6 % (112,8 → 109,9 Н), реакции — менее 1 %; сечения сохраняются");
  s.addNotes("В уточняющем расчёте методом кинетостатики добавили силы тяжести и инерции кулисы и ползуна. " +
    "Сила руки уменьшилась на 2,6 процента, реакции изменились меньше чем на процент. Значит, сечения из прочностного расчёта подходят с запасом.");
}

// ------------------------------------------------------------------ 10. 3D-модель
{
  const s = content("3D-модель и сборка (КОМПАС-3D)");
  pic(s, "детали.png", M, 1.3, 7.45, 4.15, { caption: "Детали укупоривателя" });
  pic(s, "крайние_положения.png", 8.35, 1.3, W - M - 8.35, 4.15, { caption: "Крайние положения рукояти" });
  const tiles = [["10 деталей", "+ ключ-шестигранник S5"], ["29 сопряжений", "в сборке УКП.00.000"],
                 ["40 положений", "пересечений тел нет"], ["М10 × 1,5", "резьба пальца, гайки и винта"]];
  const tw = (W - 2 * M - 3 * 0.25) / 4;
  tiles.forEach(([b, t], i) => stat(s, M + i * (tw + 0.25), 5.7, tw, 1.1, b, t, { bigSize: 22 }));
  s.addNotes("По расчётам построили 3D-модели в КОМПАС-3D: стойка, кулиса с пазами облегчения, камень-обойма, палец, направляющая, ползун, шайба, гайка, кожух и установочный винт. " +
    "Сборка проверена на пересечения тел в 40 положениях рукояти — пересечений нет.");
}

// ------------------------------------------------------------------ 11. МКЭ
{
  const s = content("Расчёт МКЭ (APM FEM): до и после доработки");
  const gw = 3.55, gh = 2.25, gx = M, gy = 1.25;
  pic(s, "мкэ_кулиса.png", gx, gy, gw, gh, { caption: "Кулиса: пазы облегчения" });
  pic(s, "мкэ_ползун.png", gx + gw + 0.25, gy, gw, gh, { caption: "Ползун: скругления R3" });
  pic(s, "мкэ_камень.png", gx, gy + gh + 0.2, gw, gh, { caption: "Камень: замкнутая обойма" });
  pic(s, "мкэ_направляющая.png", gx + gw + 0.25, gy + gh + 0.2, gw, gh, { caption: "Направляющая: планка 12 мм" });
  const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: INK } } });
  const b = (t) => ({ text: t, options: { bold: true, color: C.text2 } });
  s.addTable([
    [hdr("Деталь"), { text: [{ text: "σ" }, { text: "max", options: { subscript: true } }, { text: ", МПа" }],
                      options: { bold: true, color: "FFFFFF", fill: { color: INK } } }, hdr("[σ]"), hdr("Материал")],
    ["Кулиса", b("92,6"), "98", "Ст3сп"],
    ["Ползун", b("95,9 → 49,0"), "98", "Ст3сп"],
    ["Камень", b("646 → 100"), "142", "сталь 45"],
    ["Направляющая", b("920 → 136"), "142", "сталь 45"],
    ["Палец D", b("192"), "314", "40Х"],
  ], { x: 8.25, y: 1.25, w: W - M - 8.25, colW: [1.35, 1.35, 0.6, 1.18], rowH: 0.44, fontSize: 13, color: C.text1,
       border: { type: "solid", pt: 0.75, color: LINE }, fill: { color: "FFFFFF" }, valign: "middle",
       margin: [0, 0.07, 0, 0.07], objectName: "мкэ_таблица" });
  stat(s, 8.25, 4.2, W - M - 8.25, 1.25, "−22 % массы", "кулиса: 577,6 → 449,7 г без роста напряжений", { bigSize: 22, dark: true });
  result(s, "Материалы выбраны минимально достаточными: после доработки σmax ≤ [σ] у всех деталей");
  s.addNotes("Расчёт методом конечных элементов в APM FEM выполнили в самом нагруженном положении. По картам напряжений доработали геометрию: " +
    "в камне и направляющей пики напряжений снизились в 6–7 раз, в ползуне — вдвое, кулису облегчили на 22 процента без роста напряжений. " +
    "Материал каждой детали выбран самый простой, который выдерживает нагрузку.");
}

// ------------------------------------------------------------------ 12. Заключение
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addText("Заключение", { x: M, y: 1.6, w: 7.5, h: 0.8, fontSize: 36, bold: true, color: "FFFFFF", margin: 0,
    fontFace: THEME.headFontFace, isTextBox: true, objectName: "заголовок" });
  const items = [
    "Спроектирован укупориватель бутылки Long Neck 0,33 л: ход головки 16 мм, усилие 1974 Н, сила руки ≤ 112,8 Н при рукояти 500 мм",
    "Синтез: окно качания 59,47° → 22,72° (ψ = 36,75°), e = 12,53 мм",
    "Кинематика, первичный и уточняющий силовые расчёты: учёт масс снижает силу руки на 2,6 %",
    "Приняты кулиса 8 × 18 (Ст3сп), шток Ø8, ось и палец Ø10",
    "3D-модели и сборка доработаны по МКЭ, материалы выбраны по напряжениям",
  ];
  s.addText(items.map((t, i) => ({ text: nb(t), options: { bullet: { indent: 18 }, breakLine: i < items.length - 1 } })),
    { x: M, y: 2.6, w: 7.4, h: 3.8, fontSize: 16, color: "FFFFFF", margin: 0, valign: "top", paraSpaceAfter: 10,
      isTextBox: true, objectName: "итоги" });
  txt(s, "Спасибо за внимание!", { x: M, y: 6.55, w: 7.4, h: 0.45, fontSize: 20, bold: true, color: C.accent1 });
  pic(s, "01_без_кожуха.png", 8.55, 0.6, 4.18, 6.3, { pad: 0.12 });
  s.addNotes("Итак, спроектирован ручной укупориватель: ход головки 16 миллиметров, усилие 1974 ньютона при силе руки не больше 113 ньютонов. " +
    "Выполнены синтез, кинематика, силовые и прочностной расчёты, построены 3D-модели, детали доработаны по МКЭ. Спасибо за внимание!");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("ok", OUT);
})();
