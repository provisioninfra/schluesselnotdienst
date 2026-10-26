"""Copyright-Zeile im Footer ohne Gedankenstriche. Aufruf: python3 build_footer_text_ops.py <pages_dir> <ops_out_dir>"""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oplib import single_text
NEW = "© 2026 ProVision Infra GmbH, Schlüsselnotdienst. Alle Rechte vorbehalten."
pages_dir, out_dir = sys.argv[1], sys.argv[2]; os.makedirs(out_dir, exist_ok=True); n = 0
for f in sorted(glob.glob(os.path.join(pages_dir, "*.json"))):
    slug = os.path.basename(f)[:-5]; page = json.load(open(f, encoding="utf-8")); v = page["version"]; patches = []
    for s in v["sections"]:
        for fr in s["layer"]["frames"]:
            for r in fr["rows"]:
                for m in r["molecules"]:
                    for a in m["atoms"]:
                        if a["type"] != "plain-text": continue
                        txt = " ".join(b["text"] for b in a["data"]["text"]["blocks"])
                        if "Alle Rechte vorbehalten" in txt and txt.strip() != NEW:
                            val, snap = single_text(a, NEW); patches.append({"atomId": a["_id"], "value": val, "snapshot": snap, "note": "copyright"})
    if patches:
        json.dump({"slug": slug, "pageId": v["pageId"], "patches": patches}, open(os.path.join(out_dir, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1); n += 1
print("files:", n)
