#!/usr/bin/env python3
"""Patch-Operationen für Startseite, Türöffnung, Impressum, AGB, Datenschutzerklärung.
Aufruf: python3 build_special_ops.py <pages_dir> <ops_out_dir>
"""
import sys, os, json, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oplib import *  # noqa

PAGES_DIR, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

def load(slug):
    return json.load(open(os.path.join(PAGES_DIR, f"{slug}.json"), encoding="utf-8"))

class Ops:
    def __init__(self, slug, page):
        self.slug, self.page, self.patches, self.seo = slug, page, [], None
        self.S = sections_by_title(page["version"])
    def add(self, atom, value, snapshot, note):
        self.patches.append({"atomId": atom["_id"], "value": value, "snapshot": snapshot, "note": note})
    def common_header_footer(self, copyright=True):
        for hs in self.S.get("Header", []):
            for m, val, snap in header_menu_fix(hs):
                self.add(m, val, snap, "header menu")
        for fz in self.S.get("Fußzeile", []):
            if copyright:
                for pt in find_atoms(fz, "plain-text"):
                    if "Copyright" in pt["data"]["text"]["blocks"][0]["text"]:
                        val, snap = single_text(pt, "© 2026 ProVision Infra GmbH, Schlüsselnotdienst. Alle Rechte vorbehalten."); self.add(pt, val, snap, "footer text")
            for fm in find_atoms(fz, "menu-v2"):
                val, snap = footer_menu_value(fm); self.add(fm, val, snap, "footer menu")
    def dump(self):
        ops = {"slug": self.slug, "pageId": self.page["_id"], "seo": self.seo, "patches": self.patches}
        json.dump(ops, open(os.path.join(OUT, f"{self.slug}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{self.slug:22s} patches={len(self.patches):2d} title={self.seo['seoTitle']!r} ({len(self.seo['seoTitle'])})")

# ---------------- Startseite ----------------
HERO_PHOTO = "media/0496d5a4-d79f-4e3d-80a7-5efcf913dc13"
HOME_TEXT = ("Der ProVision Infra Schlüsselnotdienst sitzt in Bad Bevensen, Klein Hesebecker Straße 11. Von dort fahren wir in den Landkreis Uelzen, "
             "in den Landkreis Lüneburg und ins Wendland, bei Bedarf bis Munster, Faßberg und Celle. Nach Uelzen brauchen wir rund 20 Minuten, nach Lüneburg etwa 30. "
             "Die Türöffnung kostet in Bad Bevensen 115 €, im Umland je nach Entfernung 135 bis 260 €, inklusive Anfahrt und Mehrwertsteuer (werktags von 8 bis 18 Uhr, sonst 54 € mehr). "
             "Den Preis bestätigen wir Dir am Telefon. Wähle unten Deinen Ort.")

def home_html():
    near = "".join(f'<li><a href="/{s}">Schlüsseldienst {esc(G.kurz(G.ORTE[s]))}</a></li>' for s in ["bad-bevensen", "uelzen", "lueneburg", "bienenbuettel", "ebstorf", "dannenberg", "celle"])
    near += '<li><a href="/turoffnung">Türöffnung &amp; Preise</a></li>'
    return "\n".join([
        '<section class="pvi-local" id="einsatzgebiet">', CSS, '<div class="pvi-wrap">',
        f'<p>{esc(HOME_TEXT)}</p>',
        '<h3>Schlüsseldienst in Deiner Nähe</h3>', f'<ul class="pvi-near">{near}</ul>',
        '<h3>Alle Einsatzorte</h3>', orte_grid(None), MAP_IFRAME,
        f'<p class="pvi-cta"><a href="tel:{TEL_E164}">☎ Jetzt anrufen: {TEL}</a></p>',
        f'<p class="pvi-small" style="text-align:center;margin-top:14px">{esc(BRAND)} · {esc(B["strasse"])}, {B["plz"]} {esc(B["ort"])} · 24 Stunden, 7 Tage die Woche</p>',
        '</div></section>'])

def build_startseite():
    page = load("startseite"); o = Ops("startseite", page)
    for hero in o.S["Hero"]:
        # Hintergrund: Foto der Türöffnung statt Bild mit eingebautem Logo; kräftigeres Overlay; Text linksbündig
        mobile = hero.get("styles", {}).get("visibility_breakpoints") == "mobile"
        st = hero.get("styles", {})
        want = {"bg_image_src": HERO_PHOTO, "overlay_type": "solid", "overlay_solid_color": "black", "overlay_solid_opacity": 64,
                "align_horizontal": "left", "padding_top": 260 if mobile else 180, "padding_bottom": 90 if mobile else 120}  # mobil halbiert OnePage den Wert; 130 px Abstand zur schwebenden Kopfleiste
        cur = {k: st.get(k) for k in want}
        if cur != want:
            o.patches.append({"target": "organism", "organismId": hero["_id"], "value": {"styles": want}, "snapshot": {"styles": {k: (st.get(k) if k in st else None) for k in want}}, "note": "hero section"})
        col = 24 if mobile else 14
        for fr in hero["layer"]["frames"]:
            for row in fr["rows"]:
                for mol in row["molecules"]:
                    ms = mol.get("styles", {})
                    if ms.get("layout_column") != col or ms.get("align_center") != "left":
                        o.patches.append({"target": "molecule", "moleculeId": mol["_id"], "value": {"styles": {"layout_column": col, "align_center": "left"}}, "snapshot": {"styles": {"layout_column": ms.get("layout_column"), "align_center": ms.get("align_center")}}, "note": "hero molecule"})
        h1_size = 40 if mobile else 62
        for h in find_atoms(hero, "header"):
            blocks = h["data"]["text"]["blocks"]
            if blocks[0]["type"] == "h1":
                ob = blocks[0]
                nb = block("Schlüsselnotdienst Bad Bevensen", "h1", data=dict(ob.get("data") or {}, align_horizontal="left", font_type="custom", font_size=h1_size), key=ob.get("key"))
                nb["inlineStyleRanges"] = [{"offset": 0, "length": len(nb["text"]), "style": "BOLD"}]
                val, snap = set_text(h, [nb]); o.add(h, val, snap, "hero h1")
                hs = h.get("styles", {})
                if hs.get("font_size") != h1_size or hs.get("indentLg") != 24:
                    o.add(h, {"styles": {"font_type": "custom", "font_size": h1_size, "indentLg": 24, "font_line_height": "custom", "font_line_height_custom": 1.08}},
                          {"styles": {k: hs.get(k) for k in ("font_type", "font_size", "indentLg", "font_line_height", "font_line_height_custom")}}, "hero h1 styles")
            elif blocks[0]["type"] == "h2":
                ob = blocks[0]
                nb = block("Uelzen, Lüneburg und Umgebung. Rund um die Uhr zum Festpreis, in über 90 Prozent der Fälle ohne Schaden an Tür oder Schloss.", "h2", data=dict(ob.get("data") or {}, align_horizontal="left", font_type="m"), key=ob.get("key"))
                val, snap = set_text(h, [nb]); o.add(h, val, snap, "hero h2")
        for lg in find_atoms(hero, "link-group"):
            ls = lg.get("styles", {})
            if ls.get("align_horizontal") != "left":
                o.add(lg, {"styles": {"align_horizontal": "left"}}, {"styles": {"align_horizontal": ls.get("align_horizontal")}}, "hero buttons left")
        for lg in find_atoms(hero, "link-group"):
            d = lg["data"]
            if d.get("first_link_action_type") == "link":
                snap = {"data": {k: d[k] for k in ("first_link_action_type", "first_link_href") if k in d}}
                o.add(lg, {"data": {"first_link_action_type": "tel", "first_link_tel": "058214049049", "first_link_text": "Jetzt anrufen"}}, snap, "hero button tel")
    eg = o.S["Einsatzgebiet"][0]
    for cc in find_atoms(eg, "custom-code"):
        if "Einsatzorte" in cc["data"]["html"] or "maps" in cc["data"]["html"] or "pvi-local" in cc["data"]["html"]:
            o.add(cc, {"data": {"html": home_html()}}, {"data": {"html": cc["data"]["html"]}}, "einsatzgebiet html")
    # Preiskarten (115 € Bad Bevensen, 3 Karten) und gelbe Akzentlinien
    for sec in page["version"]["sections"]:
        for cc in find_atoms(sec, "custom-code"):
            h = cc["data"]["html"]
            if sec.get("title") == "Preisplan" and ("card" in h or "pvi-price" in h):
                newp = price_cards("115", False)
                if newp != h: o.add(cc, {"data": {"html": newp}}, {"data": {"html": h}}, "preisplan html")
            elif "accent-line" in h and h != ACCENT_HTML:
                o.add(cc, {"data": {"html": ACCENT_HTML}}, {"data": {"html": h}}, "akzentlinie")
    # Überschrift, USP-Karten, "Das bekommst Du bei uns", Kontakt-Person
    for sec in page["version"]["sections"]:
        t = sec.get("title")
        if t == "Vorteile Überschrift":
            for h in find_atoms(sec, "header"):
                val, snap = single_text(h, "Wir öffnen Deine Tür zerstörungsfrei"); o.add(h, val, snap, "überschrift")
        if t == "USP":
            cards = []
            for fr in sec["layer"]["frames"]:
                for row in fr["rows"]:
                    for mol in row["molecules"]:
                        hs = [a for a in mol["atoms"] if a["type"] == "header"]; ps = [a for a in mol["atoms"] if a["type"] == "plain-text"]
                        if hs and ps: cards.append((hs[0], ps[0]))
            texte = [
                ("Rund um die Uhr erreichbar", "Festpreis am Telefon, bevor wir losfahren.\nKeine Anfahrtskosten im Einsatzgebiet.\nIn Bad Bevensen meist nach 10 Minuten vor Ort, in Uelzen nach rund 20."),
                ("Nie wieder ausgesperrt", "Auf Wunsch sorgen wir noch vor Ort dafür, dass Dir das nicht wieder passiert: mit einem Ersatzschlüssel, einem neuen Zylinder oder einem Schließsystem, das ohne Schlüssel auskommt."),
                ("Bezahlen, wie es Dir passt", "Bar, EC- oder Kreditkarte, PayPal.\nGeschäftskunden auf Wunsch per Rechnung.\nEine Quittung oder Rechnung gibt es immer."),
            ]
            for (h, ptx), (title, body) in zip(cards, texte):
                val, snap = single_text(h, title); o.add(h, val, snap, "usp header")
                val, snap = single_text(ptx, body); o.add(ptx, val, snap, "usp text")
        if t == "Das Zeichnet UNS aus":
            heads = find_atoms(sec, "header"); texts = find_atoms(sec, "plain-text")
            mapping_h = {0: "Das bekommst Du bei uns", 1: "Fester Preis im Voraus", 2: "Zahlung nach Deinen Wünschen"}
            for i, h in enumerate(heads):
                if i in mapping_h:
                    val, snap = single_text(h, mapping_h[i]); o.add(h, val, snap, f"zeichnet header {i}")
            mapping_t = {
                0: "Hinter dem Schlüsselnotdienst steht die ProVision Infra GmbH aus Bad Bevensen. Wir planen und installieren Schließ- und Zutrittssysteme für Unternehmen und kennen Türen und Schlösser deshalb von innen. Dieses Wissen hilft, wenn Du vor verschlossener Tür stehst. Ruf an, wir sind unterwegs.",
                1: "Du kennst den Preis, bevor wir kommen. Zusatzkosten gibt es nur für Material, und auch das besprechen wir vorher.",
                2: "Bar, Karte, PayPal oder für Geschäftskunden auf Rechnung.",
            }
            for i, ptx in enumerate(texts):
                if i in mapping_t:
                    val, snap = single_text(ptx, mapping_t[i]); o.add(ptx, val, snap, f"zeichnet text {i}")
        if t == "Formular":
            for a in find_atoms(sec, "person"):
                old = copy.deepcopy(a["data"]["title_plain_text"]); new = copy.deepcopy(old)
                new["blocks"] = [dict(new["blocks"][0], text="ProVision Infra Schlüsselnotdienst")]
                o.add(a, {"data": {"title_plain_text": new}}, {"data": {"title_plain_text": old}}, "person title")
    o.common_header_footer()
    o.seo = {"title": "Startseite", "seoTitle": "Schlüsselnotdienst Bad Bevensen · Uelzen · Lüneburg 24/7",
             "seoDescription": "Schlüsseldienst für Bad Bevensen, Uelzen, Lüneburg und Umgebung: Türöffnung ab 115 € Festpreis, ohne Schaden, rund um die Uhr erreichbar. ☎ 05821 4049049",
             "seoKeywords": "Schlüsselnotdienst Bad Bevensen, Schlüsseldienst Bad Bevensen, Schlüsseldienst Uelzen, Schlüsseldienst Lüneburg, Türöffnung Festpreis, Schlüsseldienst 24h Landkreis Uelzen",
             "noindex": False}
    o.dump()

# ---------------- Türöffnung ----------------
def tuer_html(accent):
    faq = [
        ("Was kostet eine Türöffnung beim Schlüsseldienst?", "Beim ProVision Infra Schlüsselnotdienst kostet die Türöffnung montags bis freitags von 8 bis 18 Uhr 115 € in Bad Bevensen. Im Umland richtet sich der Festpreis nach der Entfernung: 135 € bis etwa 20 km, 169 € bis etwa 40 km, 199 € im Wendland und 260 € im Landkreis Celle, jeweils inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu."),
        ("Wird die Tür bei der Öffnung beschädigt?", "In über 90 Prozent der Fälle öffnen wir ohne Schaden. Muss ein Zylinder getauscht werden, besprechen wir das vorher und haben Ersatz dabei."),
        ("Muss ich mich ausweisen?", "Ja, wir öffnen nur für Berechtigte. Ohne Ausweis kannst Du die Berechtigung im Nachgang nachweisen oder schriftlich versichern."),
        ("Wie kann ich bezahlen?", "Bar, mit EC- oder Kreditkarte oder per PayPal direkt vor Ort. Geschäftskunden zahlen auf Wunsch per Rechnung."),
        ("Wie schnell seid Ihr da?", "Von Bad Bevensen aus sind wir in Uelzen in rund 20 Minuten, in Lüneburg in etwa 30 Minuten. Die genaue Ankunftszeit nennen wir Dir am Telefon."),
    ]
    faqh = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)
    near = "".join(f'<li><a href="/{s}">Schlüsseldienst {esc(G.kurz(G.ORTE[s]))}</a></li>' for s in ["bad-bevensen", "uelzen", "lueneburg", "bienenbuettel", "ebstorf", "dannenberg", "celle"])
    rows = [("Türöffnung in Bad Bevensen", "115 €"), ("Umkreis bis etwa 20 km, z. B. Uelzen, Bienenbüttel, Ebstorf", "135 €"),
            ("Umkreis etwa 20 bis 40 km, z. B. Lüneburg, Amelinghausen, Bleckede, Munster", "169 €"), ("Wendland, z. B. Lüchow, Clenze", "199 €"),
            ("Landkreis Celle, z. B. Celle, Faßberg", "260 €"), ("Fenster- oder Fahrzeugöffnung", "wie Türöffnung"),
            ("Zuschlag nachts, am Wochenende und an Feiertagen", "+ 54 €"), ("Austausch Profilzylinder (zzgl. Material)", "ab 60 €")]
    cell = 'style="padding:12px 14px;border-top:1px solid rgba(255,255,255,.1)"'
    table = ('<table style="width:100%;border-collapse:collapse;background:rgba(255,255,255,.04);border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.12)">'
             '<thead><tr style="background:#263E96;color:#fff"><th style="padding:12px 14px;text-align:left">Leistung (Mo bis Fr, 8 bis 18 Uhr)</th><th style="padding:12px 14px;text-align:right">Festpreis inkl. Anfahrt und MwSt.</th></tr></thead><tbody>'
             + "".join(f'<tr><td {cell}>{esc(a)}</td><td {cell.replace(chr(34) + ">", chr(34)[:0]) if False else cell[:-1]};text-align:right;font-weight:700;color:#FBC91B">{esc(b)}</td></tr>' for a, b in rows)
             + '</tbody></table>')
    checks = "".join(f"<li>{esc(t)}</li>" for t in [
        "Ein fester Gesamtpreis vor der Auftragserteilung, nicht „ab 19 €“.",
        "Eine Adresse in der Region und eine Festnetznummer im Impressum. Bei uns: Klein Hesebecker Straße 11, Bad Bevensen, 05821 4049049.",
        "Keine Pflicht zur Barzahlung. Karte und PayPal sind möglich, eine Quittung oder Rechnung bekommst Du immer.",
        "Ausweiskontrolle vor der Öffnung. Ein seriöser Dienst öffnet nur für Berechtigte.",
        "Öffnung ohne Schaden als Regel, Zylindertausch nur nach Absprache."])
    return "\n".join([ACCENT_HTML, '<section class="pvi-local" id="preise">', CSS, '<div class="pvi-wrap">',
        '<h2>Unsere Festpreise auf einen Blick</h2>', table,
        '<p class="pvi-small" style="margin-top:12px">Alle Preise inkl. MwSt. Den Festpreis bestätigen wir Dir vor dem Auftrag am Telefon. Zahlung bar, mit EC-/Kreditkarte oder PayPal.</p>',
        '<h2>Woran erkennst Du einen seriösen Schlüsseldienst?</h2>', f'<ul>{checks}</ul>',
        '<h2>Häufige Fragen zur Türöffnung</h2>', f'<div class="pvi-faq">{faqh}</div>',
        '<h2>Türöffnung in Deiner Nähe</h2>', f'<ul class="pvi-near">{near}</ul>',
        f'<p class="pvi-cta"><a href="tel:{TEL_E164}">☎ Jetzt anrufen: {TEL}</a></p>',
        '</div></section>'])

def build_turoffnung():
    page = load("turoffnung"); o = Ops("turoffnung", page)
    first = o.S["layout"][0]
    h1 = [a for a in find_atoms(first, "header") if a["data"]["text"]["blocks"][0]["type"] == "h1"][0]
    val, snap = single_text(h1, "Was kostet eine Türöffnung? Festpreise & Ablauf"); o.add(h1, val, snap, "h1")
    cc = find_atoms(first, "custom-code")[0]
    newh = tuer_html(cc["data"]["html"])
    if newh != cc["data"]["html"]:
        o.add(cc, {"data": {"html": newh}}, {"data": {"html": cc["data"]["html"]}}, "preise/faq html")
    # Fließtexte der Seite
    sec1, sec2 = o.S["layout"][0], o.S["layout"][1]
    for ptx in find_atoms(sec1, "plain-text"):
        val, snap = single_text(ptx, "Der Preis hängt vom Anfahrtsweg, von der Uhrzeit und davon ab, ob Material gebraucht wird. Seriöse Anbieter nennen Dir den Gesamtpreis vor dem Einsatz.\n\nBei uns kostet die Türöffnung 115 € in Bad Bevensen. Im Umland richtet sich der Festpreis nach der Entfernung, von 135 € im näheren Umkreis bis 260 € im Landkreis Celle, inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Muss ein Zylinder ersetzt werden, besprechen wir das vorher mit Dir.\n\nDie Verbraucherzentrale beschreibt, woran Du unseriöse Notdienste erkennst: an Lockpreisen, fehlender Adresse und Druck zur Barzahlung. Bei uns findest Du eine feste Adresse, eine Festnetznummer, den Preis vorab und eine Quittung.")
        o.add(ptx, val, snap, "preis text")
    for ptx in find_atoms(sec2, "plain-text"):
        val, snap = single_text(ptx, "Die Öffnung beginnt am Telefon. Wir fragen, welche Tür betroffen ist, ob sie zugefallen oder abgeschlossen ist und ob ein Schlüssel von innen steckt. So wissen wir vor der Anfahrt, welches Werkzeug wir brauchen.\n\nVor Ort prüfen wir Deinen Ausweis oder einen anderen Nachweis, dass Du hier wohnst. Dann öffnen wir mit Spezialwerkzeug, in über 90 Prozent der Fälle ohne Schaden an Tür oder Schloss.\n\nKeinen Ausweis dabei? Dann zeigst Du ihn uns im Nachgang oder bestätigst Deine Berechtigung schriftlich. Die Einzelheiten stehen in unseren AGB.")
        o.add(ptx, val, snap, "ablauf text")
    for sec in o.S.get("Bewertungen", []):
        for h in find_atoms(sec, "header"):
            val, snap = single_text(h, "Das sagen Kunden über uns"); o.add(h, val, snap, "bewertungen header")
    o.common_header_footer()
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "Was kostet eine Türöffnung beim Schlüsseldienst?", "acceptedAnswer": {"@type": "Answer", "text": "Beim ProVision Infra Schlüsselnotdienst kostet die Türöffnung montags bis freitags von 8 bis 18 Uhr 115 € in Bad Bevensen. Im Umland richtet sich der Festpreis nach der Entfernung: 135 € bis etwa 20 km, 169 € bis etwa 40 km, 199 € im Wendland und 260 € im Landkreis Celle, jeweils inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu."}},
        {"@type": "Question", "name": "Wird die Tür bei der Öffnung beschädigt?", "acceptedAnswer": {"@type": "Answer", "text": "In über 90 Prozent der Fälle öffnen wir ohne Schaden. Muss ein Zylinder getauscht werden, besprechen wir das vorher und haben Ersatz dabei."}},
        {"@type": "Question", "name": "Muss ich mich ausweisen?", "acceptedAnswer": {"@type": "Answer", "text": "Ja, wir öffnen nur für Berechtigte. Ohne Ausweis kannst Du die Berechtigung im Nachgang nachweisen oder schriftlich versichern."}},
        {"@type": "Question", "name": "Wie kann ich bezahlen?", "acceptedAnswer": {"@type": "Answer", "text": "Bar, mit EC- oder Kreditkarte oder per PayPal direkt vor Ort. Geschäftskunden zahlen auf Wunsch per Rechnung."}}]}, ensure_ascii=False, indent=1)
    bc = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Startseite", "item": G.DOMAIN + "/"}, {"@type": "ListItem", "position": 2, "name": "Türöffnung & Preise", "item": G.DOMAIN + "/turoffnung"}]}, ensure_ascii=False)
    o.seo = {"title": "Türöffnung & Preise", "seoTitle": "Was kostet eine Türöffnung? Festpreise & Ablauf",
             "seoDescription": "Was kostet eine Türöffnung? 115 € in Bad Bevensen, im Umland 135 bis 260 € je nach Entfernung. Festpreis inkl. Anfahrt, ohne Schaden, rund um die Uhr.",
             "seoKeywords": "Türöffnung Kosten, Was kostet eine Türöffnung, Türöffnung Festpreis, Schlüsseldienst Preise, seriöser Schlüsseldienst, Türöffnung Uelzen, Türöffnung Lüneburg",
             "codeHead": f'<script type="application/ld+json">\n{faq_ld}\n</script>\n<script type="application/ld+json">\n{bc}\n</script>', "noindex": False}
    o.dump()

# ---------------- Impressum / AGB / Datenschutz ----------------
def build_legal(slug, seo_title, seo_desc, phone_fix=False):
    page = load(slug); o = Ops(slug, page)
    if phone_fix:
        for sec in o.S.get("layout", []):
            for pt in find_atoms(sec, "plain-text"):
                blocks = pt["data"]["text"]["blocks"]
                if any("05821-4049040" in b["text"] for b in blocks):
                    nb = copy.deepcopy(blocks)
                    for b in nb: b["text"] = b["text"].replace("05821-4049040", "05821-4049049")
                    val, snap = set_text(pt, nb); o.add(pt, val, snap, "telefon korrigiert")
    for sec in page["version"]["sections"]:
        if "Formular" in (sec.get("title") or ""):
            for a in find_atoms(sec, "header") + find_atoms(sec, "plain-text"):
                cur = a["data"]["text"]["blocks"][0]["text"].strip()
                repl = {"Chatte mit uns": "Schreib uns", "beispiel@gmail.com": "schluesselnotdienst-baumann@t-online.de",
                        "E-Mail an Schlüsselnotdienst Baumann": "Schreib uns eine E-Mail", "Unser Team ist hier, um Dir zu helfen": "Wir antworten in der Regel am selben Tag",
                        "Schlüsselnotdienst Jannes Heino Baumann": "ProVision Infra Schlüsselnotdienst", "Kontaktiere Uns": "Kontakt", "Mo-So von 00:00 bis 24:00": "Täglich rund um die Uhr"}
                if cur in repl:
                    val, snap = single_text(a, repl[cur]); o.add(a, val, snap, f"kontakt: {cur[:20]}")
    o.common_header_footer()
    # Rechtstexte liegen bei provision-infra.de; die internen Seiten bleiben erreichbar, aber ohne Indexierung
    o.seo = {"seoTitle": seo_title, "seoDescription": seo_desc, "noindex": True}
    o.dump()

build_startseite()
build_turoffnung()
build_legal("impressum", "Impressum | ProVision Infra Schlüsselnotdienst", "Impressum des ProVision Infra Schlüsselnotdienstes (ProVision Infra GmbH, Bad Bevensen): Anbieterkennzeichnung, Kontaktdaten und rechtliche Hinweise.", phone_fix=True)
build_legal("agb", "AGB | ProVision Infra Schlüsselnotdienst", "Allgemeine Geschäftsbedingungen des ProVision Infra Schlüsselnotdienstes: Türöffnung, Berechtigungsnachweis, Festpreise, Zahlung und Haftung.")
build_legal("datenschutzerklarung", "Datenschutzerklärung | ProVision Infra Schlüsselnotdienst", "Datenschutzerklärung des ProVision Infra Schlüsselnotdienstes: Welche Daten wir verarbeiten, zu welchem Zweck und welche Rechte Du hast.")
