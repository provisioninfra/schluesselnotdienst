const fs = require("fs"); const path = require("path");
state.uploadMedia = async (filePath, opts = {}) => {
  const buf = fs.readFileSync(filePath); const name = opts.name || path.basename(filePath);
  const ct = opts.contentType || (name.endsWith(".png") ? "image/png" : name.endsWith(".svg") ? "image/svg+xml" : "image/jpeg");
  const b64 = buf.toString("base64");
  return await page.evaluate(async ({b64, name, ct, size, w, h, siteId}) => {
    const bin = atob(b64); const arr = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    const blob = new Blob([arr], {type: ct});
    const r1 = await fetch("https://api-eu.onepage.io/api/v1/media", {method: "POST", credentials: "include", headers: {"content-type": "application/json;charset=UTF-8"}, body: JSON.stringify({size, name, contentType: ct, height: h, width: w, preview: null, siteId, isAvatar: false})});
    const j1 = await r1.json(); if (!j1.media) return {error: "create failed", j1};
    const fd = new FormData(); for (const [k, v] of Object.entries(j1.s3.fields)) fd.append(k, v); fd.append("Content-Type", ct); fd.append("file", blob, name);
    const r2 = await fetch(j1.s3.url, {method: "POST", body: fd});
    const r3 = await fetch("https://api-eu.onepage.io/api/v1/media/" + j1.media.id + "?siteId=" + siteId, {method: "PATCH", credentials: "include", headers: {"content-type": "application/json;charset=UTF-8"}, body: JSON.stringify({isAvatar: false})});
    const j3 = await r3.json();
    return {s3status: r2.status, src: j3.src, status: j3.status, id: j3.id, meta: j3.meta};
  }, {b64, name, ct, size: buf.length, w: opts.width || 0, h: opts.height || 0, siteId: state.SITE});
};
return "uploadMedia installed";
