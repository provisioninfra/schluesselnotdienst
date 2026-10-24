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
                        val, snap = single_text(pt, "Copyright © 2026 ProVision Infra GmbH – Schlüsselnotdienst – Alle Rechte vorbehalten."); self.add(pt, val, snap, "footer text")
            for fm in find_atoms(fz, "menu-v2"):
                val, snap = footer_menu_value(fm); self.add(fm, val, snap, "footer menu")
    def dump(self):
        ops = {"slug": self.slug, "pageId": self.page["_id"], "seo": self.seo, "patches": self.patches}
        json.dump(ops, open(os.path.join(OUT, f"{self.slug}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{self.slug:22s} patches={len(self.patches):2d} title={self.seo['seoTitle']!r} ({len(self.seo['seoTitle'])})")

# ---------------- Startseite ----------------
HOME_TEXT = ("Der ProVision Infra Schlüsselnotdienst sitzt in Bad Bevensen (Klein Hesebecker Straße 11) und ist als mobiler Schlüsseldienst im gesamten Landkreis Uelzen, "
             "im Landkreis Lüneburg und im Landkreis Lüchow-Dannenberg unterwegs – bis nach Munster, Faßberg und Celle. Kurze Wege bedeuten kurze Wartezeiten: "
             "Nach Uelzen brauchen wir rund 20 Minuten, nach Lüneburg etwa 30. Den Festpreis für die Türöffnung inklusive Anfahrt nennen wir Dir vorab am Telefon – "
             "in Bad Bevensen 115 €, im Umland 135 € (Mo–Fr 8–18 Uhr, sonst + 54 €). Wähle unten Deinen Ort, um Anfahrtszeit, Preise und Leistungen für Deine Region zu sehen.")

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
        for h in find_atoms(hero, "header"):
            blocks = h["data"]["text"]["blocks"]
            if blocks[0]["type"] == "h1":
                nb = []
                for i, b in enumerate(blocks):
                    b2 = copy.deepcopy(b)
                    if i == 0:
                        b2["text"] = "Schlüsselnotdienst Bad Bevensen"
                        b2["inlineStyleRanges"] = [{"offset": 0, "length": len(b2["text"]), "style": "BOLD"}]
                    else:
                        b2["type"] = "unstyled"  # leere Zeilen: keine zusätzlichen H1-Tags mehr
                    nb.append(b2)
                val, snap = set_text(h, nb); o.add(h, val, snap, "hero h1")
            elif blocks[0]["type"] == "h2":
                val, snap = single_text(h, "Uelzen • Lüneburg • Umgebung – 24/7 Notdienst zum Festpreis"); o.add(h, val, snap, "hero h2")
        for lg in find_atoms(hero, "link-group"):
            d = lg["data"]
            if d.get("first_link_action_type") == "link":
                snap = {"data": {k: d[k] for k in ("first_link_action_type", "first_link_href") if k in d}}
                o.add(lg, {"data": {"first_link_action_type": "tel", "first_link_tel": "058214049049", "first_link_text": "Jetzt anrufen"}}, snap, "hero button tel")
    eg = o.S["Einsatzgebiet"][0]
    for cc in find_atoms(eg, "custom-code"):
        if "Einsatzorte" in cc["data"]["html"] or "maps" in cc["data"]["html"]:
            o.add(cc, {"data": {"html": home_html()}}, {"data": {"html": cc["data"]["html"]}}, "einsatzgebiet html")
    o.common_header_footer()
    o.seo = {"title": "Startseite", "seoTitle": "Schlüsselnotdienst Bad Bevensen · Uelzen · Lüneburg 24/7",
             "seoDescription": "Schlüsseldienst für Bad Bevensen, Uelzen, Lüneburg & Umgebung: Türöffnung ab 115 € Festpreis, zerstörungsfrei, 24/7, keine Anfahrtskosten. ☎ 05821 4049049",
             "seoKeywords": "Schlüsselnotdienst Bad Bevensen, Schlüsseldienst Bad Bevensen, Schlüsseldienst Uelzen, Schlüsseldienst Lüneburg, Türöffnung Festpreis, Schlüsseldienst 24h Landkreis Uelzen",
             "noindex": False}
    o.dump()

# ---------------- Türöffnung ----------------
def tuer_html(accent):
    faq = [
        ("Was kostet eine Türöffnung beim Schlüsseldienst?", "Beim ProVision Infra Schlüsselnotdienst kostet die Türöffnung montags bis freitags von 8 bis 18 Uhr 115 € in Bad Bevensen und 135 € im Umland – Festpreis inklusive Anfahrt und MwSt. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Den Preis bestätigen wir vor dem Auftrag am Telefon."),
        ("Wird die Tür bei der Öffnung beschädigt?", "In über 90 % der Fälle öffnen wir zerstörungsfrei. Muss ein Zylinder getauscht werden, besprechen wir das vorher und haben Ersatz dabei."),
        ("Muss ich mich ausweisen?", "Ja, wir öffnen nur für Berechtigte. Ohne Ausweis kannst Du die Berechtigung im Nachgang nachweisen oder rechtsverbindlich versichern."),
        ("Wie kann ich bezahlen?", "Bar, mit EC- oder Kreditkarte oder per PayPal direkt vor Ort; Geschäftskunden auch auf Rechnung."),
        ("Wie schnell seid Ihr da?", "Von Bad Bevensen aus sind wir in Uelzen in rund 20 Minuten, in Lüneburg in etwa 30 Minuten. Die genaue Ankunftszeit nennen wir Dir am Telefon."),
    ]
    faqh = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)
    near = "".join(f'<li><a href="/{s}">Schlüsseldienst {esc(G.kurz(G.ORTE[s]))}</a></li>' for s in ["bad-bevensen", "uelzen", "lueneburg", "bienenbuettel", "ebstorf", "dannenberg", "celle"])
    table = ('<table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,.05)">'
             '<thead><tr style="background:#115697;color:#fff"><th style="padding:12px 14px;text-align:left">Leistung</th><th style="padding:12px 14px;text-align:right">Festpreis inkl. Anfahrt &amp; MwSt.</th></tr></thead><tbody>'
             '<tr><td style="padding:12px 14px;border-top:1px solid #e3ebf5">Türöffnung in Bad Bevensen (Mo–Fr 8–18 Uhr)</td><td style="padding:12px 14px;border-top:1px solid #e3ebf5;text-align:right;font-weight:700">115 €</td></tr>'
             '<tr><td style="padding:12px 14px;border-top:1px solid #e3ebf5">Türöffnung im Umland Uelzen / Lüneburg / Lüchow-Dannenberg (Mo–Fr 8–18 Uhr)</td><td style="padding:12px 14px;border-top:1px solid #e3ebf5;text-align:right;font-weight:700">135 €</td></tr>'
             '<tr><td style="padding:12px 14px;border-top:1px solid #e3ebf5">Fenster- oder Fahrzeugöffnung</td><td style="padding:12px 14px;border-top:1px solid #e3ebf5;text-align:right;font-weight:700">wie Türöffnung</td></tr>'
             '<tr><td style="padding:12px 14px;border-top:1px solid #e3ebf5">Zuschlag nachts, Wochenende, Feiertag</td><td style="padding:12px 14px;border-top:1px solid #e3ebf5;text-align:right;font-weight:700">+ 54 €</td></tr>'
             '<tr><td style="padding:12px 14px;border-top:1px solid #e3ebf5">Austausch Profilzylinder (zzgl. Material)</td><td style="padding:12px 14px;border-top:1px solid #e3ebf5;text-align:right;font-weight:700">ab 60 €</td></tr>'
             '</tbody></table>')
    checks = "".join(f"<li>{esc(t)}</li>" for t in [
        "Fester Gesamtpreis vor Auftragserteilung am Telefon – nicht „ab 19 €“.",
        "Regionale Adresse im Impressum und eine Festnetznummer (bei uns: Klein Hesebecker Straße 11, Bad Bevensen, 05821 4049049).",
        "Keine Barzahlungspflicht: Karte und PayPal sind möglich, Du bekommst eine Quittung oder Rechnung.",
        "Ausweiskontrolle vor der Öffnung – ein seriöser Dienst öffnet nur für Berechtigte.",
        "Zerstörungsfreie Öffnung als Standard, Zylindertausch nur nach Absprache."])
    return "\n".join([accent, '<section class="pvi-local" id="preise">', CSS, '<div class="pvi-wrap">',
        '<h3>Unsere Festpreise auf einen Blick</h3>', table,
        '<p class="pvi-small" style="margin-top:12px">Alle Preise inkl. MwSt. Den Festpreis bestätigen wir Dir vor dem Auftrag am Telefon. Zahlung bar, mit EC-/Kreditkarte oder PayPal.</p>',
        '<h3>Woran erkennst Du einen seriösen Schlüsseldienst?</h3>', f'<ul>{checks}</ul>',
        '<h3>Häufige Fragen zur Türöffnung</h3>', f'<div class="pvi-faq">{faqh}</div>',
        '<h3>Türöffnung in Deiner Nähe</h3>', f'<ul class="pvi-near">{near}</ul>',
        f'<p class="pvi-cta"><a href="tel:{TEL_E164}">☎ Jetzt anrufen: {TEL}</a></p>',
        '</div></section>'])

def build_turoffnung():
    page = load("turoffnung"); o = Ops("turoffnung", page)
    first = o.S["layout"][0]
    h1 = [a for a in find_atoms(first, "header") if a["data"]["text"]["blocks"][0]["type"] == "h1"][0]
    val, snap = single_text(h1, "Was kostet eine Türöffnung? Festpreise & Ablauf"); o.add(h1, val, snap, "h1")
    cc = find_atoms(first, "custom-code")[0]
    o.add(cc, {"data": {"html": tuer_html(cc["data"]["html"])}}, {"data": {"html": cc["data"]["html"]}}, "preise/faq html")
    o.common_header_footer()
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "Was kostet eine Türöffnung beim Schlüsseldienst?", "acceptedAnswer": {"@type": "Answer", "text": "Beim ProVision Infra Schlüsselnotdienst kostet die Türöffnung montags bis freitags von 8 bis 18 Uhr 115 € in Bad Bevensen und 135 € im Umland – Festpreis inklusive Anfahrt und MwSt. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu."}},
        {"@type": "Question", "name": "Wird die Tür bei der Öffnung beschädigt?", "acceptedAnswer": {"@type": "Answer", "text": "In über 90 % der Fälle öffnen wir zerstörungsfrei. Muss ein Zylinder getauscht werden, besprechen wir das vorher und haben Ersatz dabei."}},
        {"@type": "Question", "name": "Muss ich mich ausweisen?", "acceptedAnswer": {"@type": "Answer", "text": "Ja, wir öffnen nur für Berechtigte. Ohne Ausweis kannst Du die Berechtigung im Nachgang nachweisen oder rechtsverbindlich versichern."}},
        {"@type": "Question", "name": "Wie kann ich bezahlen?", "acceptedAnswer": {"@type": "Answer", "text": "Bar, mit EC- oder Kreditkarte oder per PayPal direkt vor Ort; Geschäftskunden auch auf Rechnung."}}]}, ensure_ascii=False, indent=1)
    bc = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Startseite", "item": G.DOMAIN + "/"}, {"@type": "ListItem", "position": 2, "name": "Türöffnung & Preise", "item": G.DOMAIN + "/turoffnung"}]}, ensure_ascii=False)
    o.seo = {"title": "Türöffnung & Preise", "seoTitle": "Was kostet eine Türöffnung? Festpreise & Ablauf",
             "seoDescription": "Was darf eine Türöffnung kosten? 115 € in Bad Bevensen, 135 € im Umland – Festpreis inkl. Anfahrt, zerstörungsfrei, 24/7 erreichbar. So arbeitet ProVision Infra.",
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
    o.common_header_footer()
    o.seo = {"seoTitle": seo_title, "seoDescription": seo_desc, "noindex": False}
    o.dump()

build_startseite()
build_turoffnung()
build_legal("impressum", "Impressum | ProVision Infra Schlüsselnotdienst", "Impressum des ProVision Infra Schlüsselnotdienstes (ProVision Infra GmbH, Bad Bevensen): Anbieterkennzeichnung, Kontaktdaten und rechtliche Hinweise.", phone_fix=True)
build_legal("agb", "AGB | ProVision Infra Schlüsselnotdienst", "Allgemeine Geschäftsbedingungen des ProVision Infra Schlüsselnotdienstes: Türöffnung, Berechtigungsnachweis, Festpreise, Zahlung und Haftung.")
build_legal("datenschutzerklarung", "Datenschutzerklärung | ProVision Infra Schlüsselnotdienst", "Datenschutzerklärung des ProVision Infra Schlüsselnotdienstes: Welche Daten wir verarbeiten, zu welchem Zweck und welche Rechte Du hast.")
