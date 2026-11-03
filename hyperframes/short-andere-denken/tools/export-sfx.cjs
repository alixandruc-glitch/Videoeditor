// Liest Sound-Effekt-Zeitpunkte (window.__sfx) und Sprechertext (window.__vo) aus index.html → assets/sfx.json.
// Aufruf: node tools/export-sfx.cjs   (benötigt das npm-Paket "playwright")
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const dir = path.resolve(__dirname, "..");
  const browser = await chromium.launch(
    process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {},
  );
  const page = await browser.newPage();
  await page.goto("file://" + path.join(dir, "index.html"));
  const data = await page.evaluate(() => ({
    duration: +document.getElementById("root").dataset.duration,
    sfx: window.__sfx,
    vo: window.__vo,
  }));
  await browser.close();
  fs.writeFileSync(path.join(dir, "assets", "sfx.json"), JSON.stringify(data, null, 1));
  console.log(`${data.sfx.length} Sound-Effekte, ${data.vo.length} Sprecherzeilen, Dauer ${data.duration}s → assets/sfx.json`);
})();
