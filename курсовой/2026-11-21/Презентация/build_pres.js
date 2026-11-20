// Презентация к защите курсового проекта «Тангенсный механизм ручного укупоривателя» — 13 слайдов, 16:9 (21.11).
// Структура и замечания преподавателя: титул; цели и задачи; постановка ТЗ (схема без чисел); метрический синтез; кинематика;
// первичный силовой (по звеньям, уравнения вместо матрицы); эпюры; прочность (сечения); уточнённый (график от времени);
// МКЭ; прототипирование (детали до и после); выводы (схема с размерами); спасибо за внимание. Каждый расчётный слайд —
// «постановка — результат». Значения — до десятых. Содержание — РПЗ v13.
// Рисунки — fig/ (prep_figs.py 20.11 + make_figs.py). Сборка:  NODE_PATH=<pptxgenjs> PPTX_SKILL=<навык pptx> node build_pres.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const FIG = path.join(__dirname, "fig");
const SIZES = JSON.parse(fs.readFileSync(path.join(FIG, "sizes.json"), "utf8"));
const OUT = path.join(__dirname, "Презентация_укупориватель.pptx");

const INK = "17212E", BRASS = "C8902E", TINT = "F0F2F5", LINE = "D6DBE2", PALE = "B9C3CF";
const THEME = {
  name: "Укупориватель", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "1E2630", lt1: "FFFFFF", dk2: INK, lt2: TINT, accent1: BRASS, accent2: "566579", accent3: "9AA5B2",
            accent4: "2E7D6B", accent5: "A8432F", accent6: "6E8FB3", hlink: "566579", folHlink: "9AA5B2" },
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
const nm = (s) => `${s}_${++objN}`;
// неразрывные пробелы: число не отрывается от единицы, знаки ≤ = × · — от операндов
const nb = (t) => typeof t !== "string" ? t : t.replace(/ ([≤≥=×·<>]) /g, " $1 ").replace(/ →/g, " →")
  .replace(/([≤≥]) /g, "$1 ").replace(/(\d) /g, "$1 ");

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
function stat(slide, x, y, w, h, big, small, { dark = false, bigSize = 24 } = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08,
    fill: { color: dark ? INK : TINT }, line: { type: "none" }, objectName: nm("плашка") });
  slide.addText([
    { text: nb(big), options: { fontSize: bigSize, bold: true, color: dark ? C.accent1 : C.text2, breakLine: true } },
    { text: nb(small), options: { fontSize: 13, color: dark ? "D9DEE5" : C.accent2 } },
  ], { x: x + 0.2, y: y + 0.06, w: w - 0.4, h: h - 0.12, valign: "middle", margin: 0, paraSpaceAfter: 2,
       isTextBox: true, objectName: nm("число") });
}
function result(slide, text, y = 6.18) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M, h: 0.62, rectRadius: 0.1,
    fill: { color: INK }, line: { type: "none" }, objectName: nm("вывод") });
  slide.addText("РЕЗУЛЬТАТ", { x: M + 0.2, y, w: 1.4, h: 0.62, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5,
    valign: "middle", margin: 0, isTextBox: true, objectName: nm("метка") });
  slide.addText(nb(text), { x: M + 1.65, y, w: W - 2 * M - 1.8, h: 0.62, fontSize: 16, bold: true, color: "FFFFFF",
    valign: "middle", margin: 0, isTextBox: true, objectName: nm("текст_вывода") });
}
// панель «Постановка»: что делаем, по каким критериям, при каких ограничениях
function setup(slide, rows, { x = M, y = 1.3, w = 3.55, h = 4.65 } = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: TINT }, line: { type: "none" },
    objectName: nm("постановка") });
  slide.addText("ПОСТАНОВКА", { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.3, fontSize: 12, bold: true, color: C.accent1,
    charSpacing: 1.5, margin: 0, isTextBox: true, objectName: nm("метка") });
  const runs = [];
  rows.forEach(([head, body], i) => {
    runs.push({ text: nb(head), options: { bold: true, color: C.text2, fontSize: 14, breakLine: true } });
    runs.push({ text: nb(body), options: { color: C.text1, fontSize: 14, breakLine: i < rows.length - 1, paraSpaceAfter: 9 } });
  });
  slide.addText(runs, { x: x + 0.25, y: y + 0.6, w: w - 0.5, h: h - 0.8, valign: "top", margin: 0, paraSpaceAfter: 2,
    isTextBox: true, objectName: nm("текст_постановки") });
}
function badge(slide, x, y, n, d = 0.5) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: BRASS }, line: { type: "none" }, objectName: nm("круг") });
  slide.addText(String(n), { x, y, w: d, h: d, fontSize: 16, bold: true, color: "FFFFFF", align: "center",
    valign: "middle", margin: 0, isTextBox: true, objectName: nm("номер") });
}
const content = (title) => { const s = pres.addSlide({ masterName: "CONTENT" }); s.addText(title, { placeholder: "title" }); return s; };
const txt = (s, t, o) => s.addText(nb(t), Object.assign({ fontSize: 15, color: C.text1, margin: 0, valign: "top", isTextBox: true,
                                                          objectName: nm("текст") }, o));
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: INK } } });
const b = (t) => ({ text: nb(t), options: { bold: true, color: C.text2 } });

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
  s.addNotes("Здравствуйте. Наша бригада представляет курсовой проект — ручной укупориватель бутылки на тангенсном механизме.");
}

// ------------------------------------------------------------------ 2. Цели и задачи
{
  const s = content("Цели и задачи");
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 1.3, w: 4.0, h: 4.65, rectRadius: 0.08, fill: { color: INK },
    line: { type: "none" }, objectName: "цель_фон" });
  txt(s, "ЦЕЛЬ", { x: M + 0.3, y: 1.55, w: 3.4, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  txt(s, "Закрыть бутылку кронен-крышкой", { x: M + 0.3, y: 1.9, w: 3.4, h: 1.0, fontSize: 24, bold: true, color: "FFFFFF" });
  txt(s, "ручным настольным укупоривателем: Long Neck 0,33 л, крышка Ø26 мм", { x: M + 0.3, y: 2.95, w: 3.4, h: 0.8,
      fontSize: 15, color: "D9DEE5" });
  txt(s, "НАЗНАЧЕНИЕ", { x: M + 0.3, y: 4.0, w: 3.4, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  txt(s, "Повышение производительности технологических процессов розлива спиртных напитков",
      { x: M + 0.3, y: 4.35, w: 3.4, h: 1.3, fontSize: 15, color: "FFFFFF" });
  const tasks = ["Сформулировать техническое задание и критерии", "Выполнить метрический синтез механизма",
    "Провести кинематический анализ", "Выполнить первичный силовой расчёт", "Рассчитать звенья на прочность, подобрать сечения",
    "Выполнить уточнённый силовой расчёт с учётом масс", "Построить геометрическую модель (КОМПАС-3D)",
    "Провести расчёт МКЭ и доработать детали", "Изготовить и испытать прототип"];
  txt(s, "ЗАДАЧИ", { x: 5.0, y: 1.3, w: 3, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  const cw = (W - M - 5.0 - 2 * 0.2) / 3, ch = 1.37;
  tasks.forEach((t, i) => {
    const x = 5.0 + (i % 3) * (cw + 0.2), y = 1.68 + Math.floor(i / 3) * (ch + 0.08);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: TINT },
      line: { type: "none" }, objectName: nm("задача") });
    badge(s, x + 0.18, y + 0.14, i + 1, 0.4);
    txt(s, t, { x: x + 0.18, y: y + 0.6, w: cw - 0.36, h: ch - 0.64, fontSize: 13, color: C.text1 });
  });
  s.addNotes("Цель проекта — закрыть бутылку кронен-крышкой ручным настольным устройством; назначение — повышение " +
    "производительности процессов розлива. Для этого нужно сформулировать ТЗ, выполнить синтез, кинематику, силовые и прочностной " +
    "расчёты, построить модель, провести расчёт МКЭ и изготовить прототип.");
}

// ------------------------------------------------------------------ 3. Постановка ТЗ
{
  const s = content("Постановка задачи и техническое задание");
  pic(s, "схема_постановка.png", M, 1.3, 4.6, 4.75, { caption: "0 — стойка, 1 — кулиса, 2 — камень, 3 — ползун" });
  const x = 5.55, tw = (W - M - x - 0.25) / 2, th = 1.05;
  txt(s, "ДАНО (ТЗ)", { x, y: 1.3, w: 3, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  [["0,33 л", "бутылка Long Neck, венчик 26 H 180"], ["Ø26 мм", "кронен-крышка тип I, жесть 0,22 мм"],
   ["≤ 120 Н", "сила руки на рукояти"], ["≤ 500 мм", "длина рукояти"],
   ["16 мм", "ход головки: подход 10 + обжим 6"], ["≥ 6 бут./мин", "производительность"]]
    .forEach(([bg, sm], i) => stat(s, x + (i % 2) * (tw + 0.25), 1.68 + Math.floor(i / 2) * (th + 0.17), tw, th, bg, sm, { bigSize: 22 }));
  txt(s, "ТРЕБУЕТСЯ", { x, y: 5.4, w: 3, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  txt(s, "найти размеры механизма (e, L, φн, φк), нагрузки и сечения звеньев; построить модель и прототип",
      { x: x + 1.55, y: 5.36, w: W - M - x - 1.55, h: 0.75, fontSize: 14 });
  result(s, "Расчётное усилие укупоривания Fук = 1974 Н (сечение юбки крышки, σт жести 415 МПа)");
  s.addNotes("Механизм: стойка, кулиса с рукоятью, камень и ползун. Поворот кулисы через камень двигает ползун вертикально. " +
    "Исходные данные — из ГОСТов на бутылку, крышку и эргономику: сила руки не более 120 ньютонов, рукоять до 500 миллиметров, " +
    "ход головки 16 миллиметров. Расчётное усилие укупоривания — 1974 ньютона. Размеры схемы на этом этапе неизвестны.");
}

// ------------------------------------------------------------------ 4. Метрический синтез
{
  const s = content("Метрический синтез");
  setup(s, [["Что делаем", "выбираем окно качания кулисы φн → φк и расстояние e от оси O до оси ползуна"],
            ["Критерии", "минимум площади треугольника O–Bн–Bк (компактность) и минимум углового хода ψ"],
            ["Ограничения", "P ≤ 120 Н, L ≤ 500 мм, e ≥ 10 мм, ход S = 16 мм"],
            ["Метод", "перебор ψ, компромисс — точка равных относительных уступок"]]);
  const x = 4.4;
  pic(s, "синтез_площадь.png", x, 1.3, 4.75, 4.65, { caption: "Площадь треугольника при разных окнах" });
  pic(s, "синтез_уступки.png", x + 4.95, 1.3, W - M - x - 4.95, 4.65, { caption: "Минимальная площадь и уступки" });
  result(s, "ψ = 36,8°, окно 59,5° → 22,7°, e = 12,5 мм; уступки по обоим критериям — 25,3 %");
  s.addNotes("Синтез: подбирали окно качания кулисы и расстояние e. Критерии — компактность и малый угловой ход — противоречат " +
    "друг другу, поэтому выбрали точку равных относительных уступок. Получили угловой ход 36,8 градуса и e = 12,5 миллиметра.");
}

// ------------------------------------------------------------------ 5. Кинематика
{
  const s = content("Кинематический анализ");
  setup(s, [["Что делаем", "находим положения, скорости и ускорения ползуна и кулисы"],
            ["Закон движения", "трапеция угловой скорости: разгон, постоянная скорость, торможение при обжиме"],
            ["Ограничение", "скорость руки ≤ 0,7 м/с → ωmax = 1,4 рад/с"],
            ["Метод", "аналоги скоростей и ускорений — производные функции положения yD = e · tg φ"]]);
  const x = 4.4;
  pic(s, "омега.png", x, 1.3, 4.6, 4.65, { caption: "Угловая скорость кулисы ω(t)" });
  pic(s, "ползун_кинематика.png", x + 4.8, 1.3, W - M - x - 4.8, 4.65, { caption: "Координата, скорость, ускорение ползуна" });
  result(s, "Рабочий ход 0,9 с, касание крышки при t = 0,4 с; ε = +3,2 / −3,0 рад/с², |vD| ≤ 31,7 мм/с");
  s.addNotes("Закон движения кулисы — трапеция угловой скорости с максимумом 1,4 радиана в секунду. Весь ход занимает 0,9 секунды. " +
    "Скорости и ускорения ползуна получены через аналоги — производные функции положения по углу.");
}

// ------------------------------------------------------------------ 6. Первичный силовой расчёт — по звеньям
{
  const s = content("Первичный силовой расчёт: по звеньям");
  txt(s, "Постановка: без масс и трения; для каждого звена ΣFx = 0, ΣFy = 0, ΣM = 0 — 9 уравнений, 9 неизвестных, 40 001 положение кулисы",
      { x: M, y: 1.18, w: W - 2 * M, h: 0.4, fontSize: 14, color: C.accent2 });
  const cw = (W - 2 * M - 2 * 0.25) / 3;
  [["звено1.png", "ур1.png", "Звено 1 — кулиса с рукоятью"], ["звено2.png", "ур2.png", "Звено 2 — камень"],
   ["звено3.png", "ур3.png", "Звено 3 — ползун"]].forEach(([fig, eq, cap], i) => {
    const x = M + i * (cw + 0.25);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.65, w: cw, h: 4.35, rectRadius: 0.06, fill: { color: "FFFFFF" },
      line: { color: LINE, width: 0.75 }, objectName: nm("звено") });
    txt(s, cap, { x: x + 0.15, y: 1.73, w: cw - 0.3, h: 0.32, fontSize: 15, bold: true, color: C.text2 });
    pic(s, fig, x + 0.1, 2.08, cw - 0.2, 2.25, { card: false, pad: 0.04 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: 4.4, w: cw - 0.2, h: 1.52, rectRadius: 0.05, fill: { color: TINT },
      line: { type: "none" }, objectName: nm("уравнения_фон") });
    pic(s, eq, x + 0.1, 4.42, cw - 0.2, 1.48, { card: false, pad: 0.03 });
  });
  result(s, "Pmax = 112,8 Н < 120 Н при φу = 41,6°; R12 = 2515 Н; длина рукояти 470 → 500 мм");
  s.addNotes("Силовой расчёт вели по звеньям. Кулиса: на неё действуют сила руки, реакция оси O и реакция камня. Камень: реакция " +
    "кулисы и реакция ползуна. Ползун: реакция камня, реакция направляющей и сопротивление крышки. Для каждого звена — три " +
    "уравнения равновесия. Максимальная сила руки 112,8 ньютона, меньше допустимых 120.");
}

// ------------------------------------------------------------------ 7. Эпюры
{
  const s = content("Внутренние силовые факторы кулисы");
  setup(s, [["Что делаем", "строим эпюры N, Q, M кулисы для подбора сечения"],
            ["Схема", "балка OK длиной 500 мм; сила камня — в точке D, сила руки — в точке K"],
            ["Опасное положение", "φу = 41,6° — начало пластической деформации: P = 112,8 Н, R12 = 2515 Н"]]);
  pic(s, "эпюры_фи_у.png", 4.4, 1.3, 5.6, 4.65, { caption: "Схема и эпюры N, Q, M кулисы при φу" });
  const x = 10.2, w = W - M - x;
  stat(s, x, 1.3, w, 1.45, "40,8 Н·м", "|M| под камнем, точка D", { dark: true });
  stat(s, x, 2.9, w, 1.45, "2430,5 Н", "поперечная сила на участке O–D");
  stat(s, x, 4.5, w, 1.45, "−75,0 Н", "продольная сила в кулисе");
  result(s, "Опасное сечение кулисы — под камнем (точка D); в точке K момент равен нулю");
  s.addNotes("Кулису рассматриваем как балку длиной 500 миллиметров. В опасном положении наибольший изгибающий момент — " +
    "40,8 ньютон-метра в сечении под камнем. По нему подбираем сечение.");
}

// ------------------------------------------------------------------ 8. Прочностной расчёт
{
  const s = content("Прочностной расчёт и сечения звеньев");
  setup(s, [["Условие", "σ = N/A + M/W ≤ [σ] = σт / n, n = 2,5"],
            ["Сортамент", "лист — ГОСТ 19903-2015, круг — ГОСТ 2590-2006"],
            ["Проверки", "шток — сжатие и устойчивость (Ясинский / Эйлер); ось и палец — срез; отверстия — смятие"]]);
  pic(s, "сечения.png", 4.4, 1.3, W - M - 4.4, 2.15, { caption: "Принятые сечения (штриховка — металл, ЕСКД)" });
  s.addTable([
    [hdr("Элемент"), hdr("Проверка"), hdr("МПа"), hdr("Допуск")],
    ["Кулиса 8 × 18, Ст3сп", "изгиб", b("94,8"), "98"],
    ["Шток Ø8, Ст3сп", "сжатие / устойчивость", b("39,3 / nу = 6,2"), "98 / ≥ 3"],
    ["Ось O Ø10 / палец D Ø10", "срез", b("31,0 / 32,0"), "50"],
    ["Отверстие кулисы со ступицей", "смятие", b("12,2"), "24"],
  ], { x: 4.4, y: 3.62, w: W - M - 4.4, colW: [3.0, 2.25, 1.75, 1.33], rowH: 0.45, fontSize: 14, color: C.text1,
       border: { type: "solid", pt: 0.75, color: LINE }, fill: { color: "FFFFFF" }, valign: "middle",
       margin: [0, 0.08, 0, 0.08], objectName: "проверки" });
  result(s, "Кулиса 8 × 18 (Ст3сп), шток Ø8, ось и палец Ø10; без ступицы смятие 30,4 > 24 МПа → ступица Ø16 × 12");
  s.addNotes("Сечения подбирали по условию прочности с запасом 2,5 и по сортаменту. Кулиса — полоса 8 на 18 из Ст3сп, " +
    "напряжение 94,8 при допускаемых 98 мегапаскалях. Шток диаметром 8 проходит по устойчивости с запасом 6,2. Ось и палец " +
    "диаметром 10 проходят по срезу. Отверстие кулисы без ступицы не проходило по смятию — ввели ступицу.");
}

// ------------------------------------------------------------------ 9. Уточнённый расчёт
{
  const s = content("Уточнённый силовой расчёт");
  setup(s, [["Что делаем", "повторяем силовой расчёт с массами звеньев"],
            ["Метод", "кинетостатика: + силы тяжести G1, G3, силы инерции Ф1, Ф3 и момент MФ1; трение не учитываем"],
            ["Критерий", "изменение силы руки и реакций; проверка принятых сечений"]]);
  pic(s, "схемы_уточняющий.png", 4.4, 1.3, 3.75, 4.65, { caption: "Схемы с силами тяжести и инерции" });
  pic(s, "сила_руки_t.png", 8.35, 1.3, W - M - 8.35, 4.65, { caption: "Сила руки P(t): первичный, уточнённый, допустимая" });
  result(s, "Сила руки 112,8 → 109,9 Н (−2,6 %), реакции меняются менее чем на 1 % — сечения сохраняются");
  s.addNotes("В уточнённом расчёте добавили силы тяжести и инерции кулисы и ползуна. На графике силы руки от времени видно: " +
    "уточнённая кривая идёт чуть ниже первичной, максимум снизился на 2,6 процента, обе ниже допустимых 120 ньютонов.");
}

// ------------------------------------------------------------------ 10. МКЭ
{
  const s = content("Расчёт методом конечных элементов");
  setup(s, [["Что делаем", "расчёт напряжений в деталях в APM FEM при φу = 41,6°"],
            ["Критерий", "σmax ≤ [σ] материала детали"],
            ["Доработка", "форма — пазы облегчения, скругления, замкнутая обойма; материал — самый простой из достаточных"]]);
  const gx = 4.4, gw = 2.4, gh = 2.25;
  pic(s, "мкэ_кулиса.png", gx, 1.3, gw, gh, { caption: "Кулиса" });
  pic(s, "мкэ_ползун.png", gx + gw + 0.2, 1.3, gw, gh, { caption: "Ползун" });
  pic(s, "мкэ_камень.png", gx, 1.3 + gh + 0.15, gw, gh, { caption: "Камень" });
  pic(s, "мкэ_направляющая.png", gx + gw + 0.2, 1.3 + gh + 0.15, gw, gh, { caption: "Направляющая" });
  const tx = gx + 2 * gw + 0.4;
  s.addTable([
    [hdr("Деталь"), { text: [{ text: "σ" }, { text: "max", options: { subscript: true } }, { text: ", МПа" }],
                      options: { bold: true, color: "FFFFFF", fill: { color: INK } } }, hdr("[σ]")],
    ["Кулиса", b("92,6"), "98"], ["Ползун", b("95,9 → 49,0"), "98"], ["Камень", b("646 → 100"), "142"],
    ["Направляющая", b("920 → 136,2"), "142"], ["Палец D", b("192"), "314"],
  ], { x: tx, y: 1.3, w: W - M - tx, colW: [1.35, 1.2, 0.583], rowH: 0.45, fontSize: 13, color: C.text1,
       border: { type: "solid", pt: 0.75, color: LINE }, fill: { color: "FFFFFF" }, valign: "middle",
       margin: [0, 0.06, 0, 0.06], objectName: "мкэ_таблица" });
  stat(s, tx, 4.25, W - M - tx, 1.45, "−22 % массы", "кулиса 577,6 → 449,7 г", { dark: true, bigSize: 22 });
  result(s, "После доработки σmax ≤ [σ] у всех деталей; материалы: Ст3сп, сталь 45, 40Х — по напряжениям");
  s.addNotes("По картам напряжений МКЭ доработали детали: в камне и направляющей пики снизились в 6–7 раз, в ползуне вдвое, " +
    "кулису облегчили на 22 процента без роста напряжений. Материал каждой детали — самый простой, который выдерживает нагрузку.");
}

// ------------------------------------------------------------------ 11. Прототипирование — детали до и после
{
  const s = content("Прототипирование: детали до и после");
  const y = 1.3, h = 3.75;
  txt(s, "НАПРАВЛЯЮЩАЯ", { x: M, y, w: 4, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  pic(s, "до_направляющая.png", M, y + 0.35, 2.05, h - 0.35, { caption: "до" });
  pic(s, "после_направляющая.png", M + 2.2, y + 0.35, 2.05, h - 0.35, { caption: "после: полка под шток" });
  const x2 = M + 4.55;
  txt(s, "ПОЛЗУН", { x: x2, y, w: 4, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  pic(s, "до_ползун.png", x2, y + 0.35, 1.35, h - 0.35, { caption: "до" });
  pic(s, "после_ползун.png", x2 + 1.5, y + 0.35, 1.35, h - 0.35, { caption: "после: верх" });
  pic(s, "после_головка.png", x2 + 3.0, y + 0.35, 1.75, h - 0.35, { caption: "головка (клей)" });
  const x3 = x2 + 5.0;
  txt(s, "УЗЕЛ В СБОРКЕ", { x: x3, y, w: 3, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5 });
  pic(s, "сборка_узел.png", x3, y + 0.35, W - M - x3, h - 0.35, { caption: "шток в полке, головка снизу" });
  const notes = [["3D-печать FDM", "все детали, резьба М10 × 1,5 и ключ S5 — печатные"],
                 ["Зазоры", "отверстия под оси Ø10 → Ø10,6: кулиса треснула при посадке без зазора"],
                 ["Направляющая-«стул»", "полка с отверстием Ø8,6 ведёт шток ползуна"],
                 ["Ползун из двух частей", "головка клеится на хвостовик после установки"]];
  const nw = (W - 2 * M - 3 * 0.2) / 4;
  notes.forEach(([hd, t], i) => {
    const x = M + i * (nw + 0.2);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.2, w: nw, h: 0.85, rectRadius: 0.06, fill: { color: TINT },
      line: { type: "none" }, objectName: nm("заметка") });
    s.addText([{ text: nb(hd), options: { bold: true, color: C.text2, fontSize: 13, breakLine: true } },
               { text: nb(t), options: { color: C.text1, fontSize: 12 } }],
      { x: x + 0.15, y: 5.24, w: nw - 0.3, h: 0.77, valign: "middle", margin: 0, isTextBox: true, objectName: nm("заметка_текст") });
  });
  result(s, "Сборка проверена в КОМПАС-3D: пересечений на всём ходе нет, новый порядок сборки выполним");
  s.addNotes("Прототип печатали на 3D-принтере. После первой сборки доработали детали: кулиса треснула на оси без зазора — " +
    "отверстия увеличили до 10,6 миллиметра. Направляющую сделали в виде «стула» с полкой, через отверстие которой проходит шток, " +
    "а ползун разрезали: головку приклеивают снизу после установки.");
}

// ------------------------------------------------------------------ 12. Выводы
{
  const s = content("Выводы");
  const items = [
    "Спроектирован ручной укупориватель бутылки Long Neck 0,33 л: ход головки 16 мм, усилие 1974 Н, сила руки ≤ 112,8 Н при рукояти 500 мм",
    "Синтез: окно качания 59,5° → 22,7° (ψ = 36,8°), e = 12,5 мм",
    "Выполнены кинематика, первичный и уточнённый силовые расчёты: учёт масс снижает силу руки на 2,6 %",
    "По прочности приняты кулиса 8 × 18 (Ст3сп), шток Ø8, ось и палец Ø10",
    "3D-модели доработаны по МКЭ, прототип напечатан и собран",
  ];
  s.addText(items.map((t, i) => ({ text: nb(t), options: { bullet: { indent: 18 }, breakLine: i < items.length - 1 } })),
    { x: M, y: 1.4, w: 7.4, h: 4.6, fontSize: 17, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 12,
      isTextBox: true, objectName: "итоги" });
  pic(s, "схема_результат.png", 8.4, 1.3, W - M - 8.4, 5.6, { caption: "Схема с размерами по результатам расчёта" });
  s.addNotes("Итак, спроектирован укупориватель: ход 16 миллиметров, усилие 1974 ньютона при силе руки не больше 113 ньютонов. " +
    "Справа — схема механизма с размерами, полученными в расчётах.");
}

// ------------------------------------------------------------------ 13. Спасибо за внимание
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addText("Спасибо за внимание!", { x: M, y: 2.9, w: 7.6, h: 1.0, fontSize: 44, bold: true, color: "FFFFFF", margin: 0,
    fontFace: THEME.headFontFace, isTextBox: true, objectName: "заголовок" });
  txt(s, "Проектирование и исследование тангенсного механизма ручного укупоривателя бутылки",
      { x: M, y: 4.05, w: 7.4, h: 0.8, fontSize: 18, color: C.accent1 });
  txt(s, "РК6-55Б  ·  бригада №2  ·  руководитель Подчасов Е.О.", { x: M, y: 6.55, w: 7.4, h: 0.35, fontSize: 13, color: PALE });
  pic(s, "01_без_кожуха.png", 8.55, 0.6, 4.18, 6.3, { pad: 0.12 });
  s.addNotes("Спасибо за внимание! Готовы ответить на вопросы.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("ok", OUT);
})();
