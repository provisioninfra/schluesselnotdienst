const fs = require("fs");
const orte = JSON.parse(fs.readFileSync("/home/user/schluesselnotdienst/seo/tools/orte.json", "utf8"));
const towns = (Array.isArray(orte) ? orte : orte.orte).map(o => o.slug).sort();
const all = ["", "turoffnung", "impressum", "agb", "datenschutzerklarung"].concat(towns); const slugs = all.slice(state.qaFrom||0, (state.qaFrom||0)+ (state.qaN||6));
if (!state.qa || state.qa.isClosed()) state.qa = await page.context().newPage();
const p = state.qa; const results = [];
for (const slug of slugs) for (const [vp, w, h] of [["desk", 1440, 900], ["mob", 390, 844]]) {
  const errors = [], failed = [];
  const onCon = m => { if (m.type() === "error") errors.push(m.text().slice(0, 220)); };
  const onFail = r => failed.push("FAIL " + r.url().slice(0, 160));
  const onResp = r => { if (r.status() >= 400) failed.push(r.status() + " " + r.url().slice(0, 160)); };
  p.on("console", onCon); p.on("requestfailed", onFail); p.on("response", onResp);
  await p.setViewportSize({width: w, height: h});
  const url = "https://schluesselnotdienst-baumann.de/" + slug + "?qa=" + Date.now();
  try { await p.goto(url, {waitUntil: "networkidle", timeout: 60000}); } catch (e) { errors.push("goto: " + String(e.message).slice(0, 120)); }
  await p.waitForTimeout(700);
  await p.evaluate(async () => { for (const b of document.querySelectorAll("[class*=gdpr],[class*=cookie]")) b.style.display = "none"; const H = document.documentElement.scrollHeight; for (let y = 0; y < H; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); } window.scrollTo(0, 0); });
  await p.waitForTimeout(900);
  const info = await p.evaluate(() => {
    const iw = innerWidth; const sw = document.documentElement.scrollWidth;
    const heads = [...document.querySelectorAll("h1,h2,h3,h4")].filter(e => e.getBoundingClientRect().width > 0).map(e => e.tagName + ":" + e.textContent.trim().replace(/\s+/g, " ").slice(0, 60));
    const imgs = [...document.querySelectorAll("img")].filter(i => i.getBoundingClientRect().width > 0);
    const broken = imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => (i.currentSrc || i.src).slice(0, 120));
    const noAlt = imgs.filter(i => !i.getAttribute("alt") || !i.getAttribute("alt").trim()).map(i => (i.currentSrc || i.src).slice(0, 120));
    const links = [...document.querySelectorAll("a[href]")].map(a => a.getAttribute("href"));
    const internal = [...new Set(links.filter(x => x && (x.startsWith("/") || x.includes("schluesselnotdienst-baumann.de"))))];
    const external = [...new Set(links.filter(x => x && /^https?:/.test(x) && !x.includes("schluesselnotdienst-baumann.de")))];
    const other = [...new Set(links.filter(x => x && /^(tel:|mailto:|#)/.test(x)))];
    const over = [...document.querySelectorAll("body *")].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > iw + 2 && getComputedStyle(e).position !== "fixed"; }).slice(0, 6).map(e => e.tagName + "." + String(e.className).slice(0, 50) + " right=" + Math.round(e.getBoundingClientRect().right));
    const txt = document.body.innerText; const junk = ["undefined", "null", "{{", "NaN", "[object"].filter(k => txt.includes(k));
    const h1s = [...document.querySelectorAll("h1")].filter(e => e.getBoundingClientRect().width > 0).length;
    return {sw, iw, h1s, heads, imgCount: imgs.length, broken, noAlt, internal, external, other, over, junk, height: document.documentElement.scrollHeight};
  });
  await p.screenshot({path: `/tmp/claude-0/-home-user-schluesselnotdienst/b61433d6-4144-509c-9875-45e76cdc31dd/scratchpad/bd/qa/${slug || "home"}_${vp}.png`, fullPage: true});
  p.off("console", onCon); p.off("requestfailed", onFail); p.off("response", onResp);
  const rec = Object.assign({slug: slug || "/", vp, errors: [...new Set(errors)], failed: [...new Set(failed)]}, info); results.push(rec); fs.appendFileSync("/tmp/claude-0/-home-user-schluesselnotdienst/b61433d6-4144-509c-9875-45e76cdc31dd/scratchpad/bd/qa/results.jsonl", JSON.stringify(rec) + "\n");
}
return {pages: results.length, withErrors: results.filter(r => r.errors.length).length, withFailed: results.filter(r => r.failed.length).length, overflow: results.filter(r => r.sw > r.iw).map(r => r.slug + "/" + r.vp), broken: results.filter(r => r.broken.length).map(r => r.slug + "/" + r.vp), multiH1: results.filter(r => r.h1s !== 1).map(r => r.slug + "/" + r.vp + "=" + r.h1s)};
