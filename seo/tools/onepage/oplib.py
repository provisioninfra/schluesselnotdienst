#!/usr/bin/env python3
"""Gemeinsame Helfer für die OnePage-Patch-Builder (Draft.js-Blöcke, Seitenstruktur, HTML-Bausteine)."""
import sys, os, json, copy, re, html, random, string
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import generate_pages as G
B = G.B
TEL_E164 = B["telefon_e164"]
TEL = B["telefon_anzeige"]
kurz = G.kurz
BRAND = "ProVision Infra Schlüsselnotdienst"
# Rechtstexte liegen zentral bei der ProVision Infra GmbH
LEGAL_URLS = {"impressum": "https://provision-infra.de/impressum/", "datenschutz": "https://provision-infra.de/datenschutz/", "agb": "https://provision-infra.de/agb/"}
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
.pvi-local{font-family:inherit;color:#E8EDF7;line-height:1.65;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.12);padding:44px 32px;border-radius:22px;box-sizing:border-box;text-align:left}
.pvi-local *{box-sizing:border-box}
.pvi-local .pvi-wrap{max-width:1100px;margin:0 auto;padding:0}
.pvi-local p{margin:0 0 16px;font-size:1.04rem;color:#D5DDEC}
.pvi-local h3{color:#fff;font-size:1.45rem;line-height:1.3;margin:40px 0 16px;font-weight:600;text-align:center}
.pvi-local h3::after{content:"";display:block;width:44px;height:3px;background:#FBC91B;border-radius:2px;margin:12px auto 0}
.pvi-local .pvi-grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin:8px 0 8px}
.pvi-local .pvi-card{background:#071A4A;border:1px solid rgba(255,255,255,.12);border-top:3px solid #FBC91B;border-radius:16px;padding:24px 26px;box-shadow:0 12px 30px rgba(0,0,0,.25)}
.pvi-local .pvi-card h3{margin-top:0;font-size:1.2rem;text-align:left}
.pvi-local .pvi-card h3::after{margin-left:0}
.pvi-local ol,.pvi-local ul{padding-left:22px;margin:0 0 12px}
.pvi-local li{margin:7px 0;color:#D5DDEC}
.pvi-local li strong,.pvi-local p strong{color:#fff}
.pvi-local .pvi-services{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px}
.pvi-local .pvi-services li{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:16px 18px;margin:0}
.pvi-local details{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:0 18px;margin:10px 0;transition:border-color .25s ease}
.pvi-local details[open]{border-color:rgba(251,201,27,.55)}
.pvi-local summary{cursor:pointer;font-weight:600;color:#fff;padding:15px 30px 15px 0;list-style:none;position:relative}
.pvi-local summary::-webkit-details-marker{display:none}
.pvi-local summary::after{content:"+";position:absolute;right:0;top:11px;font-size:1.4rem;color:#FBC91B;transition:transform .25s ease}
.pvi-local details[open] summary::after{content:"+";transform:rotate(45deg)}
.pvi-local details p{padding-bottom:16px;margin:0}
.pvi-local .pvi-near{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.pvi-local .pvi-near a{display:inline-block;background:#FBC91B;color:#0B1A3A;text-decoration:none;padding:10px 18px;border-radius:999px;font-weight:600;transition:transform .2s ease,background-color .2s ease}
.pvi-local .pvi-near a:hover{background:#fff;transform:translateY(-2px)}
.pvi-local .pvi-orte{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 30px}
.pvi-local .pvi-orte a,.pvi-local .pvi-orte span{display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#fff;padding:14px 10px;border-radius:12px;font-weight:600;text-align:center;text-decoration:none;transition:background-color .2s ease,color .2s ease,border-color .2s ease}
.pvi-local .pvi-orte a:hover{background:#FBC91B;color:#0B1A3A;border-color:#FBC91B}
.pvi-local .pvi-orte span{background:#263E96;border-color:#FBC91B}
.pvi-local .pvi-map{position:relative;width:100%;padding-bottom:37.38%;height:0;overflow:hidden;border-radius:16px;border:1px solid rgba(255,255,255,.12)}
.pvi-local .pvi-map iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
.pvi-local .pvi-cta{text-align:center;margin:30px 0 0}
.pvi-local .pvi-cta a{display:inline-block;background:#FBC91B;color:#0B1A3A;text-decoration:none;font-weight:700;padding:16px 32px;border-radius:999px;font-size:1.08rem;box-shadow:0 0 0 1px rgba(251,201,27,.35),0 12px 30px rgba(251,201,27,.2);transition:transform .2s ease,box-shadow .2s ease}
.pvi-local .pvi-cta a:hover{transform:translateY(-2px);box-shadow:0 0 0 1px rgba(251,201,27,.5),0 16px 36px rgba(251,201,27,.3)}
.pvi-local .pvi-small{font-size:.95rem;color:#B7C2D9;text-align:center}
.pvi-local table{color:#E8EDF7}
@media (max-width:700px){.pvi-local{padding:28px 16px}.pvi-local .pvi-map{padding-bottom:70%}.pvi-local h3{font-size:1.25rem}}
</style>
"""

PRICE_CSS = """
<style>
.pvi-prices{display:flex;gap:20px;overflow-x:auto;padding:8px 4px 18px;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch}
.pvi-prices::-webkit-scrollbar{height:8px}.pvi-prices::-webkit-scrollbar-thumb{background:rgba(255,255,255,.18);border-radius:8px}
.pvi-price{flex:0 0 330px;scroll-snap-align:start;background:#071A4A;border:1px solid rgba(255,255,255,.12);border-radius:18px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 14px 34px rgba(0,0,0,.3);transition:transform .25s ease,border-color .25s ease;text-align:left}
.pvi-price:hover{transform:translateY(-4px);border-color:rgba(251,201,27,.55)}
.pvi-price__head{background:#263E96;color:#fff;padding:18px 20px;font-weight:600;font-size:1.15rem;text-align:center}
.pvi-price__head small{display:block;font-weight:400;font-size:.85rem;opacity:.85;margin-top:4px}
.pvi-price__body{padding:22px 22px 8px;flex:1}
.pvi-price__amount{font-size:2.3rem;font-weight:700;color:#FBC91B;text-align:center;margin:0 0 6px;line-height:1.1}
.pvi-price__note{text-align:center;color:#B7C2D9;font-size:.9rem;margin:0 0 14px}
.pvi-price ul{list-style:none;padding:0;margin:0}
.pvi-price li{position:relative;padding:9px 0 9px 26px;color:#D5DDEC;border-bottom:1px solid rgba(255,255,255,.08);font-size:.98rem}
.pvi-price li:last-child{border-bottom:0}
.pvi-price li::before{content:"✓";position:absolute;left:0;top:8px;color:#FBC91B;font-weight:700}
.pvi-price__foot{display:flex;gap:10px;padding:14px 22px 22px;justify-content:center;flex-wrap:wrap}
.pvi-price__foot a{flex:1;min-width:120px;text-align:center;text-decoration:none;padding:12px 16px;border-radius:999px;font-weight:600;font-size:.95rem;transition:transform .2s ease,background-color .2s ease,color .2s ease}
.pvi-price__foot .pvi-call{background:#FBC91B;color:#0B1A3A}
.pvi-price__foot .pvi-call:hover{background:#fff;transform:translateY(-2px)}
.pvi-price__foot .pvi-more{border:1px solid rgba(255,255,255,.35);color:#fff}
.pvi-price__foot .pvi-more:hover{border-color:#FBC91B;color:#FBC91B}
@media (max-width:600px){.pvi-price{flex-basis:86%}}
</style>
"""

def price_cards(preis, full=True):
    """Preiskarten im dunklen Design. preis: Festpreis Türöffnung (str). full: 6 Karten (Ortsseiten) oder 3 (Startseite)."""
    std = [f"Bar, Karte oder PayPal", "Montag bis Freitag, 8 bis 18 Uhr", "Nachts, am Wochenende und an Feiertagen + 54 €"]
    cards = [
        ("Türöffnung", "Festpreis inkl. MwSt. und Anfahrt", f"{preis} €", None, ["Zugefallene und abgeschlossene Türen"] + std, "/turoffnung"),
        ("Fensteröffnung", "Festpreis inkl. MwSt. und Anfahrt", f"{preis} €", None, ["Gekippte oder zugefallene Fenster"] + std, "/turoffnung"),
        ("Fahrzeugöffnung", "Festpreis inkl. MwSt. und Anfahrt", f"{preis} €", None, ["Abgeschlossene Pkw und Transporter"] + std, "/turoffnung"),
    ]
    if full:
        cards += [
            ("Profilzylinder", "Austausch und Reparatur", "ab 60 €", "zzgl. Material", ["Einbau direkt vor Ort", "Hochwertige Zylinder im Fahrzeug vorrätig", "Bar, Karte oder auf Rechnung"], "https://provision-infra.de/"),
            ("Schließanlagen", "Angebot für Schließsysteme", "50 €", "entfällt bei Auftragserteilung", ["Bedarfsanalyse und Planung", "Materialbeschaffung und Montage", "Zahlung auf Rechnung"], "https://provision-infra.de/"),
            ("Sicherheitsberatung", "Einbruchschutz für Haus und Wohnung", "auf Anfrage", None, ["Beratung bei Dir vor Ort", "Schwachstellen an Türen und Fenstern", "Angebot für Beschläge kostenlos"], "https://provision-infra.de/"),
        ]
    out = [PRICE_CSS, '<div class="pvi-prices">']
    for title, sub, amount, note, feats, more in cards:
        ext = more.startswith("http")
        out.append('<div class="pvi-price">'
                   f'<div class="pvi-price__head">{esc(title)}<small>{esc(sub)}</small></div>'
                   f'<div class="pvi-price__body"><p class="pvi-price__amount">{esc(amount)}</p>'
                   + (f'<p class="pvi-price__note">{esc(note)}</p>' if note else '')
                   + '<ul>' + "".join(f'<li>{esc(f)}</li>' for f in feats) + '</ul></div>'
                   f'<div class="pvi-price__foot"><a class="pvi-call" href="tel:{TEL_E164}">Anrufen</a>'
                   f'<a class="pvi-more" href="{more}"' + (' target="_blank" rel="noopener"' if ext else '') + '>Mehr erfahren</a></div></div>')
    out.append('</div>')
    return "\n".join(out)

REVIEWS_CSS = """
<style>
.reviews-container{width:100%;overflow:hidden;padding:30px 0 10px;background:transparent}
.reviews-slider{display:flex;width:max-content;animation:scroll 55s linear infinite}
.reviews-container:hover .reviews-slider{animation-play-state:paused}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.review-card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:24px;width:300px;margin:0 12px;flex-shrink:0;display:flex;flex-direction:column;justify-content:space-between;text-align:left}
.stars{color:#FBC91B;margin-bottom:10px;font-size:18px;letter-spacing:2px}
.text{font-size:14.5px;color:#D5DDEC;line-height:1.55;margin:0}
.author{font-weight:600;margin-top:14px;color:#fff;font-size:13px;border-top:1px solid rgba(255,255,255,.1);padding-top:10px}
@media (prefers-reduced-motion:reduce){.reviews-slider{animation:none;flex-wrap:wrap;width:auto;justify-content:center}.review-card[aria-hidden=true]{display:none}}
</style>
"""

def reviews_dark(html_old):
    """Bewertungs-Marquee behalten, CSS gegen dunkle Variante tauschen, Duplikate aria-hidden."""
    import re as _re
    body = _re.sub(r"<style>.*?</style>", "", html_old, flags=_re.S).strip()
    parts = body.split('<div class="review-card"')
    if len(parts) == 13:
        body = parts[0] + "".join(('<div class="review-card"' + (' aria-hidden="true"' if i > 6 and 'aria-hidden' not in p[:30] else '') + p) for i, p in enumerate(parts[1:], 1))
    return body + "\n" + REVIEWS_CSS

ACCENT_HTML = '<div class="accent-line"></div>\n<style>.accent-line{width:50px;height:3px;background-color:#FBC91B!important;margin:15px auto;border-radius:2px}</style>'

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
        f'<p>Als mobiler <strong>Schlüsselnotdienst aus Bad Bevensen</strong> ({esc(B["strasse"])}) sind wir täglich im Landkreis Uelzen, im Landkreis Lüneburg, im Landkreis Lüchow-Dannenberg sowie bis Munster, Faßberg und Celle im Einsatz. Der Umkreis liegt bei etwa 80 km. Wähle Deinen Ort:</p>',
        orte_grid(o["slug"]),
        MAP_IFRAME,
        f'<p class="pvi-cta"><a href="tel:{TEL_E164}">☎ Jetzt anrufen: {TEL}</a></p>',
        f'<p class="pvi-small" style="text-align:center;margin-top:14px">{esc(BRAND)} · {esc(B["strasse"])}, {B["plz"]} {esc(B["ort"])} · 24 Stunden, 7 Tage die Woche</p>',
        '</div></section>'
    ]
    return "\n".join(parts)

# ---------- per-page ops ----------
def hero_plain_text(o):
    k = kurz(o)
    l1 = f"Türöffnung in {k} und Umgebung"
    l2 = f"Festpreis {o['preis_tueroeffnung']} € inkl. Anfahrt, in etwa {o['eta']} Minuten bei Dir"
    l3 = "ohne Schaden an Tür und Schloss, zum vorher genannten Preis"
    text = f"{l1}\n{l2}\n{l3}"
    return text, [(len(l1) + 1 + len(l2) + 1, len(l3))]


VORTEILE_TEXTE = [
    ("Rund um die Uhr erreichbar", "Tag und Nacht, auch an Feiertagen.\nFestpreis am Telefon, bevor wir losfahren.\nIn {k} meist nach etwa {eta} Minuten vor Ort."),
    ("Feste Preise ohne Überraschungen", "Anfahrt und Mehrwertsteuer sind im Preis enthalten.\nMaterial wie ein neuer Zylinder berechnen wir nur nach Absprache."),
    ("Bezahlen, wie es Dir passt", "Bar, EC- oder Kreditkarte, PayPal.\nGeschäftskunden auf Wunsch per Rechnung.\nEine Quittung oder Rechnung gibt es immer."),
]


def vorteile_patches(section, k, eta):
    """Drei Vorteils-Karten (Header + Text) neu texten. Rückgabe: [(atom, value, snapshot, note)]"""
    out = []
    cards = []
    for fr in (section.get("layer") or {}).get("frames", []):
        for row in fr.get("rows", []):
            for mol in row.get("molecules", []):
                hs = [a for a in mol.get("atoms", []) if a["type"] == "header"]
                ps = [a for a in mol.get("atoms", []) if a["type"] == "plain-text"]
                if hs and ps:
                    cards.append((hs[0], ps[0]))
    for (h, ptx), (title, body) in zip(cards, VORTEILE_TEXTE):
        v, sn = single_text(h, title); out.append((h, v, sn, "vorteil header"))
        v, sn = single_text(ptx, body.format(k=k, eta=eta)); out.append((ptx, v, sn, "vorteil text"))
    return out


def footer_menu_value(menu_atom):
    items = copy.deepcopy(menu_atom["data"]["items"])
    old = copy.deepcopy(menu_atom["data"]["items"])
    mapping = {"impressum": LEGAL_URLS["impressum"], "datenschutz": LEGAL_URLS["datenschutz"], "agb": LEGAL_URLS["agb"]}
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
