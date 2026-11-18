// paper.html → «Инструкция по сборке и эксплуатации.pdf» (Chromium, A4, с фоном). NODE_PATH — где установлен playwright.
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch({ headless: true });
  const pg = await b.newPage();
  await pg.goto("file:///" + path.join(__dirname, "paper.html").replace(/\\/g, "/"));
  await pg.waitForTimeout(500);
  const over = await pg.evaluate(() => [...document.querySelectorAll(".page")].map((p, i) => [i + 1, p.scrollHeight - p.clientHeight]).filter(x => x[1] > 1));
  console.log("переполненные страницы:", over.length ? JSON.stringify(over) : "нет");
  await pg.pdf({ path: path.join(__dirname, "Инструкция по сборке и эксплуатации.pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log("готово");
})();
