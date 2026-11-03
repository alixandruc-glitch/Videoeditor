// Liest die Sound-Effekt-Zeitpunkte (window.__sfx) aus index.html und schreibt assets/sfx.json.
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
  }));
  await browser.close();
  fs.writeFileSync(path.join(dir, "assets", "sfx.json"), JSON.stringify(data, null, 1));
  console.log(`${data.sfx.length} Sound-Effekte, Dauer ${data.duration}s → assets/sfx.json`);
})();
