// Презентация курсового проекта по образцу курсовой/примеры/Презентация.pptx (1).pdf — 13 слайдов, 16:9.
// Картинки — fig/ (make_figs.py, рисунки v30). Сборка: node build_pres.js (NODE_PATH — папка с pptxgenjs).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const FIG = path.join(__dirname, "fig");
const SIZES = JSON.parse(fs.readFileSync(path.join(FIG, "sizes.json"), "utf8"));
const OUT = path.join(__dirname, "Презентация_укупориватель.pptx");
const THEME = {
  name: "Укупориватель МГТУ", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "1F2328", lt1: "FFFFFF", dk2: "1B3A6B", lt2: "EEF2F8", accent1: "1B3A6B", accent2: "D4A72C",
            accent3: "5B6573", accent4: "2F8F5B", accent5: "B03A2E", accent6: "7FAE6A", hlink: "1B3A6B", folHlink: "5B6573" },
};
const NAVY = "1B3A6B", GOLD = "D4A72C", TINT = "EEF2F8", MUTED = "5B6573";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";                       // 10 × 5,625″
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Тангенсный механизм ручного укупоривателя";
const C = pres.SchemeColor;
const EMBLEM = path.join(FIG, "герб.png");

pres.defineSlideMaster({
  title: "TITLE", background: { color: NAVY },
  objects: [{ image: { path: EMBLEM, x: 9.0, y: 0.25, w: 0.72, h: 0.81 } }],
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  objects: [
    { image: { path: EMBLEM, x: 9.18, y: 0.18, w: 0.55, h: 0.62 } },
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.22, w: 8.5, h: 0.62, fontSize: 26, bold: true,
                                color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 9.25, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right" },
});

// картинка, вписанная в рамку (x, y, w, h) по центру
function pic(slide, rel, x, y, w, h, extra = {}) {
  const [pw, ph] = SIZES[rel];
  const k = Math.min(w / pw, h / ph), iw = pw * k, ih = ph * k;
  slide.addImage({ path: path.join(FIG, rel), x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih,
                   objectName: path.basename(rel), ...extra });
}
const text = (slide, t, o) => slide.addText(t, { isTextBox: true, fontSize: 15, color: C.text1, margin: 0, valign: "top", ...o });
const caption = (slide, t, x, y, w) => text(slide, t, { x, y, w, h: 0.3, fontSize: 11, color: MUTED, align: "center" });
// карточка-число: крупное значение и подпись
function stat(slide, x, y, w, h, value, label) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.08,
                                                   objectName: "card " + label });
  text(slide, value, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: h * 0.52, fontSize: 26, bold: true, color: C.text2, valign: "middle" });
  text(slide, label, { x: x + 0.15, y: y + h * 0.6, w: w - 0.3, h: h * 0.36, fontSize: 12, color: MUTED });
}
// итог внизу слайда — плашка с золотым номером-кружком (мотив презентации)
function result(slide, t, y = 4.78) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 8.6, h: 0.5, fill: { color: TINT }, line: { color: TINT },
                                                   rectRadius: 0.08, objectName: "итог" });
  slide.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.1, w: 0.3, h: 0.3, fill: { color: GOLD }, line: { color: GOLD } });
  text(slide, "!", { x: 0.62, y: y + 0.1, w: 0.3, h: 0.3, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  text(slide, t, { x: 1.05, y: y + 0.05, w: 7.95, h: 0.4, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
}
const content = (title) => { const s = pres.addSlide({ masterName: "CONTENT" }); s.addText(title, { placeholder: "title" }); return s; };

// 1 титул
let s = pres.addSlide({ masterName: "TITLE" });
text(s, "Курсовой проект", { x: 0.6, y: 0.55, w: 5.2, h: 0.4, fontSize: 16, color: GOLD, bold: true });
text(s, "Проектирование и исследование тангенсного механизма ручного укупоривателя бутылки",
     { x: 0.6, y: 1.05, w: 5.0, h: 2.0, fontSize: 28, bold: true, color: "FFFFFF" });
text(s, "РК6-55Б · бригада №2", { x: 0.6, y: 3.55, w: 5.0, h: 0.35, fontSize: 15, color: "FFFFFF" });
text(s, "Броцман Р.А., Девяткин Д.А., Калугин С.А., Корнеев А.Е., Салихова Е.Д.", { x: 0.6, y: 3.95, w: 5.0, h: 0.6, fontSize: 13, color: "CADCFC" });
text(s, "Руководитель: Подчасов Е.О.", { x: 0.6, y: 4.55, w: 5.0, h: 0.3, fontSize: 13, color: "FFFFFF" });
text(s, "МГТУ им. Н.Э. Баумана, кафедра РК6 · 2026", { x: 0.6, y: 4.9, w: 5.0, h: 0.3, fontSize: 11, color: "CADCFC" });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.0, y: 1.2, w: 3.4, h: 4.0, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, rectRadius: 0.12 });
pic(s, "00_общий_вид.png", 6.15, 1.3, 3.1, 3.8);

// 2 цели и задачи
s = content("Цели и задачи");
text(s, [{ text: "Цель: ", options: { bold: true, color: C.text2 } },
         { text: "спроектировать, исследовать и изготовить ручной укупориватель бутылки Long Neck 0,33 л с приводом тангенсным механизмом." }],
     { x: 0.5, y: 1.05, w: 8.6, h: 0.6 });
const TASKS = [["Постановка ТЗ", "назначение, качественные и количественные критерии"],
               ["Расчёт", "синтез, кинематика, первичный силовой, прочностной и уточняющий силовой расчёты"],
               ["Конструирование", "3D-модели и сборка, расчёт МКЭ, доработка деталей"],
               ["Испытания", "прототип на 3D-принтере, сборка, инструкция по сборке и эксплуатации"]];
TASKS.forEach(([h, d], i) => {
  const x = 0.5 + i * 2.2, y = 1.95;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.0, h: 2.65, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.08 });
  s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: y + 0.18, w: 0.5, h: 0.5, fill: { color: GOLD }, line: { color: GOLD } });
  text(s, String(i + 1), { x: x + 0.15, y: y + 0.18, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  text(s, h, { x: x + 0.15, y: y + 0.85, w: 1.75, h: 0.4, fontSize: 13, bold: true, color: C.text2 });
  text(s, d, { x: x + 0.15, y: y + 1.3, w: 1.75, h: 1.25, fontSize: 12, color: C.text1 });
});

// 3 устройство и принцип работы
s = content("Устройство и принцип работы");
text(s, [{ text: "Тангенсный механизм: ", options: { bold: true, color: C.text2, breakLine: true } },
         { text: "кулиса с рукоятью поворачивается вокруг оси O, камень скользит по кулисе и через палец D двигает ползун строго вертикально:", options: { breakLine: true } },
         { text: "y = e · tg φ", options: { bold: true, fontSize: 20, color: C.text2, breakLine: true } },
         { text: "Головка с конической горловиной надевается на кронен-крышку и обжимает её юбку на венчике бутылки." }],
     { x: 0.5, y: 1.1, w: 4.6, h: 2.4, paraSpaceAfter: 8 });
stat(s, 0.5, 3.7, 2.15, 0.95, "16 мм", "ход головки");
stat(s, 2.85, 3.7, 2.15, 0.95, "6 мм", "из них — обжим крышки");
pic(s, "01_без_кожуха.png", 5.4, 1.0, 3.8, 4.1);

// 4 исходные данные
s = content("Исходные данные");
[["0,33 л", "бутылка Long Neck, Ø60,4 × 226,5 мм"], ["Ø26 мм", "кронен-крышка, жесть 0,22 мм"], ["1974 Н", "усилие укупоривания"],
 ["≤ 120 Н", "допустимая сила руки"], ["16 мм", "ход головки (10 подход + 6 обжим)"], ["500 мм", "длина рукояти"]]
  .forEach(([v, l], i) => stat(s, 0.5 + (i % 3) * 2.92, 1.15 + Math.floor(i / 3) * 1.55, 2.72, 1.3, v, l));
text(s, "Материалы: звенья — Ст3сп, сталь 45, сталь 40Х (по напряжениям); кожух — АБС; прототип — печать FDM.",
     { x: 0.5, y: 4.4, w: 8.6, h: 0.5, fontSize: 13, color: MUTED });

// 5 синтез
s = content("Синтез: выбор окна качания кулисы");
pic(s, "v30/рис3.png", 0.5, 1.0, 4.2, 3.4); caption(s, "площадь треугольника O–Bн–Bк при разных окнах", 0.5, 4.4, 4.2);
pic(s, "v30/рис4.png", 4.9, 1.0, 4.2, 3.4); caption(s, "минимальная площадь и относительные уступки", 4.9, 4.4, 4.2);
result(s, "Принято: ψ = 36,75°, окно 59,47° → 22,72°, e = 12,53 мм (равные уступки 25,3 %)");

// 6 кинематика
s = content("Кинематический анализ");
pic(s, "v30/рис2.png", 0.5, 0.95, 3.2, 3.35); caption(s, "кинематическая схема", 0.5, 4.33, 3.2);
pic(s, "v30/рис6.png", 3.9, 0.95, 5.2, 3.35); caption(s, "координата, скорость и ускорение ползуна", 3.9, 4.33, 5.2);
result(s, "Трапецеидальный закон ω(t): ωmax = 1,40 рад/с, рабочий ход 0,913 с");

// 7 первичный силовой
s = content("Первичный силовой расчёт");
pic(s, "v30/рис8.png", 0.5, 0.95, 4.3, 3.35); caption(s, "расчётные схемы звеньев", 0.5, 4.33, 4.3);
pic(s, "v30/рис10.png", 5.0, 0.95, 4.1, 3.35); caption(s, "сила руки и реакции от угла φ", 5.0, 4.33, 4.1);
result(s, "9 уравнений равновесия: Pmax = 112,8 Н ≤ 120 Н при φу = 41,63°; R12 = 2515 Н");

// 8 прочностной
s = content("Прочностной расчёт");
pic(s, "v30/рис11.png", 0.5, 0.95, 4.6, 3.35); caption(s, "эпюры N, Q, M кулисы при φу", 0.5, 4.33, 4.6);
stat(s, 5.35, 1.0, 3.75, 1.0, "8 × 18 мм", "кулиса Ст3сп: σ = 94,6 ≤ 98 МПа");
stat(s, 5.35, 2.15, 3.75, 1.0, "Ø8 мм", "шток ползуна: запас устойчивости 6,15");
stat(s, 5.35, 3.3, 3.75, 1.0, "Ø10 мм", "ось O и палец D: срез 32 ≤ 50 МПа");
result(s, "Сечения подобраны по опасным положениям φу (обжим) и φк (конец хода)");

// 9 уточняющий
s = content("Уточняющий силовой расчёт");
pic(s, "v30/рис14.png", 0.5, 0.95, 4.3, 3.35); caption(s, "схемы с силами тяжести и инерции", 0.5, 4.33, 4.3);
pic(s, "v30/рис15.png", 5.0, 0.95, 4.1, 3.35); caption(s, "сила руки и реакции с учётом масс", 5.0, 4.33, 4.1);
result(s, "Учёт масс и инерции: сила руки 112,8 → 109,9 Н (−2,6 %), реакции — менее 1 %");

// 10 3D
s = content("3D-модель (КОМПАС-3D v25)");
pic(s, "детали.png", 0.5, 0.95, 6.1, 3.75);
pic(s, "00_общий_вид.png", 6.8, 0.95, 2.3, 3.75);
result(s, "11 деталей, сборка — 29 сопряжений; на всём ходе рукояти пересечений нет");

// 11 МКЭ
s = content("Расчёт МКЭ (APM FEM): до и после доработки");
[["apm_кулиса.png", "Кулиса: 92,6 МПа, пазы облегчения −22 % массы"], ["apm_ползун.png", "Ползун: 95,9 → 49,0 МПа"],
 ["apm_камень.png", "Камень: 646 → 100 МПа, сталь 45"], ["apm_направляющая.png", "Направляющая: 920 → 136 МПа, сталь 45"]]
  .forEach(([f, c], i) => { const x = 0.5 + (i % 2) * 4.4, y = 0.95 + Math.floor(i / 2) * 1.92;
    pic(s, f, x, y, 4.2, 1.55); caption(s, c, x, y + 1.55, 4.2); });
result(s, "Материал — минимально достаточный: Ст3сп / сталь 45 / сталь 40Х");

// 12 прототип
s = content("Прототип: 3D-печать и испытание");
pic(s, "сборка.png", 0.5, 0.95, 8.6, 2.45);
stat(s, 0.5, 3.6, 2.75, 1.05, "FDM, 0,4 мм", "все детали напечатаны, резьбы М10 × 1,5 — тоже");
stat(s, 3.42, 3.6, 2.75, 1.05, "10 шагов", "сборка по инструкции, ключ S5 для винта");
stat(s, 6.35, 3.6, 2.75, 1.05, "Ø10,6", "испытание: кулиса сломалась на оси — введён зазор 0,3 мм");

// 13 заключение
s = pres.addSlide({ masterName: "TITLE" });
text(s, "Заключение", { x: 0.6, y: 0.4, w: 6, h: 0.6, fontSize: 28, bold: true, color: "FFFFFF" });
text(s, ["Спроектирован укупориватель: ход 16 мм, усилие 1974 Н, сила руки ≤ 112,8 Н",
         "Синтез, кинематика, силовые и прочностной расчёты выполнены",
         "3D-модели доработаны по МКЭ, материалы выбраны по напряжениям",
         "Прототип напечатан и испытан, по испытанию введены зазоры в подвижных посадках"]
       .map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } })),
     { x: 0.6, y: 1.3, w: 5.3, h: 3.5, fontSize: 16, color: "FFFFFF", paraSpaceAfter: 12 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.1, y: 1.3, w: 3.4, h: 3.6, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, rectRadius: 0.12 });
pic(s, "03_рукоять_внизу.png", 6.2, 1.4, 3.2, 3.4);

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("сохранено:", OUT);
})();
