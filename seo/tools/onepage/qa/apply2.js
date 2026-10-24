const fs = require("fs");
const SITE = state.SITE;
const pick = (obj, tmpl) => { if (tmpl === null || typeof tmpl !== "object" || Array.isArray(tmpl)) return obj === undefined ? null : obj; const out = {}; for (const k of Object.keys(tmpl)) out[k] = obj && typeof obj === "object" ? pick(obj[k], tmpl[k]) : null; return out; };
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
// index page: sections, molecules (with paths), atoms (with paths)
const index = (version, pageId) => {
  const secs = {}, mols = {}, atoms = {};
  for (const sec of version.sections || []) {
    secs[sec._id] = {obj: sec, path: {siteId: SITE, pageId, organismId: sec._id, organismLocation: "section"}};
    const layer = sec.layer; if (!layer) continue;
    for (const fr of layer.frames || []) for (const row of fr.rows || []) for (const mol of row.molecules || []) {
      const mp = {siteId: SITE, pageId, organismId: sec._id, organismLocation: "section", layerId: layer._id, frameId: fr._id, rowId: row._id, moleculeId: mol._id};
      mols[mol._id] = {obj: mol, path: mp};
      for (const atom of mol.atoms || []) atoms[atom._id] = {obj: atom, path: Object.assign({}, mp, {atomId: atom._id})};
    }
  }
  return {secs, mols, atoms};
};
state.applyOps2 = async (opsPath, opts = {}) => {
  const ops = JSON.parse(fs.readFileSync(opsPath, "utf8"));
  const rep = {slug: ops.slug, applied: 0, skipped: [], verifyFail: [], seo: null};
  const page = await state.fetchPage(SITE, ops.pageId);
  if (!opts.noHistory) rep.history = (await state.rpc("versionHistory.saveToHistory", {pageId: ops.pageId, siteId: SITE, type: "private"})).status;
  const ix = index(page.version, ops.pageId);
  const items = [];
  for (const p of ops.patches) {
    const target = p.target || "atom";
    const ent = target === "organism" ? ix.secs[p.organismId] : target === "molecule" ? ix.mols[p.moleculeId] : ix.atoms[p.atomId];
    if (!ent) { rep.skipped.push({note: p.note, reason: "not found"}); continue; }
    const cur = pick(ent.obj, p.snapshot);
    if (!eq(cur, p.snapshot) && !opts.force) { rep.skipped.push({note: p.note, reason: "snapshot mismatch", cur: JSON.stringify(cur).slice(0, 160)}); continue; }
    items.push({target, path: ent.path, value: p.value, snapshot: p.snapshot, note: p.note, id: p.organismId || p.moleculeId || p.atomId});
  }
  if (items.length) {
    const r = await state.rpc("transactions.processV2", {id: state.uuid(), type: "do", actionList: items.map(i => ({target: i.target, type: "patch", path: i.path, value: i.value, snapshot: i.snapshot})), siteId: SITE});
    rep.patchStatus = r.status; rep.patchResult = JSON.stringify(r.json).slice(0, 160); rep.applied = items.length;
  }
  if (ops.seo) rep.seo = (await state.rpc("pagesV2.updateVersionData", {siteId: SITE, pageId: ops.pageId, version: ops.seo})).status;
  const page2 = await state.fetchPage(SITE, ops.pageId); const ix2 = index(page2.version, ops.pageId);
  for (const i of items) { const ent = i.target === "organism" ? ix2.secs[i.id] : i.target === "molecule" ? ix2.mols[i.id] : ix2.atoms[i.id]; const cur = pick(ent.obj, i.value); if (!eq(cur, i.value)) rep.verifyFail.push(i.note); }
  if (ops.seo) for (const k of Object.keys(ops.seo)) if (!eq(page2.version[k], ops.seo[k])) rep.verifyFail.push("seo." + k);
  return rep;
};
return "applyOps2 installed";
