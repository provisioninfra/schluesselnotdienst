#!/usr/bin/env python3
"""Gemeinsame Helfer für die OnePage-Patch-Builder (Draft.js-Blöcke, Seitenstruktur, HTML-Bausteine)."""
import sys, os, json, copy, re, html, random, string
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import generate_pages as G
B = G.B
TEL_E164 = B["telefon_e164"]
TEL = B["telefon_anzeige"]
BRAND = "ProVision Infra Schlüsselnotdienst"
ALPH = string.ascii_letters + string.digits + "_-"

def nid(n=21):
    return "".join(random.choice(ALPH) for _ in range(n))

def esc(s):
    return html.escape(s, quote=False)

# ---------- Draft.js helpers ----------
def block(text, btype, data=None, key=None, bold_ranges=None):
    return {"key": key or nid(5).lower(), "text": text, "type": btype, "depth": 0,
            "inlineStyleRanges": [{"offset": a, "length": b, "style": "BOLD"} for a, b in (bold_ranges or [])],
            "entityRanges": [], "data": data or {}}

def set_text(atom, new_blocks):
    """returns (value, snapshot) for patching atom.data.text"""
    old = copy.deepcopy(atom["data"]["text"])
    new = {"blocks": new_blocks, "entityMap": {}}
    return {"data": {"text": new}}, {"data": {"text": old}}

def single_text(atom, text, btype=None, bold_ranges=None):
    ob = atom["data"]["text"]["blocks"][0]
    nb = block(text, btype or ob["type"], data=copy.deepcopy(ob.get("data") or {}), key=ob.get("key"), bold_ranges=bold_ranges)
    return set_text(atom, [nb])

# ---------- page structure access ----------
def atoms(section):
    for fr in (section.get("layer") or {}).get("frames", []):
        for row in fr.get("rows", []):
            for mol in row.get("molecules", []):
                for a in mol.get("atoms", []):
                    yield mol, a

def sections_by_title(version):
    d = {}
    for s in version["sections"]:
        d.setdefault(s.get("title"), []).append(s)
    return d

def find_atoms(section, atype):
    return [a for _, a in atoms(section) if a.get("type") == atype]

# ---------- HTML block ----------
CSS = """
<style>
.pvi-local{font-family:inherit;color:#1d2a3a;line-height:1.6;background:#f5f9ff;padding:44px 28px;border-radius:18px;box-sizing:border-box;text-align:left}
.pvi-local h3,.pvi-local .pvi-cta,.pvi-local .pvi-small{text-align:center}
.pvi-local .pvi-card h3{text-align:left}
.pvi-local *{box-sizing:border-box}
.pvi-local .pvi-wrap{max-width:1100px;margin:0 auto;padding:0}
@media (max-width:600px){.pvi-local{padding:28px 16px}}
.pvi-local p{margin:0 0 16px;font-size:1.05rem}
.pvi-local h3{color:#0056A3;font-size:1.45rem;line-height:1.3;margin:36px 0 14px;font-weight:700}
.pvi-local .pvi-grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin:8px 0 8px}
.pvi-local .pvi-card{background:#fff;border:1px solid #dde7f3;border-top:5px solid #115697;border-radius:14px;padding:22px 24px;box-shadow:0 4px 14px rgba(0,0,0,.05)}
.pvi-local .pvi-card h3{margin-top:0;font-size:1.25rem}
.pvi-local ol,.pvi-local ul{padding-left:22px;margin:0 0 12px}
.pvi-local li{margin:6px 0}
.pvi-local .pvi-services{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.pvi-local .pvi-services li{background:#f5f9ff;border-radius:12px;padding:14px 16px;margin:0}
.pvi-local details{background:#fff;border:1px solid #dde7f3;border-radius:12px;padding:0 18px;margin:10px 0}
.pvi-local summary{cursor:pointer;font-weight:700;color:#0d3e75;padding:14px 0;list-style:none;position:relative;padding-right:28px}
.pvi-local summary::-webkit-details-marker{display:none}
.pvi-local summary::after{content:"+";position:absolute;right:0;top:12px;font-size:1.3rem;color:#0056A3}
.pvi-local details[open] summary::after{content:"–"}
.pvi-local details p{padding-bottom:14px;margin:0}
.pvi-local .pvi-near{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:10px}
.pvi-local .pvi-near a{display:inline-block;background:#0056A3;color:#fff;text-decoration:none;padding:10px 16px;border-radius:999px;font-weight:600}
.pvi-local .pvi-near a:hover{background:#F7C41B;color:#1d2a3a}
.pvi-local .pvi-orte{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 30px}
.pvi-local .pvi-orte a,.pvi-local .pvi-orte span{display:flex;align-items:center;justify-content:center;background:#e6f0fa;color:#0056A3;padding:14px 10px;border-radius:12px;font-weight:600;text-align:center;text-decoration:none;box-shadow:0 2px 6px rgba(0,0,0,.05)}
.pvi-local .pvi-orte a:hover{background:#0056A3;color:#fff}
.pvi-local .pvi-orte span{background:#0056A3;color:#fff}
.pvi-local .pvi-map{position:relative;width:100%;padding-bottom:37.38%;height:0;overflow:hidden;border-radius:14px}
.pvi-local .pvi-map iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
.pvi-local .pvi-cta{text-align:center;margin:28px 0 0}
.pvi-local .pvi-cta a{display:inline-block;background:#115697;color:#fff;text-decoration:none;font-weight:700;padding:16px 30px;border-radius:999px;font-size:1.1rem}
.pvi-local .pvi-cta a:hover{background:#F7C41B;color:#1d2a3a}
.pvi-local .pvi-small{font-size:.95rem;color:#4a5968}
@media (max-width:600px){.pvi-local .pvi-map{padding-bottom:70%}}
</style>
"""
MAP_IFRAME = '<div class="pvi-map"><iframe src="https://www.google.com/maps/d/u/0/embed?mid=1jHbiTcWVwjbPiy-JEHT8qWWffvY4nCk&ehbc=2E312F&noprof=1" title="Einsatzgebiet des ProVision Infra Schlüsselnotdienstes" loading="lazy" allowfullscreen=""></iframe></div>'

ORTE_ORDER = ["bad-bevensen", "uelzen", "lueneburg", "bienenbuettel", "altenmedingen", "barum", "himbergen", "ebstorf", "wriedel", "melbeck", "adendorf", "barendorf", "dahlenburg", "amelinghausen", "bleckede", "rosche", "suderburg", "wieren", "bad-bodenteich", "zernien", "dannenberg", "hitzacker", "luechow", "munster", "fassberg", "eschede", "celle", "bavendorf"]

def orte_grid(current_slug):
    items = []
    for s in ORTE_ORDER:
        o = G.ORTE[s]
        name = o["name"]
        if s == current_slug:
            items.append(f'<li><span aria-current="page">{esc(name)}</span></li>')
        else:
            items.append(f'<li><a href="/{s}" title="Schlüsseldienst {esc(G.kurz(o))}">{esc(name)}</a></li>')
    return '<ul class="pvi-orte">' + "".join(items) + "</ul>"

def local_html(o):
    k = G.kurz(o)
    ablauf = "".join(f"<li>{esc(re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', s)).replace('&lt;strong&gt;','<strong>').replace('&lt;/strong&gt;','</strong>')}</li>" for s in G.ablauf(o))
    leist = "".join(f"<li><strong>{esc(n)}</strong><br>{esc(t)}</li>" for n, t in G.leistungen(o))
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in G.faq(o))
    near = "".join(f'<li><a href="{l.replace(G.DOMAIN, "")}">Schlüsseldienst {esc(n)}</a></li>' for n, l in G.nachbarn_links(o))
    near += '<li><a href="/turoffnung">Türöffnung &amp; Preise</a></li>'
    parts = [
        f'<section class="pvi-local" id="einsatzgebiet">', CSS, '<div class="pvi-wrap">',
        f'<p>{esc(G.intro(o))}</p>',
        f'<p>{esc(G.lokal_abschnitt(o))}</p>',
        '<div class="pvi-grid2">',
        f'<div class="pvi-card"><h3>Was kostet der Schlüsseldienst in {esc(k)}?</h3><p>{esc(G.preise(o))}</p></div>',
        f'<div class="pvi-card"><h3>So läuft Deine Türöffnung in {esc(k)} ab</h3><ol>{ablauf}</ol></div>',
        '</div>',
        f'<h3>Unsere Leistungen in {esc(k)}</h3><ul class="pvi-services">{leist}</ul>',
        f'<h3>Häufige Fragen zum Schlüsseldienst in {esc(k)}</h3><div class="pvi-faq">{faq}</div>',
        f'<h3>Schlüsseldienst in der Nähe von {esc(k)}</h3><ul class="pvi-near">{near}</ul>',
        '<h3>Unser Einsatzgebiet</h3>',
        f'<p>Als mobiler <strong>Schlüsselnotdienst aus Bad Bevensen</strong> ({esc(B["strasse"])}) sind wir täglich im Landkreis Uelzen, im Landkreis Lüneburg, im Landkreis Lüchow-Dannenberg sowie bis Munster, Faßberg und Celle im Einsatz – schnell, zuverlässig und in ca. 80 km Umkreis. Wähle Deinen Ort:</p>',
        orte_grid(o["slug"]),
        MAP_IFRAME,
        f'<p class="pvi-cta"><a href="tel:{TEL_E164}">☎ Jetzt anrufen: {TEL}</a></p>',
        f'<p class="pvi-small" style="text-align:center;margin-top:14px">{esc(BRAND)} · {esc(B["strasse"])}, {B["plz"]} {esc(B["ort"])} · 24 Stunden, 7 Tage die Woche</p>',
        '</div></section>'
    ]
    return "\n".join(parts)

# ---------- per-page ops ----------
def hero_plain_text(o):
    k = G.kurz(o)
    l1 = f"Türöffnung in {k} & Umgebung"
    l2 = f"Festpreis {o['preis_tueroeffnung']} € inkl. Anfahrt · in ca. {o['eta']} Min. vor Ort"
    l3 = "fair • transparent • zerstörungsfrei"
    text = f"{l1}\n{l2}\n{l3}"
    return text, [(len(l1) + 1 + len(l2) + 1, len(l3))]

def footer_menu_value(menu_atom):
    items = copy.deepcopy(menu_atom["data"]["items"])
    old = copy.deepcopy(menu_atom["data"]["items"])
    mapping = {"impressum": "/impressum", "datenschutz": "/datenschutzerklarung", "agb": "/agb"}
    kept = []
    for it in items:
        t = (it["data"].get("link_text") or "").lower()
        target = next((v for key, v in mapping.items() if key in t), None)
        if target:
            it["data"]["link_action_type"] = "link"; it["data"]["link_href"] = target; it["data"]["link_blank"] = False
            kept.append(it)
        # drop dead links (SIMONSVOSS_Technologies, EVVA...) silently
    tmpl = copy.deepcopy(old[0])
    def mk(text, href):
        n = copy.deepcopy(tmpl); n["_id"] = nid(); n["data"]["link_text"] = text; n["data"]["link_href"] = href
        n["data"]["link_action_type"] = "link"; n["data"]["link_blank"] = False; n["data"]["link_subtitle"] = ""
        return n
    have = {(it["data"].get("link_text") or "").strip().lower() for it in kept}
    std = [("Startseite", "/"), ("Türöffnung & Preise", "/turoffnung"), ("Einsatzgebiete", "/#einsatzgebiet")]
    new_items = [mk(t, h) for t, h in std if t.lower() not in have] + kept
    return {"data": {"items": new_items}}, {"data": {"items": old}}

def header_menu_fix(header_section):
    """Geschäftskunden (404) -> Einsatzgebiete bzw. Türöffnung & Preise (wenn Einsatzgebiete schon vorhanden); Leistungen -> Türöffnung & Preise.
    returns list of (atom, value, snapshot)"""
    out = []
    menus = find_atoms(header_section, "menu-v2")
    texts = [((it["data"].get("link_text") or "").strip().lower()) for m in menus for it in m["data"]["items"]]
    has_einsatz = texts.count("einsatzgebiete")
    has_tuer = "türöffnung & preise" in texts
    for m in menus:
        items = copy.deepcopy(m["data"]["items"]); old = copy.deepcopy(m["data"]["items"]); changed = False
        for it in items:
            t = (it["data"].get("link_text") or "").strip().lower(); href = it["data"].get("link_href") or ""
            is_dead = "geschaftskunden" in href or "geschäftskunden" in t
            is_my_dup = (t == "einsatzgebiete" and href == "/#einsatzgebiet" and has_einsatz > 1)
            if is_dead or is_my_dup:
                if (has_einsatz == 0 and not is_my_dup):
                    it["data"].update({"link_text": "Einsatzgebiete", "link_href": "/#einsatzgebiet", "link_action_type": "link", "link_megamenu": ""}); has_einsatz += 1
                elif not has_tuer:
                    it["data"].update({"link_text": "Türöffnung & Preise", "link_href": "/turoffnung", "link_action_type": "link", "link_megamenu": ""}); has_tuer = True
                else:
                    it["data"].update({"link_text": "Bad Bevensen", "link_href": "/bad-bevensen", "link_action_type": "link", "link_megamenu": ""})
                changed = True
            elif t == "leistungen" and it["data"].get("link_action_type") == "link" and href in ("/", ""):
                it["data"].update({"link_text": "Türöffnung & Preise", "link_href": "/turoffnung", "link_action_type": "link"}); changed = True
        if changed:
            out.append((m, {"data": {"items": items}}, {"data": {"items": old}}))
    return out
