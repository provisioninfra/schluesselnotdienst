#!/usr/bin/env python3
"""Erzeugt aus orte.json die Texte und SEO-Daten für jede Orts-Unterseite.

Jeder Baustein liegt in mehreren Fassungen vor. Welche Fassung ein Ort bekommt, entscheidet ein
Hash aus Slug und Baustein. So liest sich jede Seite anders, ohne dass Inhalte erfunden werden.
Regeln: keine Gedankenstriche, keine Dreiergruppen als Stilmittel, keine vagen Autoritäten.

Aufruf:  python3 seo/tools/generate_pages.py
Ausgabe: seo/seiten/<slug>.md, seo/05-keyword-map.csv, seo/06-interne-verlinkung.md
"""
import json, csv, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "seiten")
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(HERE, "orte.json"), encoding="utf-8"))
B = D["basis"]
ORTE = {o["slug"]: o for o in D["orte"]}
DOMAIN = B["domain"]
TEL = B["telefon_anzeige"]


# Zuordnung der Textfassungen je Ort. optimize_variants.py verteilt sie so, dass sich keine zwei Seiten zu stark ähneln
# (seo/tools/varianten.json). Ohne Datei entscheidet ein Hash aus Slug und Baustein.
_VAR_FILE = os.path.join(HERE, "varianten.json")
VARIANTS = json.load(open(_VAR_FILE, encoding="utf-8")) if os.path.exists(_VAR_FILE) else {}


def pick(slug, salt, n):
    v = VARIANTS.get(slug, {}).get(salt)
    if v is not None:
        return v % n
    return int(hashlib.md5(f"{slug}:{salt}".encode()).hexdigest(), 16) % n


def variant(slug, salt, options, **fmt):
    return options[pick(slug, salt, len(options))].format(**fmt)


def kurz(o):
    return o.get("name_kurz", o["name"])


def fmt_args(o):
    sg = o.get("samtgemeinde")
    lage = f"{kurz(o)} ({o['art']}, {o['kreis']}" + (f", {sg})" if sg else ")")
    return dict(k=kurz(o), eta=o["eta"], p=o["preis_tueroeffnung"], TEL=TEL, lage=lage, strasse=B["strasse"])


# ---------------------------------------------------------------- SEO-Felder
def title_for(o):
    a = fmt_args(o)
    cands = [
        "Schlüsseldienst {k}: 24h Notdienst zum Festpreis",
        "Schlüsseldienst {k}: Türöffnung ab {p} €, Tag und Nacht",
        "Schlüsselnotdienst {k}: Türöffnung zum Festpreis",
        "Schlüsseldienst in {k}: Festpreis {p} €, rund um die Uhr",
    ]
    start = pick(o["slug"], "title", len(cands))
    order = cands[start:] + cands[:start] + ["Schlüsseldienst {k}: Notdienst zum Festpreis", "Schlüsseldienst {k} 24h"]
    for c in order:
        t = c.format(**a)
        if len(t) <= 60:
            return t
    return f"Schlüsseldienst {a['k']}"


def desc_for(o):
    a = fmt_args(o)
    cands = [
        "Ausgesperrt in {k}? Wir öffnen Deine Tür ohne Schaden, Festpreis {p} € inkl. Anfahrt. Tag und Nacht erreichbar, in etwa {eta} Minuten vor Ort. ☎ {TEL}",
        "Schlüsseldienst {k}: Türöffnung für {p} € inkl. Anfahrt und MwSt., rund um die Uhr erreichbar, in etwa {eta} Minuten bei Dir. ☎ {TEL}",
        "Schlüsselnotdienst für {k} und Umgebung: Türöffnung zum Festpreis von {p} €, 24 Stunden erreichbar, in etwa {eta} Minuten vor Ort. ☎ {TEL}",
        "Tür zu in {k}? Der ProVision Infra Schlüsselnotdienst kommt in rund {eta} Minuten und öffnet zum Festpreis von {p} €, Anfahrt inklusive. ☎ {TEL}",
        "Schlüsseldienst in {k} mit Festpreis: Türöffnung {p} € inkl. Anfahrt, meist ohne Schaden, Tag und Nacht erreichbar. Ankunft in etwa {eta} Minuten. ☎ {TEL}",
    ]
    start = pick(o["slug"], "desc", len(cands))
    for c in cands[start:] + cands[:start]:
        d = c.format(**a)
        if len(d) <= 155:
            return d
    return f"Schlüsseldienst {a['k']}: Türöffnung für {a['p']} € inkl. Anfahrt, Tag und Nacht erreichbar. ☎ {TEL}"


def keywords(o):
    k = kurz(o)
    return f"Schlüsseldienst {k}, Schlüsselnotdienst {k}, Türöffnung {k}, Schlüsseldienst {k} 24h, Aufsperrdienst {k}, Schlüsseldienst {k} Kosten, Autoöffnung {k}"


# ---------------------------------------------------------------- Hero
def hero_h1(o):
    return variant(o["slug"], "h1", [
        "Schlüsseldienst {k}: Notdienst rund um die Uhr zum Festpreis",
        "Schlüsseldienst {k}: Türöffnung zum Festpreis, Tag und Nacht",
        "Schlüsselnotdienst {k}: schnell vor Ort, Preis vorab",
        "Schlüsseldienst für {k}: 24 Stunden erreichbar, Festpreis vorab",
    ], **fmt_args(o))


def hero_h2(o):
    return variant(o["slug"], "h2", [
        "ProVision Infra Schlüsselnotdienst für {k}",
        "ProVision Infra Schlüsselnotdienst in {k}",
        "Dein Schlüsselnotdienst für {k} und Umgebung",
    ], **fmt_args(o))


def hero_lines(o):
    """Drei Zeilen für den Hero-Text; die letzte Zeile wird fett gesetzt."""
    a = fmt_args(o)
    sets = [
        ("Türöffnung in {k} und Umgebung", "Festpreis {p} € inkl. Anfahrt, in etwa {eta} Minuten bei Dir", "ohne Schaden an Tür und Schloss, zum vorher genannten Preis"),
        ("Ausgesperrt in {k}? Wir kommen.", "{p} € Festpreis inklusive Anfahrt, Ankunft in rund {eta} Minuten", "Öffnung in der Regel ohne Schaden, Preis vorab am Telefon"),
        ("Schlüsselnotdienst für {k}", "Türöffnung zum Festpreis von {p} €, Anfahrt inklusive", "nach etwa {eta} Minuten vor Ort, Preis vorher zugesagt"),
    ]
    return [s.format(**a) for s in sets[pick(o["slug"], "herolines", len(sets))]]


def hero_alt(o):
    return f"Schlüsseldienst öffnet eine Haustür in {kurz(o)}, ProVision Infra Schlüsselnotdienst"


# ---------------------------------------------------------------- Vorteile (drei Karten)
def vorteile(o):
    a = fmt_args(o)
    cards = [
        ("Rund um die Uhr erreichbar", [
            "Tag und Nacht, auch an Feiertagen.\nFestpreis am Telefon, bevor wir losfahren.\nIn {k} meist nach etwa {eta} Minuten vor Ort.",
            "Anruf genügt, zu jeder Uhrzeit.\nNach etwa {eta} Minuten sind wir in {k}.\nDen Preis kennst Du vorher.",
            "Wochenende, Feiertag oder mitten in der Nacht: Wir gehen ran.\nAnkunft in {k} nach rund {eta} Minuten.\nFestpreis vorab.",
        ]),
        ("Feste Preise ohne Überraschungen", [
            "Anfahrt und Mehrwertsteuer sind im Preis enthalten.\nMaterial wie ein neuer Zylinder berechnen wir nur nach Absprache.",
            "Ein Preis, am Telefon genannt und vor Ort eingehalten.\nZuschläge gibt es nur nachts und am Wochenende, und die kennst Du vorher.",
            "Keine Anfahrtskosten und keine Pauschale für schwierige Türen.\nMaterial kommt nur dazu, wenn Du es vorher freigibst.",
        ]),
        ("Bezahlen, wie es Dir passt", [
            "Bar, EC- oder Kreditkarte, PayPal.\nGeschäftskunden auf Wunsch per Rechnung.\nEine Quittung oder Rechnung gibt es immer.",
            "Karte, PayPal oder bar, ganz wie Du möchtest.\nFirmen zahlen auf Rechnung.\nDie Quittung bekommst Du sofort.",
            "Wir nehmen Bargeld, Karte und PayPal.\nFür Unternehmen stellen wir eine Rechnung aus.\nEinen Beleg gibt es in jedem Fall.",
        ]),
    ]
    out = []
    for i, (title, texts) in enumerate(cards):
        out.append((title, texts[pick(o["slug"], f"vorteil{i}", len(texts))].format(**a)))
    return out


# ---------------------------------------------------------------- Abschnittstitel
def einsatz_header(o):
    return variant(o["slug"], "egh", [
        "Alles Wichtige für {k}: Preise, Ablauf, Antworten und Einsatzgebiet",
        "Schlüsseldienst {k}: Preise, Ablauf und Antworten",
        "Was Du über den Schlüsseldienst in {k} wissen solltest",
        "Türöffnung in {k}: Kosten, Ablauf und häufige Fragen",
    ], **fmt_args(o))


def preisplan_header(o):
    return variant(o["slug"], "pph", [
        "Leistungen für {k}",
        "Leistungen und Festpreise in {k}",
        "Unsere Festpreise für {k}",
    ], **fmt_args(o))


def headings(o):
    k = kurz(o)
    s = o["slug"]
    return {
        "preis": f"Was kostet der Schlüsseldienst in {k}?",
        "ablauf": variant(s, "hab", ["So läuft Deine Türöffnung in {k} ab", "Ablauf einer Türöffnung in {k}", "So läuft der Einsatz in {k} ab"], k=k),
        "leistungen": variant(s, "hle", ["Unsere Leistungen in {k}", "Leistungen vor Ort in {k}", "Das machen wir in {k}"], k=k),
        "faq": variant(s, "hfa", ["Häufige Fragen zum Schlüsseldienst in {k}", "Fragen und Antworten für {k}", "Häufige Fragen aus {k}"], k=k),
        "nah": variant(s, "hna", ["Schlüsseldienst in der Nähe von {k}", "Auch in der Nähe von {k} im Einsatz", "Nachbarorte von {k}"], k=k),
        "gebiet": "Unser Einsatzgebiet",
    }


# ---------------------------------------------------------------- Fließtexte
def intro(o):
    a = fmt_args(o)
    if o["slug"] == "bad-bevensen":
        return ("Du stehst in Bad Bevensen vor verschlossener Tür? Dann ist Hilfe nah. Der ProVision Infra Schlüsselnotdienst hat seinen Sitz in der "
                f"{B['strasse']}, mitten in der Kurstadt. Kein Callcenter und keine Vermittlung: Du sprichst direkt mit dem Monteur, der zu Dir kommt. "
                f"Meist sind wir innerhalb von {a['eta']} Minuten da, in der Innenstadt, im Kurviertel oder in den Ortsteilen von Medingen bis Seedorf. "
                f"Die Öffnung gelingt in über 90 Prozent der Fälle ohne Schaden, zum Festpreis von {a['p']} €.")
    return variant(o["slug"], "intro", [
        "Die Tür ist zu und der Schlüssel liegt drinnen? In {k} hilft der ProVision Infra Schlüsselnotdienst aus Bad Bevensen, Tag und Nacht. Bis zu Dir brauchen wir etwa {eta} Minuten, den Preis nennen wir vor der Abfahrt.",
        "Der Schlüsseldienst für {lage}: Wenn die Tür zugefallen ist oder das Schloss klemmt, kommt der ProVision Infra Schlüsselnotdienst, auch nachts und am Wochenende. Von Bad Bevensen aus sind wir in rund {eta} Minuten bei Dir.",
        "In {k} und Umgebung öffnet der ProVision Infra Schlüsselnotdienst Türen zum Festpreis von {p} €. Der Betrieb sitzt in Bad Bevensen im Landkreis Uelzen, die Anfahrt dauert etwa {eta} Minuten.",
        "Ausgesperrt in {k}? Ruf an, wir sind unterwegs. Der ProVision Infra Schlüsselnotdienst erreicht {k} in rund {eta} Minuten und öffnet die Tür in den meisten Fällen ohne Schaden.",
        "Schlüssel verloren oder Tür zugefallen? Für {k} ist der ProVision Infra Schlüsselnotdienst aus Bad Bevensen zuständig. Festpreis {p} €, Anfahrt inklusive, Ankunft nach etwa {eta} Minuten.",
        "Wer in {k} vor verschlossener Tür steht, erreicht uns rund um die Uhr. Der ProVision Infra Schlüsselnotdienst kommt aus Bad Bevensen und ist nach etwa {eta} Minuten vor Ort, zum vorher genannten Festpreis.",
    ], **a)


def lokal_abschnitt(o):
    a = fmt_args(o)
    teile = o.get("ortsteile") or []
    s = o["lokal"].replace(" – ", ", ").replace("–", ",") + " "
    # Ortsteile nur ergänzen, wenn der handgeschriebene Absatz sie nicht schon nennt
    if teile and o["slug"] != "bad-bevensen" and not any(t in o["lokal"] for t in teile):
        liste = ", ".join(teile[:-1]) + f" und {teile[-1]}" if len(teile) > 1 else teile[0]
        s += variant(o["slug"], "teile", [
            "Wir kommen in alle Stadt- und Ortsteile, darunter {liste}. ",
            "Zum Einsatzgebiet gehören auch {liste}. ",
            "Ob {liste}: Wir fahren jeden Ortsteil an. ",
        ], liste=liste)
    s += variant(o["slug"], "lokal", [
        "Im Fahrzeug haben wir Werkzeug und gängige Profilzylinder dabei, deshalb erledigen wir die meisten Aufträge in {k} in einem Termin.",
        "Wir kommen aus der Region und kennen die Wege nach {k}. Das spart Zeit, wenn es eilt.",
        "Unser Einsatzfahrzeug ist so bestückt, dass wir in {k} eine Tür öffnen und bei Bedarf gleich einen neuen Zylinder einbauen können.",
        "Auch kleine Reparaturen am Schloss übernehmen wir direkt vor Ort in {k}, ohne zweiten Termin.",
    ], **a)
    return s


def leistungen(o):
    a = fmt_args(o)
    s = o["slug"]
    items = [
        ("Türöffnung", ["Wohnungs-, Haus- und Zimmertüren in {k}, zugefallen oder abgeschlossen. Festpreis inklusive Anfahrt, Zuschlag nachts und am Wochenende vorher genannt.",
                        "Zugefallene oder abgeschlossene Türen in {k} öffnen wir zum Festpreis, in der Regel ohne Schaden am Schloss."]),
        ("Fensteröffnung", ["Gekippte oder zugefallene Fenster und Terrassentüren öffnen wir ohne Beschädigung.",
                            "Fenster und Balkontüren, die zugefallen sind oder gekippt stehen, öffnen wir schonend."]),
        ("Fahrzeugöffnung", ["Autoschlüssel eingeschlossen? Wir öffnen abgeschlossene Fahrzeuge in {k} schonend.",
                             "Schlüssel im Auto? Pkw und Transporter öffnen wir in {k} ohne Kratzer."]),
        ("Schließzylinder und Schlösser", ["Austausch und Reparatur von Profilzylindern, Einbau von Sicherheitszylindern mit Sicherungskarte. Gängige Zylinder haben wir vorrätig.",
                                          "Neue Profilzylinder, Sicherheitszylinder mit Sicherungskarte und Reparaturen am Schloss, meist direkt im ersten Termin."]),
        ("Schließanlagen und Zutrittssysteme", ["Planung und Montage von Schließanlagen und digitalen Zutrittslösungen, etwa von SimonsVoss oder EVVA, für Mehrfamilienhäuser und Betriebe.",
                                               "Mechanische Schließanlagen und elektronische Zutrittssysteme für Hausverwaltungen, Praxen und Unternehmen in {k}."]),
        ("Einbruchschutz", ["Beratung bei Dir vor Ort in {k}: Beschläge, Zusatzschlösser, Panzerriegel und ein Blick auf Fenster und Nebeneingänge.",
                            "Wir zeigen Dir, wo Deine Tür oder Dein Fenster in {k} angreifbar ist, und rüsten mit Beschlägen oder Zusatzschlössern nach."]),
    ]
    return [(name, texts[pick(s, f"leist{i}", len(texts))].format(**a)) for i, (name, texts) in enumerate(items)]


def preise(o):
    a = fmt_args(o)
    s = o["slug"]
    haupt = variant(s, "preis", [
        "Den Festpreis für Deine Türöffnung in {k} nennen wir Dir am Telefon, inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen gilt ein fester Zuschlag, den Du ebenfalls vorher erfährst. Materialkosten entstehen nur, wenn zum Beispiel ein neuer Zylinder nötig ist.",
        "Für eine Türöffnung am Tag hält die Verbraucherzentrale Gesamtpreise im unteren dreistelligen Bereich für angemessen. In diesem Rahmen liegen wir in {k}. Getrennte Anfahrtskosten oder Aufschläge für schwierige Öffnungen gibt es nicht.",
        "Festpreis am Telefon, Anfahrt nach {k} inklusive, Zuschlag für Nacht und Wochenende vorher benannt. Du entscheidest erst, wenn Du den Preis kennst, und zahlst nach der Arbeit bar, mit Karte oder per PayPal.",
        "Was eine Türöffnung in {k} kostet, hängt von Uhrzeit und Entfernung ab, nicht von der Dauer des Einsatzes. Der Preis steht vor der Anfahrt fest und ändert sich vor Ort nicht.",
    ], **a)
    konkret = variant(s, "konkret", [
        " Konkret: Die Türöffnung in {k} kostet montags bis freitags von 8 bis 18 Uhr {p} €, inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Fenster- und Fahrzeugöffnung kosten dasselbe, ein neuer Profilzylinder beginnt bei 60 € zuzüglich Material.",
        " In Zahlen: {p} € für die Türöffnung in {k} an Werktagen zwischen 8 und 18 Uhr, Anfahrt und Mehrwertsteuer eingerechnet. Außerhalb dieser Zeiten und an Feiertagen sind es 54 € mehr. Der Austausch eines Profilzylinders kostet ab 60 € plus Material.",
    ], **a)
    return haupt + konkret


def ablauf(o):
    a = fmt_args(o)
    sets = [
        ["**Anruf:** Du rufst an unter {TEL}. Wir fragen nach Türart und Situation und nennen Dir Festpreis und Ankunftszeit.",
         "**Anfahrt:** Wir fahren sofort los. Nach etwa {eta} Minuten sind wir in {k}.",
         "**Berechtigung:** Vor Ort zeigst Du uns Deinen Ausweis oder einen anderen Nachweis, dass Du hier wohnst.",
         "**Öffnung:** Mit Spezialwerkzeug öffnen wir die Tür, in über 90 Prozent der Fälle ohne Schaden. Falls ein Zylinder getauscht werden muss, haben wir Ersatz dabei.",
         "**Bezahlung:** Du zahlst den vorher genannten Preis, bar, mit Karte oder per PayPal, und bekommst eine Quittung oder Rechnung."],
        ["**Anruf:** Du schilderst kurz, welche Tür betroffen ist. Wir nennen Preis und Ankunftszeit.",
         "**Anfahrt:** Nach etwa {eta} Minuten sind wir in {k}.",
         "**Ausweis und Öffnung:** Du zeigst uns einen Nachweis, dann öffnen wir mit Spezialwerkzeug, meist ohne Schaden.",
         "**Bezahlung:** Bar, Karte oder PayPal, Quittung inklusive."],
        ["**Du rufst an:** {TEL}, Tag und Nacht.",
         "**Wir fahren los:** von Bad Bevensen nach {k}, etwa {eta} Minuten.",
         "**Wir prüfen die Berechtigung:** Ausweis, Mietvertrag oder ein anderer Nachweis.",
         "**Wir öffnen:** mit Spezialwerkzeug, in über 90 Prozent der Fälle ohne Schaden.",
         "**Du zahlst den genannten Preis:** bar, mit Karte oder per PayPal."],
    ]
    return [s.format(**a) for s in sets[pick(o["slug"], "ablauf", len(sets))]]


def faq(o):
    a = fmt_args(o)
    s = o["slug"]
    speed = ("Wie schnell ist der Schlüsseldienst in {k} vor Ort?", [
        "Von Bad Bevensen nach {k} brauchen wir in der Regel etwa {eta} Minuten. Die genaue Ankunftszeit nennen wir Dir am Telefon.",
        "Meist sind wir nach rund {eta} Minuten in {k}. Nachts geht es oft schneller, weil die Straßen frei sind."])
    price = ("Was kostet eine Türöffnung in {k}?", [
        "Montags bis freitags von 8 bis 18 Uhr {p} €, inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Den Preis bestätigen wir Dir vor dem Auftrag.",
        "{p} € zum Festpreis an Werktagen zwischen 8 und 18 Uhr, Anfahrt und Mehrwertsteuer eingerechnet. Zu anderen Zeiten sind es 54 € mehr, auch das sagen wir Dir vorher."])
    pool = [
        ("Wird meine Tür beim Öffnen beschädigt?", ["In über 90 Prozent der Fälle öffnen wir ohne Schaden. Bei zugefallenen Türen gelingt das fast immer. Ist die Tür abgeschlossen, sagen wir Dir vorher, falls ein Zylinder getauscht werden muss."]),
        ("Ist der Schlüsselnotdienst in {k} auch nachts und am Wochenende erreichbar?", ["Ja, an jedem Tag und zu jeder Uhrzeit, auch an Feiertagen. Ruf einfach an: {TEL}."]),
        ("Muss ich mich ausweisen?", ["Ja, wir öffnen nur für Berechtigte. Hast Du den Ausweis nicht dabei, zeigst Du ihn uns im Nachgang oder bestätigst Deine Berechtigung schriftlich."]),
        ("Kann ich mit Karte oder PayPal bezahlen?", ["Ja. Neben Bargeld nehmen wir EC- und Kreditkarte sowie PayPal direkt vor Ort. Geschäftskunden zahlen auf Wunsch per Rechnung."]),
        ("Woran erkenne ich einen seriösen Schlüsseldienst in {k}?", ["An einem festen Gesamtpreis vor dem Auftrag, einer Adresse in der Region und daran, dass niemand Barzahlung erzwingt. Wir sitzen in Bad Bevensen und nennen den Preis vorab."]),
        ("Der Schlüssel steckt von innen. Geht die Tür trotzdem auf?", ["Ja. Auch mit steckendem Schlüssel öffnen wir die Tür, in den meisten Fällen ohne Schaden. Sag uns das am Telefon, dann bringen wir das passende Werkzeug mit."]),
        ("Was passiert, wenn der Zylinder getauscht werden muss?", ["Dann besprechen wir das vorher mit Dir. Gängige Zylinder haben wir im Fahrzeug, der Einbau erfolgt direkt im selben Termin."]),
        ("Öffnet Ihr in {k} auch Autos?", ["Ja. Pkw und Transporter öffnen wir schonend, wenn der Schlüssel im Fahrzeug liegt. Der Preis entspricht der Türöffnung."]),
    ]
    out = [(speed[0], speed[1][pick(s, "faqspeed", 2)]), (price[0], price[1][pick(s, "faqprice", 2)])]
    start = pick(s, "faq", len(pool))
    chosen = [pool[(start + i * 3) % len(pool)] for i in range(3)]
    seen = set()
    for q, answers in chosen:
        if q in seen:
            continue
        seen.add(q)
        out.append((q, answers[0]))
    return [(q.format(**a), ans.format(**a)) for q, ans in out[:5]]


def einsatz_text(o):
    return variant(o["slug"], "gebiet", [
        "Als mobiler <strong>Schlüsselnotdienst aus Bad Bevensen</strong> ({strasse}) sind wir täglich im Landkreis Uelzen, im Landkreis Lüneburg und im Wendland unterwegs, bei Bedarf bis Munster, Faßberg und Celle. Der Umkreis liegt bei etwa 80 km. Wähle Deinen Ort:",
        "Unser Standort ist <strong>Bad Bevensen</strong>. Von dort bedienen wir den Landkreis Uelzen, den Landkreis Lüneburg und den Landkreis Lüchow-Dannenberg sowie Teile des Heidekreises und des Landkreises Celle. Hier findest Du alle Orte mit Anfahrtszeit und Preis:",
        "Rund 80 Kilometer um <strong>Bad Bevensen</strong> sind wir im Einsatz, von Lüneburg bis Celle und von Munster bis ins Wendland. Jeder Ort hat eine eigene Seite mit Festpreis und Anfahrtszeit:",
    ], **fmt_args(o))


def nachbarn_links(o):
    return [(ORTE[n]["name"], f"{DOMAIN}/{n}") for n in o["nachbarn"] if n in ORTE]


# ---------------------------------------------------------------- Strukturierte Daten
def jsonld(o):
    k = kurz(o)
    f = faq(o)
    data = [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "@id": f"{DOMAIN}/{o['slug']}#service",
            "name": f"Schlüsseldienst {k}: Türöffnung und Schlüsselnotdienst",
            "serviceType": "Schlüsselnotdienst, Türöffnung",
            "url": f"{DOMAIN}/{o['slug']}",
            "description": desc_for(o),
            "provider": {"@id": f"{DOMAIN}/#locksmith"},
            "areaServed": {"@type": "City", "name": k, "address": {"@type": "PostalAddress", "addressLocality": k, "postalCode": o.get("plz", ""), "addressRegion": "Niedersachsen", "addressCountry": "DE"}},
            "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": B["telefon_e164"], "contactType": "customer service", "availableLanguage": "de"}},
            "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"},
            "offers": {"@type": "Offer", "name": f"Türöffnung {k} zum Festpreis", "price": o["preis_tueroeffnung"], "priceCurrency": "EUR", "description": "Festpreis inkl. Anfahrt und MwSt. (Montag bis Freitag, 8 bis 18 Uhr); nachts, am Wochenende und an Feiertagen plus 54 €", "availability": "https://schema.org/InStock", "areaServed": k},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": f"Schlüsseldienst {k}", "item": f"{DOMAIN}/{o['slug']}"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in f],
        },
    ]
    return "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n</script>' for x in data)


# ---------------------------------------------------------------- Prüfungen
BANNED = ["–", "—", "nicht nur", "Experten sagen", "Experten empfehlen", "Fachleute raten"]


def check_text(text, where):
    for b in BANNED:
        if b in text:
            raise ValueError(f"unerwünschte Wendung {b!r} in {where}: {text[:80]!r}")
    return text


def all_texts(o):
    """Alle sichtbaren Texte einer Ortsseite als Liste (für Prüfungen und Ähnlichkeitsvergleich)."""
    t = [title_for(o), desc_for(o), hero_h1(o), hero_h2(o), *hero_lines(o), hero_alt(o), einsatz_header(o), preisplan_header(o), intro(o), lokal_abschnitt(o), preise(o), einsatz_text(o)]
    t += [x for _, x in vorteile(o)] + list(headings(o).values()) + ablauf(o)
    t += [f"{n} {x}" for n, x in leistungen(o)] + [f"{q} {a}" for q, a in faq(o)]
    return t


# ---------------------------------------------------------------- Dokumentation (Markdown je Ort)
def render(o):
    k = kurz(o)
    t, d = title_for(o), desc_for(o)
    url = f"{DOMAIN}/{o['slug']}"
    H = headings(o)
    L = [f"# {o['name']}: SEO-Inhalte für `/{o['slug']}`\n"]
    if o.get("pruefen"):
        L.append(f"> Bitte prüfen: {o['pruefen']}\n")
    L.append("## 1. SEO-Felder\n")
    L.append("| Feld | Wert | Länge |\n|---|---|---|")
    L.append(f"| URL | `{o['slug']}` | |")
    L.append(f"| Seitentitel | {t} | {len(t)} |")
    L.append(f"| Beschreibung | {d} | {len(d)} |")
    L.append(f"| Keywords | {keywords(o)} | |")
    L.append(f"| Preis Türöffnung | {o['preis_tueroeffnung']} € | |\n")
    L.append("## 2. Texte\n")
    L.append(f"### H1\n{hero_h1(o)}\n\n### H2\n{hero_h2(o)}\n\n**Hero-Text:** " + " / ".join(hero_lines(o)) + "\n")
    L.append("### Vorteile\n")
    for title, body in vorteile(o):
        L.append(f"- **{title}**: " + body.replace("\n", " "))
    L.append("")
    L.append(f"### Abschnittstitel\n{einsatz_header(o)}\n\n### Einleitung\n{intro(o)}\n\n### Lokal\n{lokal_abschnitt(o)}\n")
    L.append(f"### {H['preis']}\n{preise(o)}\n")
    L.append(f"### {H['ablauf']}\n")
    for i, s in enumerate(ablauf(o), 1):
        L.append(f"{i}. {s}")
    L.append("")
    L.append(f"### {H['leistungen']}\n")
    for name, txt in leistungen(o):
        L.append(f"- **{name}**: {txt}")
    L.append("")
    L.append(f"### {H['faq']}\n")
    for q, a in faq(o):
        L.append(f"**{q}**  \n{a}\n")
    L.append(f"### {H['nah']}\n")
    for name, link in nachbarn_links(o):
        L.append(f"- [Schlüsseldienst {name}]({link})")
    L.append(f"\n### {H['gebiet']}\n{einsatz_text(o).replace('<strong>', '').replace('</strong>', '')}\n")
    L.append("## 3. Strukturierte Daten\n")
    L.append("```html\n" + jsonld(o) + "\n```\n")
    L.append(f"## 4. Prüfen\n\n1. `{url}` öffnen und Titel sowie Description im Quelltext prüfen.\n2. https://search.google.com/test/rich-results?url={url}\n3. Search Console: URL prüfen und Indexierung beantragen.\n")
    return "\n".join(L)


def main():
    rows = []
    for o in D["orte"]:
        for x in all_texts(o) + [jsonld(o)]:
            check_text(x, o["slug"])
        open(os.path.join(OUT, f"{o['slug']}.md"), "w", encoding="utf-8").write(render(o))
        k = kurz(o)
        rows.append([o["slug"], f"{DOMAIN}/{o['slug']}", f"Schlüsseldienst {k}", keywords(o), title_for(o), len(title_for(o)), desc_for(o), len(desc_for(o)), str(o["preis_tueroeffnung"])])

    with open(os.path.join(HERE, "..", "05-keyword-map.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["slug", "url", "haupt_keyword", "neben_keywords", "title", "title_len", "description", "desc_len", "preis"])
        w.writerow(["(home)", DOMAIN + "/", "Schlüsselnotdienst Bad Bevensen, Uelzen, Lüneburg", "Schlüsseldienst Bad Bevensen; Schlüsseldienst Uelzen; Schlüsseldienst Lüneburg; Türöffnung Festpreis; Schlüsselnotdienst 24h Landkreis Uelzen", "Schlüsselnotdienst Bad Bevensen · Uelzen · Lüneburg 24/7", 56, "Schlüsseldienst für Bad Bevensen, Uelzen, Lüneburg und Umgebung: Türöffnung ab 115 € Festpreis, ohne Schaden, rund um die Uhr erreichbar. ☎ 05821 4049049", 153, "115"])
        w.writerow(["turoffnung", DOMAIN + "/turoffnung", "Türöffnung Kosten", "Was kostet eine Türöffnung; Türöffnung Festpreis; Schlüsseldienst Preise; seriöser Schlüsseldienst erkennen", "Was kostet eine Türöffnung? Festpreise & Ablauf", 47, "Was kostet eine Türöffnung? 115 € in Bad Bevensen, im Umland 135 bis 260 € je nach Entfernung. Festpreis inkl. Anfahrt, ohne Schaden, rund um die Uhr.", 150, "115 bis 260"])
        w.writerows(rows)

    with open(os.path.join(HERE, "..", "06-interne-verlinkung.md"), "w", encoding="utf-8") as f:
        f.write("# Interne Verlinkung\n\n")
        f.write("## Startseite, Abschnitt „Unser Einsatzgebiet“\n\nJede Kachel ist ein Link auf die Ortsseite (Anker `#einsatzgebiet`).\n\n")
        for s in ["bad-bevensen", "uelzen", "lueneburg", "bienenbuettel", "altenmedingen", "barum", "himbergen", "ebstorf", "wriedel", "melbeck", "adendorf", "barendorf", "dahlenburg", "amelinghausen", "bleckede", "rosche", "suderburg", "wieren", "bad-bodenteich", "zernien", "dannenberg", "hitzacker", "luechow", "munster", "fassberg", "eschede", "celle", "bavendorf"]:
            f.write(f"- Schlüsseldienst {ORTE[s]['name']} → `/{s}`\n")
        f.write("\n## Ortsseiten, Abschnitt „in der Nähe“\n\n| Seite | verlinkt auf |\n|---|---|\n")
        for o in D["orte"]:
            f.write(f"| /{o['slug']} | " + ", ".join(f"/{n}" for n in o["nachbarn"]) + ", /turoffnung, / |\n")
        f.write("\n## Footer (alle Seiten)\n\n- Startseite, Türöffnung & Preise, Einsatzgebiete (intern)\n- Impressum, Datenschutzerklärung, AGB → provision-infra.de\n")

    print(f"{len(D['orte'])} Seiten geschrieben nach {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
