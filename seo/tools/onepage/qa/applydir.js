const fs = require("fs"); const path = require("path");
state.applyDir = async (dir, opts = {}) => {
  const files = fs.readdirSync(dir).filter(f => f.endsWith(".json")).sort();
  const out = []; const log = [];
  for (const f of files) {
    const slug = f.slice(0, -5);
    if (opts.only && !opts.only.includes(slug)) continue;
    if (opts.skip && opts.skip.includes(slug)) continue;
    let rep;
    try { rep = await state.applyOps2(path.join(dir, f), {noHistory: !!opts.noHistory, force: !!opts.force}); }
    catch (e) { rep = {slug, error: String(e).slice(0, 300)}; }
    log.push(rep);
    out.push(`${slug.padEnd(22)} applied=${rep.applied ?? "-"} patch=${rep.patchStatus ?? "-"} seo=${rep.seo ?? "-"} skipped=${(rep.skipped || []).length} verifyFail=${(rep.verifyFail || []).length}${rep.error ? " ERROR " + rep.error : ""}`);
  }
  fs.writeFileSync(dir + ".report.json", JSON.stringify(log, null, 1));
  return out;
};
return "applyDir installed";
