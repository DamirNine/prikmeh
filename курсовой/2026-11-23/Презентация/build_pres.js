// Презентация к защите курсового проекта «Тангенсный механизм ручного укупоривателя» — 13 слайдов, 16:9.
// Структура — по замечаниям преподавателя (21.11); оформление — по замечаниям Корнеева А.Е. (21.11): строгое академическое
// (белый фон, тёмно-синие заголовки, без цветных плашек и надписей внизу), титульный слайд — как титульный лист РПЗ,
// формулы — математическим набором (картинки STIX из make_figs.py). Значения — до десятых. Содержание — РПЗ.
// Сборка:  NODE_PATH=<pptxgenjs> PPTX_SKILL=<навык pptx> node build_pres.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const FIG = path.join(__dirname, "fig");
const SIZES = JSON.parse(fs.readFileSync(path.join(FIG, "sizes.json"), "utf8"));
const OUT = path.join(__dirname, "Презентация_укупориватель.pptx");

const NAVY = "1F3864", TEXT = "1E1E1E", GREY = "595959", LINEC = "BFC5CE", LIGHT = "F4F5F7";
const THEME = {
  name: "Укупориватель (строгая)", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: TEXT, lt1: "FFFFFF", dk2: NAVY, lt2: LIGHT, accent1: NAVY, accent2: GREY, accent3: "8C96A3",
            accent4: "2E5E8C", accent5: "A23B2C", accent6: "6E8FB3", hlink: NAVY, folHlink: GREY },
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

pres.defineSlideMaster({ title: "PLAIN", background: { color: "FFFFFF" }, objects: [] });
pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  objects: [
    { image: { path: EMBLEM, x: W - M - 0.5, y: 0.28, w: 0.5, h: 0.56 } },
    { line: { x: M, y: 1.0, w: W - 2 * M, h: 0, line: { color: NAVY, width: 1.25 } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.26, w: 11.2, h: 0.68, fontSize: 28, bold: true,
                                color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 11, color: C.accent2, align: "right" },
});

// ------------------------------------------------------------------ помощники
const ratio = (f) => SIZES[f][0] / SIZES[f][1];
let objN = 0;
const nm = (s) => `${s}_${++objN}`;
const nb = (t) => typeof t !== "string" ? t : t.replace(/(?<!М10) × (?!1,5)/g, " · ").replace(/ ([≤≥=×·<>]) /g, " $1 ")
  .replace(/ →/g, " →").replace(/([≤≥]) /g, "$1 ").replace(/(\d) /g, "$1 ");
// 21.11 (Корнеев А.Е.): индексы — нижними индексами, а не текстом: φн, Pmax, R12, Fук, σт, nу, |MD| …
const SUB_RE = /(?<![A-Za-zА-Яа-яЁё])(φ|ω|σ|ε|ψ|P|R|v|y|n|F|M|B|L)(max|min|треб|доп|обж|раб|ук|кр|н|к|у|т|D|12|10|30|23)(?![А-Яа-яЁёA-Za-z0-9])/g;
function rich(t, opt = {}) {
  t = nb(t);
  const runs = []; let last = 0;
  for (const m of t.matchAll(SUB_RE)) {
    if (m.index > last) runs.push({ text: t.slice(last, m.index), options: { ...opt } });
    runs.push({ text: m[1], options: { ...opt } });
    runs.push({ text: m[2], options: { ...opt, subscript: true } });
    last = m.index + m[0].length;
  }
  if (last < t.length || !runs.length) runs.push({ text: t.slice(last), options: { ...opt } });
  return runs;
}
const brk = (runs) => { runs[runs.length - 1].options.breakLine = true; return runs; };

function pic(slide, f, x, y, w, h, { card = true, pad = 0.08, caption = null, capH = 0.32, align = "center" } = {}) {
  const ih = caption ? h - capH : h;
  if (card) slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h: ih, fill: { color: "FFFFFF" }, line: { color: LINEC, width: 0.75 },
    objectName: nm("рамка") });
  const bw = w - 2 * pad, bh = ih - 2 * pad, r = ratio(f);
  let pw = bw, ph = bw / r;
  if (ph > bh) { ph = bh; pw = bh * r; }
  const px = align === "left" ? x + pad : x + (w - pw) / 2;
  slide.addImage({ path: path.join(FIG, f), x: px, y: y + (ih - ph) / 2, w: pw, h: ph, altText: caption || f, objectName: nm("рис") });
  if (caption) slide.addText(nb(caption), { x, y: y + ih + 0.04, w, h: capH - 0.04, fontSize: 11, color: C.accent2,
    align: "center", valign: "top", margin: 0, isTextBox: true, objectName: nm("подпись") });
}
// формула-картинка шириной не больше w, высотой h (по левому краю)
function formula(slide, f, x, y, w, h) { pic(slide, f, x, y, w, h, { card: false, pad: 0, align: "left" }); }
function stat(slide, x, y, w, h, big, small, { bigSize = 22 } = {}) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: "FFFFFF" }, line: { color: LINEC, width: 0.75 },
    objectName: nm("значение") });
  slide.addText([
    ...brk(rich(big, { fontSize: bigSize, bold: true, color: C.text2 })),
    ...rich(small, { fontSize: 12, color: C.accent2 }),
  ], { x: x + 0.18, y: y + 0.05, w: w - 0.36, h: h - 0.1, valign: "middle", margin: 0, paraSpaceAfter: 2, isTextBox: true,
       objectName: nm("число") });
}
function result(slide, text, y = 6.25) {
  slide.addShape(pres.shapes.RECTANGLE, { x: M, y, w: W - 2 * M, h: 0.55, fill: { color: LIGHT }, line: { color: NAVY, width: 1 },
    objectName: nm("вывод") });
  slide.addText([{ text: "Результат: ", options: { bold: true, color: C.text2 } }, ...rich(text, { color: C.text1 })],
    { x: M + 0.2, y, w: W - 2 * M - 0.4, h: 0.55, fontSize: 15, valign: "middle", margin: 0, isTextBox: true, objectName: nm("текст_вывода") });
}
// «Постановка»: строки (заголовок, текст[, формула-картинка, высота])
function setup(slide, rows, { x = M, y = 1.25, w = 3.65, h = 4.8 } = {}) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: LIGHT }, line: { type: "none" }, objectName: nm("постановка") });
  slide.addText("Постановка задачи", { x: x + 0.22, y: y + 0.15, w: w - 0.44, h: 0.32, fontSize: 15, bold: true, color: C.text2,
    margin: 0, isTextBox: true, objectName: nm("метка") });
  let cy = y + 0.6;
  for (const [head, body, f, fh] of rows) {
    let lines = 1, cur = 0;                       // перенос по словам: ~33 знака в строке панели (13 пт)
    for (const wd of body.split(" ")) { if (cur && cur + 1 + wd.length > 33) { lines++; cur = wd.length; } else cur += (cur ? 1 : 0) + wd.length; }
    const th = 0.27 + 0.235 * lines;
    slide.addText([{ text: nb(head), options: { bold: true, color: C.text1, fontSize: 13, breakLine: true } },
                   ...rich(body, { color: C.text1, fontSize: 13 })],
      { x: x + 0.22, y: cy, w: w - 0.44, h: th, valign: "top", margin: 0, isTextBox: true, objectName: nm("строка") });
    cy += th + 0.06;
    if (f) { formula(slide, f, x + 0.22, cy, w - 0.44, fh); cy += fh + 0.12; }
    else cy += 0.06;
  }
}
const content = (title) => { const s = pres.addSlide({ masterName: "CONTENT" }); s.addText(title, { placeholder: "title" }); return s; };
const txt = (s, t, o) => s.addText(rich(t), Object.assign({ fontSize: 15, color: C.text1, margin: 0, valign: "top", isTextBox: true,
                                                          objectName: nm("текст") }, o));
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: NAVY } } });
const b = (t) => ({ text: rich(t, { bold: true, color: C.text2 }), options: {} });
const TBL = { fontSize: 13, color: TEXT, border: { type: "solid", pt: 0.75, color: LINEC }, fill: { color: "FFFFFF" },
              valign: "middle", margin: [0, 0.07, 0, 0.07] };

// ------------------------------------------------------------------ 1. Титульный (как титульный лист РПЗ)
{
  const s = pres.addSlide({ masterName: "PLAIN" });
  const TNR = "Times New Roman";
  s.addImage({ path: EMBLEM, x: 0.75, y: 0.35, w: 1.0, h: 1.13, objectName: "герб" });
  s.addText([
    { text: "Министерство науки и высшего образования Российской Федерации", options: { breakLine: true } },
    { text: "Федеральное государственное автономное образовательное учреждение высшего образования", options: { breakLine: true } },
    { text: "«Московский государственный технический университет имени Н.Э. Баумана", options: { breakLine: true } },
    { text: "(национальный исследовательский университет)»", options: { breakLine: true } },
    { text: "(МГТУ им. Н.Э. Баумана)" },
  ], { x: 2.0, y: 0.3, w: 10.4, h: 1.3, fontSize: 13, bold: true, color: TEXT, fontFace: TNR, align: "center", valign: "middle",
       margin: 0, isTextBox: true, objectName: "шапка" });
  s.addShape(pres.shapes.LINE, { x: 0.75, y: 1.75, w: W - 1.5, h: 0, line: { color: TEXT, width: 2.5 }, objectName: "черта" });
  s.addText([{ text: "ФАКУЛЬТЕТ «Робототехника и комплексная автоматизация»", options: { breakLine: true } },
             { text: "КАФЕДРА РК-6 «Системы автоматизированного проектирования»" }],
    { x: 0.75, y: 1.9, w: W - 1.5, h: 0.7, fontSize: 14, color: TEXT, fontFace: TNR, margin: 0, isTextBox: true, objectName: "кафедра" });
  s.addText([{ text: "КУРСОВОЙ ПРОЕКТ", options: { fontSize: 22, bold: true, breakLine: true } },
             { text: "по дисциплине «Прикладная механика»", options: { fontSize: 16, breakLine: true } },
             { text: " ", options: { fontSize: 8, breakLine: true } },
             { text: "на тему:", options: { fontSize: 16, breakLine: true } },
             { text: "Проектирование и исследование тангенсного механизма ручного укупоривателя бутылки",
               options: { fontSize: 24, bold: true, color: NAVY } }],
    { x: 1.2, y: 2.85, w: W - 2.4, h: 2.3, color: TEXT, fontFace: TNR, align: "center", valign: "middle", margin: 0, isTextBox: true,
      objectName: "тема" });
  s.addText([{ text: "Выполнили: студенты группы РК6-55Б", options: { bold: true, breakLine: true } },
             { text: "Броцман Р.А., Девяткин Д.А., Калугин С.А.,", options: { breakLine: true } },
             { text: "Корнеев А.Е., Салихова Е.Д.", options: { breakLine: true } },
             { text: "Руководитель: ", options: { bold: true } }, { text: "Подчасов Е.О." }],
    { x: 7.4, y: 5.25, w: 5.2, h: 1.3, fontSize: 14, color: TEXT, fontFace: TNR, align: "left", valign: "top", margin: 0,
      isTextBox: true, objectName: "авторы" });
  s.addText("Москва, 2026", { x: 0.75, y: 6.85, w: W - 1.5, h: 0.35, fontSize: 14, color: TEXT, fontFace: TNR, align: "center",
    margin: 0, isTextBox: true, objectName: "год" });
  s.addNotes("Здравствуйте. Наша бригада представляет курсовой проект — ручной укупориватель бутылки на тангенсном механизме.");
}

// ------------------------------------------------------------------ 2. Цели и задачи
{
  const s = content("Цели и задачи");
  s.addShape(pres.shapes.RECTANGLE, { x: M, y: 1.3, w: 4.1, h: 4.6, fill: { color: LIGHT }, line: { type: "none" }, objectName: "цель_фон" });
  s.addText([{ text: "Цель", options: { bold: true, color: C.text2, fontSize: 16, breakLine: true } },
             { text: "Закрыть бутылку кронен-крышкой ручным настольным укупоривателем (Long Neck 0,33 л, крышка Ø26 мм).",
               options: { fontSize: 15, breakLine: true } },
             { text: " ", options: { fontSize: 10, breakLine: true } },
             { text: "Назначение", options: { bold: true, color: C.text2, fontSize: 16, breakLine: true } },
             { text: "Повышение производительности технологических процессов розлива спиртных напитков.", options: { fontSize: 15 } }],
    { x: M + 0.25, y: 1.5, w: 3.6, h: 4.2, color: TEXT, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "цель" });
  const tasks = ["Сформулировать техническое задание и критерии", "Выполнить метрический синтез механизма",
    "Провести кинематический анализ", "Выполнить первичный силовой расчёт", "Рассчитать звенья на прочность, подобрать сечения",
    "Выполнить уточнённый силовой расчёт с учётом масс", "Построить геометрическую модель (КОМПАС-3D)",
    "Провести расчёт МКЭ и доработать детали", "Изготовить и испытать прототип"];
  txt(s, "Задачи", { x: 5.1, y: 1.3, w: 4, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  s.addText(tasks.map((t, i) => ({ text: nb(t), options: { bullet: { type: "number" }, breakLine: i < tasks.length - 1 } })),
    { x: 5.1, y: 1.75, w: W - M - 5.1, h: 4.2, fontSize: 16, color: TEXT, valign: "top", margin: 0, paraSpaceAfter: 7,
      isTextBox: true, objectName: "задачи" });
  s.addNotes("Цель — закрыть бутылку кронен-крышкой ручным устройством; назначение — повышение производительности процессов розлива. " +
    "Задачи: сформулировать ТЗ, выполнить синтез, кинематику, силовые и прочностной расчёты, построить модель, провести расчёт МКЭ, изготовить прототип.");
}

// ------------------------------------------------------------------ 3. Постановка ТЗ
{
  const s = content("Постановка задачи и техническое задание");
  pic(s, "схема_постановка.png", M, 1.25, 4.5, 4.8, { caption: "0 — стойка, 1 — кулиса, 2 — камень, 3 — ползун" });
  const x = 5.4, tw = (W - M - x - 0.2) / 2, th = 0.98;
  txt(s, "Дано (ТЗ)", { x, y: 1.25, w: 3, h: 0.35, fontSize: 16, bold: true, color: C.text2 });
  [["0,33 л", "бутылка Long Neck, венчик 26 H 180"], ["Ø26 мм", "кронен-крышка тип I, жесть 0,22 мм"],
   ["≤ 120 Н", "сила руки на рукояти"], ["≤ 500 мм", "длина рукояти"],
   ["16 мм", "ход головки: подход 10 + обжим 6"], ["≥ 6 бут./мин", "производительность"]]
    .forEach(([bg, sm], i) => stat(s, x + (i % 2) * (tw + 0.2), 1.65 + Math.floor(i / 2) * (th + 0.14), tw, th, bg, sm));
  txt(s, "Требуется: найти размеры механизма (e, L, φн, φк), нагрузки и сечения звеньев; построить модель и прототип",
      { x, y: 5.1, w: W - M - x, h: 0.5, fontSize: 14 });
  formula(s, "ф_обжим.png", x, 5.55, 4.0, 0.58);
  result(s, "усилие укупоривания Fук = 1974 Н");
  s.addNotes("Механизм: стойка, кулиса с рукоятью, камень и ползун. Исходные данные — из ГОСТов на бутылку, крышку и эргономику. " +
    "Усилие укупоривания по сечению юбки крышки — 1974 ньютона. Размеры схемы на этом этапе неизвестны.");
}

// ------------------------------------------------------------------ 4. Метрический синтез
{
  const s = content("Метрический синтез");
  setup(s, [["Что делаем", "выбираем окно качания кулисы φн → φк и расстояние e", "ф_синтез.png", 0.95],
            ["Критерии", "минимум площади треугольника O–Bн–Bк и минимум углового хода ψ"],
            ["Ограничения", "P ≤ 120 Н, L ≤ 500 мм, e ≥ 10 мм"],
            ["Метод", "компромисс — точка равных относительных уступок"]]);
  const x = 4.45;
  pic(s, "синтез_площадь.png", x, 1.25, 4.7, 4.8, { caption: "Площадь треугольника при разных окнах" });
  pic(s, "синтез_уступки.png", x + 4.9, 1.25, W - M - x - 4.9, 4.8, { caption: "Минимальная площадь и уступки" });
  result(s, "окно качания 59,5° → 22,7° (ψ = 36,8°), e = 12,5 мм");
  s.addNotes("Синтез: подбирали окно качания кулисы и расстояние e. Компактность и малый угловой ход противоречат друг другу, " +
    "поэтому выбрали точку равных относительных уступок: угловой ход 36,8 градуса, e = 12,5 миллиметра.");
}

// ------------------------------------------------------------------ 5. Кинематика
{
  const s = content("Кинематический анализ");
  setup(s, [["Что делаем", "находим положения, скорости и ускорения ползуна", "ф_кинематика.png", 1.0],
            ["Закон движения", "трапеция угловой скорости: разгон, постоянная скорость, торможение при обжиме"],
            ["Ограничение", "скорость руки ≤ 0,7 м/с → ωmax = 1,4 рад/с"]]);
  const x = 4.45;
  pic(s, "омега.png", x, 1.25, 4.5, 4.8, { caption: "Угловая скорость кулисы ω(t)" });
  pic(s, "ползун_кинематика.png", x + 4.7, 1.25, W - M - x - 4.7, 4.8, { caption: "Координата, скорость, ускорение ползуна" });
  result(s, "ход головки 16 мм за 0,9 с, ωmax = 1,4 рад/с");
  s.addNotes("Закон движения кулисы — трапеция угловой скорости с максимумом 1,4 радиана в секунду; ход занимает 0,9 секунды. " +
    "Скорости и ускорения ползуна получены дифференцированием функции положения yD = e tg φ.");
}

// ------------------------------------------------------------------ 6. Первичный силовой — по звеньям
{
  const s = content("Первичный силовой расчёт: по звеньям");
  txt(s, "Постановка: без учёта масс и трения; уравнения равновесия звеньев:",
      { x: M, y: 1.14, w: 8.2, h: 0.32, fontSize: 13, color: C.accent2 });
  formula(s, "ф_равновесие.png", 8.95, 1.12, 3.75, 0.34);
  const cw = (W - 2 * M - 2 * 0.25) / 3;
  [["звено1.png", "ур1.png", "Звено 1 — кулиса с рукоятью"], ["звено2.png", "ур2.png", "Звено 2 — камень"],
   ["звено3.png", "ур3.png", "Звено 3 — ползун"]].forEach(([fig, eq, cap], i) => {
    const x = M + i * (cw + 0.25);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.6, w: cw, h: 4.5, fill: { color: "FFFFFF" }, line: { color: LINEC, width: 0.75 },
      objectName: nm("звено") });
    txt(s, cap, { x: x + 0.15, y: 1.68, w: cw - 0.3, h: 0.32, fontSize: 14, bold: true, color: C.text2 });
    pic(s, fig, x + 0.1, 2.02, cw - 0.2, 2.3, { card: false, pad: 0.04 });
    pic(s, eq, x + 0.1, 4.4, cw - 0.2, 1.6, { card: false, pad: 0.03 });
  });
  result(s, "Pmax = 112,8 Н < 120 Н, длина рукояти L = 500 мм");
  s.addNotes("Силовой расчёт по звеньям: для кулисы, камня и ползуна — по три уравнения равновесия. Максимальная сила руки " +
    "112,8 ньютона, меньше допустимых 120.");
}

// ------------------------------------------------------------------ 7. Эпюры
{
  const s = content("Внутренние силовые факторы кулисы");
  setup(s, [["Что делаем", "строим эпюры N, Q, M кулисы для подбора сечения"],
            ["Схема", "балка OK длиной 500 мм; сила камня — в точке D, сила руки — в точке K", "ф_момент.png", 0.4],
            ["Опасное положение", "φу = 41,6° — начало пластической деформации: P = 112,8 Н, R12 = 2515 Н"]]);
  pic(s, "эпюры_фи_у.png", 4.45, 1.25, 5.55, 4.8, { caption: "Схема и эпюры N, Q, M кулисы при φу" });
  const x = 10.2, w = W - M - x;
  stat(s, x, 1.25, w, 1.45, "40,8 Н·м", "|M| под камнем, точка D");
  stat(s, x, 2.85, w, 1.45, "2430,5 Н", "поперечная сила на участке O–D");
  stat(s, x, 4.45, w, 1.45, "−75,0 Н", "продольная сила в кулисе");
  result(s, "опасное сечение — под камнем: |MD| = 40,8 Н·м");
  s.addNotes("Кулису рассматриваем как балку длиной 500 миллиметров. Наибольший изгибающий момент — 40,8 ньютон-метра под камнем.");
}

// ------------------------------------------------------------------ 8. Прочность
{
  const s = content("Прочностной расчёт и сечения звеньев");
  setup(s, [["Условие прочности", "по пределу текучести, коэффициент запаса n = 2,5", "ф_прочность.png", 1.15],
            ["Сортамент", "лист — ГОСТ 19903-2015, круг — ГОСТ 2590-2006"],
            ["Проверки", "шток — устойчивость; ось и палец — срез; отверстия — смятие"]]);
  pic(s, "сечения.png", 4.45, 1.25, W - M - 4.45, 2.15, { caption: "Принятые сечения" });
  s.addTable([
    [hdr("Элемент"), hdr("Проверка"), hdr("МПа"), hdr("Допуск")],
    ["Кулиса 8 · 18, Ст3сп", "изгиб", b("94,8"), "98"],
    ["Шток Ø8, Ст3сп", "сжатие / устойчивость", b("39,3 / nу = 6,2"), "98 / ≥ 3"],
    ["Ось O Ø10 / палец D Ø10", "срез", b("31,0 / 32,0"), "50"],
    ["Отверстие кулисы со ступицей", "смятие", b("12,2"), "24"],
  ], Object.assign({ x: 4.45, y: 3.62, w: W - M - 4.45, colW: [3.0, 2.2, 1.75, 1.33], rowH: 0.45, fontSize: 14, objectName: "проверки" }, { ...TBL, fontSize: 14 }));
  result(s, "кулиса 8 × 18 (Ст3сп), шток Ø8, ось и палец Ø10");
  s.addNotes("Сечения подбирали по условию прочности с запасом 2,5 и по сортаменту. Кулиса — полоса 8 на 18 из Ст3сп. " +
    "Шток диаметром 8 проходит по устойчивости с запасом 6,2. Без ступицы отверстие кулисы не проходило по смятию.");
}

// ------------------------------------------------------------------ 9. Уточнённый
{
  const s = content("Уточнённый силовой расчёт");
  setup(s, [["Что делаем", "повторяем силовой расчёт с массами звеньев"],
            ["Метод", "кинетостатика: добавляем силы тяжести и инерции, трение не учитываем", "ф_инерция.png", 0.32],
            ["Критерий", "изменение силы руки и реакций; проверка принятых сечений"]]);
  pic(s, "схемы_уточняющий.png", 4.45, 1.25, 3.75, 4.8, { caption: "Схемы с силами тяжести и инерции" });
  pic(s, "сила_руки_t.png", 8.4, 1.25, W - M - 8.4, 4.8, { caption: "Сила руки P(t): первичный, уточнённый, допустимая" });
  result(s, "Pmax = 109,9 Н (−2,6 %), сечения сохраняются");
  s.addNotes("Добавили силы тяжести и инерции кулисы и ползуна. Максимум силы руки снизился на 2,6 процента, обе кривые ниже 120 ньютонов.");
}

// ------------------------------------------------------------------ 10. МКЭ
{
  const s = content("Расчёт методом конечных элементов");
  setup(s, [["Что делаем", "расчёт напряжений в деталях в APM FEM при φу = 41,6°"],
            ["Критерий", "σmax ≤ [σ] материала детали"],
            ["Доработка", "скругления, замкнутая обойма камня; материал — самый простой из достаточных"]]);
  const gx = 4.45, gw = 2.4, gh = 2.3;
  pic(s, "мкэ_кулиса.png", gx, 1.25, gw, gh, { caption: "Кулиса" });
  pic(s, "мкэ_ползун.png", gx + gw + 0.2, 1.25, gw, gh, { caption: "Ползун" });
  pic(s, "мкэ_камень.png", gx, 1.25 + gh + 0.2, gw, gh, { caption: "Камень" });
  pic(s, "мкэ_направляющая.png", gx + gw + 0.2, 1.25 + gh + 0.2, gw, gh, { caption: "Направляющая" });
  const tx = gx + 2 * gw + 0.4;
  s.addTable([
    [hdr("Деталь"), { text: [{ text: "σ" }, { text: "max", options: { subscript: true } }, { text: ", МПа" }],
                      options: { bold: true, color: "FFFFFF", fill: { color: NAVY } } }, hdr("[σ]")],
    ["Кулиса", b("92,6"), "98"], ["Ползун", b("95,9 → 49,0"), "98"], ["Камень", b("646 → 100"), "142"],
    ["Направляющая", b("920 → 136,2"), "142"], ["Палец D", b("192"), "314"],
  ], Object.assign({ x: tx, y: 1.25, w: W - M - tx, colW: [1.5, 1.08, 0.503], rowH: 0.45 }, TBL, { fontSize: 12, objectName: "мкэ_таблица" }));
  stat(s, tx, 4.3, W - M - tx, 1.3, "−22 % массы", "кулиса 577,6 → 449,7 г");
  result(s, "после доработки σmax ≤ [σ] у всех деталей");
  s.addNotes("По картам напряжений доработали детали: в камне и направляющей пики снизились в 6–7 раз, в ползуне вдвое, " +
    "кулиса стала легче на 22 процента без роста напряжений.");
}

// ------------------------------------------------------------------ 11. Прототипирование: детали до и после МКЭ (замечание Корнеева)
{
  const s = content("Прототипирование: детали до и после МКЭ");
  const names = [["кулиса", "Кулиса", "облегчена: 577,6 → 447,7 г"], ["ползун", "Ползун", "скругления, головка-колокол"],
                 ["камень", "Камень", "замкнутая обойма"], ["направляющая", "Направляющая", "планка 12 мм, скругления"]];
  const cw = (W - 2 * M - 3 * 0.25) / 4;
  txt(s, "До МКЭ", { x: M, y: 1.15, w: 3, h: 0.3, fontSize: 14, bold: true, color: C.text2 });
  txt(s, "После МКЭ", { x: M, y: 3.55, w: 3, h: 0.3, fontSize: 14, bold: true, color: C.text2 });
  names.forEach(([k, title, what], i) => {
    const x = M + i * (cw + 0.25);
    pic(s, `фэм_до_${k}.png`, x, 1.5, cw, 2.0, { caption: title });
    pic(s, `фэм_после_${k}.png`, x, 3.9, cw, 2.2, { caption: `${title}: ${what}` });
  });
  result(s, "детали доработаны по МКЭ, напечатаны (FDM) и собраны");
  s.addNotes("Слева направо — кулиса, ползун, камень и направляющая до и после доработки по расчёту МКЭ. Кулису облегчили, " +
    "у ползуна сделали скругления и головку-колокол, камень стал замкнутой обоймой, у направляющей усилена планка. " +
    "Доработанные детали напечатаны на 3D-принтере и собраны.");
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
  s.addText(items.flatMap((t, i) => { const r = rich(t); r[0].options.bullet = true; if (i < items.length - 1) r[r.length - 1].options.breakLine = true; return r; }),
    { x: M, y: 1.35, w: 7.4, h: 5.0, fontSize: 17, color: TEXT, margin: 0, valign: "top", paraSpaceAfter: 12,
      isTextBox: true, objectName: "итоги" });
  pic(s, "схема_результат.png", 8.4, 1.25, W - M - 8.4, 5.75, { caption: "Схема с размерами по результатам расчёта" });
  s.addNotes("Итак, спроектирован укупориватель: ход 16 миллиметров, усилие 1974 ньютона при силе руки не больше 113 ньютонов. " +
    "Справа — схема механизма с размерами, полученными в расчётах.");
}

// ------------------------------------------------------------------ 13. Спасибо за внимание
{
  const s = pres.addSlide({ masterName: "PLAIN" });
  s.addImage({ path: EMBLEM, x: W / 2 - 0.5, y: 0.7, w: 1.0, h: 1.13, objectName: "герб" });
  s.addText("Спасибо за внимание!", { x: M, y: 2.2, w: W - 2 * M, h: 0.9, fontSize: 40, bold: true, color: NAVY, align: "center",
    margin: 0, isTextBox: true, objectName: "заголовок" });
  s.addText("Проектирование и исследование тангенсного механизма ручного укупоривателя бутылки", { x: M, y: 3.15, w: W - 2 * M,
    h: 0.5, fontSize: 18, color: GREY, align: "center", margin: 0, isTextBox: true, objectName: "тема" });
  pic(s, "00_общий_вид.png", W / 2 - 1.4, 3.85, 2.8, 3.3, { card: false, pad: 0 });
  s.addNotes("Спасибо за внимание! Готовы ответить на вопросы.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("ok", OUT);
})();
