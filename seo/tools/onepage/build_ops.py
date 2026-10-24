#!/usr/bin/env python3
"""Baut aus den OnePage-Seiten-Dumps (pagesV2.fetchPage) und orte.json die Patch-Operationen
für die Ortsseiten: Texte (Hero, Footer), HTML-Block (Preise, Ablauf, FAQ, Nachbarorte, Einsatzgebiet),
Footer-/Header-Links sowie die SEO-Felder (Titel, Description, Keywords, Page-Code JSON-LD).

Aufruf: python3 build_ops.py <pages_dir> <ops_out_dir> [slug ...]
"""
import sys, os, json, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oplib import *  # noqa

PAGES_DIR, OUT = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3:]
os.makedirs(OUT, exist_ok=True)

def build_city(slug):
    o = G.ORTE[slug]
    k = G.kurz(o)
    page = json.load(open(os.path.join(PAGES_DIR, f"{slug}.json"), encoding="utf-8"))
    v = page["version"]
    S = sections_by_title(v)
    patches = []
    def add(atom, value, snapshot, note):
        patches.append({"atomId": atom["_id"], "value": value, "snapshot": snapshot, "note": note})

    # Hero
    hero = S["layout"][0]
    img = find_atoms(hero, "image")[0]
    add(img, {"data": {"alt": f"Schlüsseldienst öffnet eine Haustür in {k} – {BRAND}"}}, {"data": {"alt": img["data"].get("alt", "")}}, "hero alt")
    heads = find_atoms(hero, "header")
    h1, h2 = heads[0], heads[1]
    val, snap = single_text(h1, f"Schlüsseldienst {k}: Notdienst rund um die Uhr zum Festpreis", "h1"); add(h1, val, snap, "hero h1")
    val, snap = single_text(h2, f"{BRAND} für {k}", "h2"); add(h2, val, snap, "hero h2")
    pt = find_atoms(hero, "plain-text")[0]
    text, bold = hero_plain_text(o)
    val, snap = single_text(pt, text, None, bold); add(pt, val, snap, "hero text")

    # Vorteile-Karten
    for a, val, snap, note in vorteile_patches(S["Vorteile"][0], k, o["eta"]):
        cur = a["data"]["text"]["blocks"][0]["text"]
        if cur != val["data"]["text"]["blocks"][0]["text"]:
            add(a, val, snap, note)

    # Preisplan header: keep; Einsatzgebiet header + html
    eg = S["Einsatzgebiet"][0]
    egh = find_atoms(eg, "header")[0]
    val, snap = single_text(egh, f"Alles Wichtige für {k}: Preise, Ablauf, Antworten und Einsatzgebiet"); add(egh, val, snap, "einsatzgebiet header")
    egc = find_atoms(eg, "custom-code")[0]
    add(egc, {"data": {"html": local_html(o)}}, {"data": {"html": egc["data"]["html"]}}, "einsatzgebiet html")

    # Bewertungen: dunkle Variante, Duplikate aria-hidden
    bw = S["Bewertungen"][0]
    bwc = find_atoms(bw, "custom-code")[0]
    newh = reviews_dark(bwc["data"]["html"])
    if newh != bwc["data"]["html"]:
        add(bwc, {"data": {"html": newh}}, {"data": {"html": bwc["data"]["html"]}}, "bewertungen html")

    # Footer
    fz = S["Fußzeile"][0]
    fpt = find_atoms(fz, "plain-text")[0]
    val, snap = single_text(fpt, "Copyright © 2026 ProVision Infra GmbH – Schlüsselnotdienst – Alle Rechte vorbehalten."); add(fpt, val, snap, "footer text")
    fm = find_atoms(fz, "menu-v2")[0]
    val, snap = footer_menu_value(fm); add(fm, val, snap, "footer menu")

    # Header menu fixes
    for m, val, snap in header_menu_fix(S["Header"][0]):
        add(m, val, snap, "header menu")

    # Preisplan: neue Preiskarten (dunkles Design, Preis je Ort)
    pp = S["Preisplan"][0]
    ppc = find_atoms(pp, "custom-code")[0]
    newp = price_cards(o["preis_tueroeffnung"], True)
    if newp != ppc["data"]["html"]:
        add(ppc, {"data": {"html": newp}}, {"data": {"html": ppc["data"]["html"]}}, "preisplan html")
    # Preisplan header text "Leistungen für X"
    pp = S["Preisplan"][0]
    pph = find_atoms(pp, "header")[0]
    cur = pph["data"]["text"]["blocks"][0]["text"]
    if cur.strip() != f"Leistungen für {k}":
        val, snap = single_text(pph, f"Leistungen für {k}"); add(pph, val, snap, "preisplan header")

    seo = {"title": o["name"], "seoTitle": G.title_for(o), "seoDescription": G.desc_for(o),
           "seoKeywords": f"Schlüsseldienst {k}, Schlüsselnotdienst {k}, Türöffnung {k}, Schlüsseldienst {k} 24h, Aufsperrdienst {k}, Schlüsseldienst {k} Kosten, Autoöffnung {k}",
           "codeHead": G.jsonld(o), "noindex": False}
    ops = {"slug": slug, "pageId": page["_id"], "seo": seo, "patches": patches}
    json.dump(ops, open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return ops

slugs = ONLY or [s for s in G.ORTE if os.path.exists(os.path.join(PAGES_DIR, f"{s}.json"))]
for s in slugs:
    ops = build_city(s)
    print(f"{s:16s} patches={len(ops['patches']):2d} title={ops['seo']['seoTitle']!r} ({len(ops['seo']['seoTitle'])}) desc_len={len(ops['seo']['seoDescription'])} html_len={len([p for p in ops['patches'] if p['note']=='einsatzgebiet html'][0]['value']['data']['html'])}")
