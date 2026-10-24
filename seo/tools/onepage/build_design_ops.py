#!/usr/bin/env python3
"""Design-Patches (Abschnitts-, Molekül- und Atom-Styles) für alle Seiten: dunkles Marineblau wie provision-infra.de.
Aufruf: python3 build_design_ops.py <pages_dir> <ops_out_dir> [slug ...]
Ausgabe-Items tragen ein Feld "target" (organism|molecule|atom)."""
import sys, os, json, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oplib import *  # noqa

PAGES_DIR, OUT = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3:]
os.makedirs(OUT, exist_ok=True)
LEGAL = set()  # Rechtsseiten ebenfalls dunkel (einheitlich)

def sec_patch(sec, key):
    st = sec.get("styles", {})
    val = {"styles": {"color_bg": key, "color_bg_type": "palette", "color_bg_key": key, "color_text_type": "auto"}}
    snap = {"styles": {k: (st.get(k) if k in st else None) for k in ("color_bg", "color_bg_type", "color_bg_key", "color_text_type")}}
    cur = {k: st.get(k) for k in val["styles"]}
    if cur == val["styles"]:
        return None
    return {"target": "organism", "organismId": sec["_id"], "value": val, "snapshot": snap, "note": f"section {sec.get('title')} -> {key}"}

def build(slug):
    page = json.load(open(os.path.join(PAGES_DIR, f"{slug}.json"), encoding="utf-8"))
    v = page["version"]; items = []
    for sec in v["sections"]:
        t = sec.get("title") or ""; st = sec.get("styles", {})
        if t == "Fußzeile":
            continue
        if sec.get("type") == "header":
            p = sec_patch(sec, "dark")
        elif slug in LEGAL:
            p = sec_patch(sec, "light")
        elif t == "Unsere Partner":
            p = sec_patch(sec, "light")
        elif st.get("background_type") == "media":
            p = None  # Hero mit Hintergrundbild (Startseite) und Bewertungen (Türöffnung) behalten
        else:
            p = sec_patch(sec, "dark")
        if p: items.append(p)
        # Moleküle / Atome
        for fr in (sec.get("layer") or {}).get("frames", []):
            for row in fr.get("rows", []):
                for mol in row.get("molecules", []):
                    ms = mol.get("styles", {})
                    if ms.get("color_bg_key") == "key1" and ms.get("style_type") == "solid":
                        items.append({"target": "molecule", "moleculeId": mol["_id"], "value": {"styles": {"color_bg_key": "key2"}}, "snapshot": {"styles": {"color_bg_key": "key1"}}, "note": f"molecule in {t} key1->key2"})
                    for a in mol.get("atoms", []):
                        ast = a.get("styles", {})
                        if a["type"] == "image" and t in ("layout",) and ast.get("radius_key") != "16":
                            items.append({"target": "atom", "atomId": a["_id"], "value": {"styles": {"radius_key": "16"}}, "snapshot": {"styles": {"radius_key": ast.get("radius_key") if "radius_key" in ast else None}}, "note": "hero image radius"})
                        if a["type"] == "link-group" and ast.get("first_link_color_bg_key") == "key1" and ast.get("first_link_color_bg_tone") not in (0, None):
                            items.append({"target": "atom", "atomId": a["_id"], "value": {"styles": {"first_link_color_bg_tone": 0, "first_link_color_text_key": "dark"}}, "snapshot": {"styles": {"first_link_color_bg_tone": ast.get("first_link_color_bg_tone"), "first_link_color_text_key": ast.get("first_link_color_text_key")}}, "note": "button yellow/dark text"})
    ops = {"slug": slug, "pageId": page["_id"], "seo": None, "patches": items}
    json.dump(ops, open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return items

slugs = ONLY or [f[:-5] for f in sorted(os.listdir(PAGES_DIR)) if f.endswith(".json")]
for s in slugs:
    it = build(s)
    print(f"{s:22s} design patches={len(it):2d}  " + ", ".join(sorted(set(i['note'].split(' ->')[0].split(' key1')[0] for i in it)))[:150])
