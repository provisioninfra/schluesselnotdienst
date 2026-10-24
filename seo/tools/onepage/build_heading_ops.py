"""Heading-Hierarchie bereinigen (technisches SEO): h4/h5-Zwischenüberschriften der Ortsseiten -> h3,
Startseite: Abschnittstitel h2, Kartentitel h3. Aufruf: python3 build_heading_ops.py <pages_dir> <ops_out_dir>"""
import json, os, sys, glob, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oplib import set_text
pages_dir, out_dir = sys.argv[1], sys.argv[2]; os.makedirs(out_dir, exist_ok=True)
orte = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "orte.json"), encoding="utf-8"))
towns = {o["slug"] for o in (orte if isinstance(orte, list) else orte["orte"])}
HOME_MAP = {"Wir öffnen Deine Tür zerstörungsfrei": "h2", "Rund um die Uhr erreichbar": "h3", "Nie wieder ausgesperrt": "h3", "Bezahlen, wie es Dir passt": "h3",
            "Das bekommst Du bei uns": "h2", "Fester Preis im Voraus": "h3", "Zahlung nach Deinen Wünschen": "h3", "Leistungen": "h2", "Unser Einsatzgebiet": "h2",
            "So erreichst Du uns": "h2", "Öffnungszeiten": "h3", "Unsere Partner": "h2"}
def retype(atom, new_type):
    blocks = copy.deepcopy(atom["data"]["text"]["blocks"])
    changed = False
    for b in blocks:
        if b["type"].startswith("h") and b["text"].strip() and b["type"] != new_type:
            b["type"] = new_type; changed = True
    return (set_text(atom, blocks) if changed else None)
n = 0
for f in sorted(glob.glob(os.path.join(pages_dir, "*.json"))):
    slug = os.path.basename(f)[:-5]
    if slug not in towns and slug != "startseite": continue
    page = json.load(open(f, encoding="utf-8")); v = page["version"]; patches = []
    for s in v["sections"]:
        for fr in s["layer"]["frames"]:
            for r in fr["rows"]:
                for m in r["molecules"]:
                    for a in m["atoms"]:
                        if a["type"] != "header": continue
                        blocks = a["data"]["text"]["blocks"]; first = next((b for b in blocks if b["text"].strip()), None)
                        if not first or not first["type"].startswith("h"): continue
                        txt = first["text"].strip()
                        if slug == "startseite":
                            want = HOME_MAP.get(txt)
                        else:
                            want = "h3" if first["type"] in ("h4", "h5", "h6") else None
                        if want and first["type"] != want:
                            res = retype(a, want)
                            if res:
                                val, snap = res
                                patches.append({"atomId": a["_id"], "value": val, "snapshot": snap, "note": f"heading {first['type']}->{want}: {txt[:30]}"})
    if patches:
        json.dump({"slug": slug, "pageId": v["pageId"], "patches": patches}, open(os.path.join(out_dir, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        n += 1; print(f"{slug:16} {[p['note'] for p in patches]}")
print("files:", n)
