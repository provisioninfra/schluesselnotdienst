"""Alle Menü-Links auf Impressum, AGB und Datenschutz zeigen auf die Rechtsseiten von provision-infra.de.
Aufruf: python3 build_legal_links_ops.py <pages_dir> <ops_out_dir>"""
import json, os, sys, glob, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oplib import LEGAL_URLS
MAP = {"/impressum": LEGAL_URLS["impressum"], "/datenschutzerklarung": LEGAL_URLS["datenschutz"], "/agb": LEGAL_URLS["agb"],
       "/impressum/": LEGAL_URLS["impressum"], "/datenschutzerklarung/": LEGAL_URLS["datenschutz"], "/agb/": LEGAL_URLS["agb"]}
pages_dir, out_dir = sys.argv[1], sys.argv[2]; os.makedirs(out_dir, exist_ok=True)
n = 0
for f in sorted(glob.glob(os.path.join(pages_dir, "*.json"))):
    slug = os.path.basename(f)[:-5]; page = json.load(open(f, encoding="utf-8")); v = page["version"]; patches = []
    for s in v["sections"]:
        for fr in s["layer"]["frames"]:
            for r in fr["rows"]:
                for m in r["molecules"]:
                    for a in m["atoms"]:
                        if a["type"] != "menu-v2": continue
                        items = a["data"].get("items") or []; new = copy.deepcopy(items); changed = False
                        for it in new:
                            d = it.get("data") or {}
                            href = (d.get("link_href") or "").strip()
                            key = href if href in MAP else ("https://schluesselnotdienst-baumann.de" + "" if False else None)
                            if href.startswith("https://schluesselnotdienst-baumann.de"):
                                key = href.replace("https://schluesselnotdienst-baumann.de", "") or "/"
                            else:
                                key = href
                            if key in MAP:
                                d["link_href"] = MAP[key]; d["link_action_type"] = "link"; d["link_blank"] = False; changed = True
                        if changed:
                            patches.append({"atomId": a["_id"], "value": {"data": {"items": new}}, "snapshot": {"data": {"items": items}}, "note": f"legal links in {s.get('title')}"})
    if patches:
        json.dump({"slug": slug, "pageId": v["pageId"], "patches": patches}, open(os.path.join(out_dir, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1); n += 1
        print(f"{slug:24} {[p['note'] for p in patches]}")
print("files:", n)
