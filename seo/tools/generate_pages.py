#!/usr/bin/env python3
"""Erzeugt aus orte.json fertige SEO-Inhalte (Markdown) für jede Orts-Unterseite.

Aufruf:  python3 seo/tools/generate_pages.py
Ausgabe: seo/seiten/<slug>.md, seo/05-keyword-map.csv, seo/06-interne-verlinkung.md
"""
import json, csv, os, hashlib, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "seiten")
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(HERE, "orte.json"), encoding="utf-8"))
B = D["basis"]
ORTE = {o["slug"]: o for o in D["orte"]}
DOMAIN = B["domain"]
TEL = B["telefon_anzeige"]


def pick(slug, salt, n):
    return int(hashlib.md5(f"{slug}:{salt}".encode()).hexdigest(), 16) % n


def kurz(o):
    return o.get("name_kurz", o["name"])


def title_for(o):
    k = kurz(o)
    cands = [
        f"Schlüsseldienst {k} – 24h Notdienst zum Festpreis | Baumann",
        f"Schlüsseldienst {k} – Notdienst 24/7, Festpreis | Baumann",
        f"Schlüsseldienst {k} – 24h Notdienst zum Festpreis",
        f"Schlüsseldienst {k} – Türöffnung 24/7 | Baumann",
        f"Schlüsseldienst {k} 24h – Baumann",
    ]
    for c in cands:
        if len(c) <= 60:
            return c
    return cands[-1]


def desc_for(o):
    k = kurz(o)
    eta = o["eta"]
    v = pick(o["slug"], "desc", 3)
    cands = {
        0: f"Ausgesperrt in {k}? Schlüsselnotdienst Baumann öffnet Deine Tür zerstörungsfrei – Festpreis vorab am Telefon, keine Anfahrtskosten, 24/7, in ca. {eta} Min. vor Ort. ☎ {TEL}",
        1: f"Schlüsseldienst {k}: Türöffnung zum Festpreis, 24 Stunden Notdienst, keine versteckten Kosten. In ca. {eta} Min. bei Dir. Jetzt anrufen: {TEL}",
        2: f"Schlüsselnotdienst für {k} & Umgebung: zerstörungsfreie Türöffnung, Festpreis am Telefon, Bar/Karte/PayPal, 24/7 erreichbar. Ca. {eta} Min. Anfahrt. ☎ {TEL}",
    }
    d = cands[v]
    if len(d) > 155:
        d = cands[1]
    return d


def intro(o):
    k, eta = kurz(o), o["eta"]
    v = pick(o["slug"], "intro", 4)
    kreis = o["kreis"]
    sg = o.get("samtgemeinde")
    lage = f"{k} ({o['art']}, {kreis}" + (f", {sg})" if sg else ")")
    if o["slug"] == "bad-bevensen":
        return (
            f"Du stehst in Bad Bevensen vor verschlossener Tür? Dann ist Hilfe besonders nah: Der Schlüsselnotdienst Baumann hat seinen Sitz in der {B['strasse']} in Bad Bevensen. "
            f"Wir sind der Schlüsseldienst vor Ort – kein Callcenter, keine Vermittlung, sondern Jannes Heino Baumann und sein Team aus der Kurstadt selbst. "
            f"In der Regel sind wir innerhalb von {eta} Minuten bei Dir: in der Innenstadt, im Kurviertel, in Medingen, Groß und Klein Hesebeck, Jastorf, Seedorf, Gollern, Röbbel oder Sasendorf. "
            f"Die Türöffnung erfolgt in über 90 % der Fälle zerstörungsfrei – zum Festpreis, den Du vorab am Telefon erfährst."
        )
    texte = [
        f"Ausgesperrt in {k}? Schlüssel abgebrochen, verloren oder innen stecken geblieben? Der Schlüsselnotdienst Baumann aus Bad Bevensen ist Dein Schlüsseldienst für {lage}. "
        f"Wir sind rund um die Uhr erreichbar und in der Regel in etwa {eta} Minuten bei Dir vor Ort. Der Preis für die Türöffnung steht vorher fest – Du erfährst ihn am Telefon, bevor wir losfahren.",
        f"Der Schlüsseldienst für {lage}: Wenn die Tür zugefallen ist oder das Schloss klemmt, hilft der Schlüsselnotdienst Baumann – 24 Stunden am Tag, auch nachts, am Wochenende und an Feiertagen. "
        f"Von unserem Standort in Bad Bevensen sind wir in rund {eta} Minuten in {k}. Wir öffnen zerstörungsfrei, zum Festpreis und ohne versteckte Anfahrtskosten.",
        f"Schnelle Hilfe statt Abzocke: In {k} und Umgebung ist der Schlüsselnotdienst Baumann Dein seriöser Ansprechpartner für Türöffnungen, Schlosswechsel und Einbruchschutz. "
        f"Als regionaler Betrieb aus Bad Bevensen ({kreis}) nennen wir Dir den Festpreis vorab am Telefon und sind in etwa {eta} Minuten bei Dir – Tag und Nacht.",
        f"Tür zu, Schlüssel drinnen – und das ausgerechnet in {k}? Kein Problem. Der Schlüsselnotdienst Baumann ist der Schlüsseldienst für {lage} und erreicht Dich von Bad Bevensen aus in rund {eta} Minuten. "
        f"Wir arbeiten zerstörungsfrei, transparent und zum vorher vereinbarten Festpreis – ohne Aufschläge für die Anfahrt.",
    ]
    return texte[v]


def lokal_abschnitt(o):
    k = kurz(o)
    teile = o.get("ortsteile") or []
    s = o["lokal"] + " "
    if teile and o["slug"] != "bad-bevensen":
        liste = ", ".join(teile[:-1]) + f" und {teile[-1]}" if len(teile) > 1 else teile[0]
        s += f"Wir kommen in alle Stadt- und Ortsteile – darunter {liste}. "
    v = pick(o["slug"], "lokal", 3)
    s += [
        f"Als mobiler Schlüsseldienst haben wir das komplette Werkzeug und gängige Profilzylinder im Fahrzeug dabei, sodass wir die meisten Aufträge in {k} direkt vor Ort abschließen können.",
        f"Weil wir aus der Region kommen, kennen wir die Wege in und um {k} – das spart Zeit, wenn es wirklich eilt.",
        f"Unser Einsatzfahrzeug ist so ausgestattet, dass wir in {k} nicht nur Türen öffnen, sondern bei Bedarf sofort einen neuen Schließzylinder einbauen können.",
    ][v]
    return s


def leistungen(o):
    k = kurz(o)
    return [
        ("Türöffnung", f"Zerstörungsfreie Öffnung von Wohnungs-, Haus- und Zimmertüren in {k} – zugefallen oder abgeschlossen. Festpreis inkl. Anfahrt, nachts/Wochenende/Feiertag mit vorher genanntem Zuschlag."),
        ("Fensteröffnung", "Öffnung gekippter oder zugefallener Fenster und Terrassentüren ohne Beschädigung."),
        ("Fahrzeugöffnung", f"Autoschlüssel eingeschlossen? Wir öffnen abgeschlossene Fahrzeuge in {k} schonend und schnell."),
        ("Schließzylinder & Schlösser", "Austausch und Reparatur von Profilzylindern, Einbau von Sicherheitszylindern mit Sicherungskarte – hochwertige Zylinder haben wir vorrätig."),
        ("Schließanlagen & Zutrittssysteme", "Planung und Montage von Schließanlagen und digitalen Zutrittslösungen (u. a. SimonsVoss, EVVA) für Mehrfamilienhäuser, Praxen, Vereine und Betriebe."),
        ("Einbruchschutz & Sicherheitsberatung", f"Kostenlose Beratung vor Ort in {k}: Beschläge, Zusatzschlösser, Panzerriegel und Tipps, wie Du Dein Zuhause sicherer machst."),
    ]


def preise(o):
    k = kurz(o)
    v = pick(o["slug"], "preis", 3)
    return [
        f"Bei uns gibt es keine Überraschungen auf der Rechnung. Du bekommst den Festpreis für Deine Türöffnung in {k} am Telefon genannt – inklusive Anfahrt und Mehrwertsteuer. "
        "Nachts, am Wochenende und an Feiertagen gilt ein fester Zuschlag, den wir Dir ebenfalls vorher sagen. Nur wenn Material nötig ist (z. B. ein neuer Zylinder), kommen Materialkosten dazu – auch das besprechen wir vor dem Einbau. "
        "Zahlen kannst Du bar, mit EC- oder Kreditkarte oder per PayPal.",
        f"Die Verbraucherzentrale hält für eine Türöffnung tagsüber Gesamtpreise im unteren dreistelligen Bereich für angemessen – genau in diesem Rahmen bewegen wir uns in {k}. "
        "Den konkreten Festpreis erfährst Du vor der Auftragserteilung am Telefon. Es gibt keine getrennten Anfahrtskosten, keinen Aufschlag für „schwierige“ Öffnungen und keine Barzahlungspflicht: Karte und PayPal sind genauso möglich.",
        f"Transparenz ist für uns Pflicht: Festpreis am Telefon, Anfahrt nach {k} inklusive, Zuschlag für Nacht/Wochenende/Feiertag vorher benannt. "
        "Du entscheidest erst, wenn Du den Preis kennst. Bezahlt wird nach der Arbeit – bar, mit Karte oder per PayPal, für Geschäftskunden auch auf Rechnung.",
    ][v]


def ablauf(o):
    k = kurz(o)
    return [
        f"**Anruf:** Du rufst uns an ({TEL}). Wir fragen kurz nach Türart und Situation und nennen Dir den Festpreis und die voraussichtliche Ankunftszeit in {k}.",
        "**Anfahrt:** Wir fahren sofort los – in der Regel bist Du nach rund {eta} Minuten wieder drin.".format(eta=o["eta"]),
        "**Berechtigung:** Vor Ort prüfen wir, dass Du zur Wohnung oder zum Haus gehörst (Ausweis, Mietvertrag oder rechtsverbindliche Versicherung).",
        "**Öffnung:** Mit Profiwerkzeug öffnen wir die Tür in über 90 % der Fälle zerstörungsfrei. Falls doch ein Zylinder getauscht werden muss, haben wir Ersatz dabei.",
        "**Bezahlung:** Du zahlst den vorher genannten Preis – bar, mit Karte oder PayPal – und bekommst eine Quittung bzw. Rechnung.",
    ]


def faq(o):
    k, eta = kurz(o), o["eta"]
    pool = [
        (f"Wie schnell ist der Schlüsseldienst in {k} vor Ort?",
         f"Von unserem Standort in Bad Bevensen brauchen wir nach {k} in der Regel etwa {eta} Minuten. Die genaue Ankunftszeit nennen wir Dir am Telefon."),
        (f"Was kostet eine Türöffnung in {k}?",
         "Den Festpreis erfährst Du vor dem Auftrag am Telefon – inklusive Anfahrt und MwSt. Nachts, am Wochenende und an Feiertagen gilt ein fester, vorher genannter Zuschlag. Es gibt keine versteckten Kosten."),
        ("Wird meine Tür beim Öffnen beschädigt?",
         "In über 90 % der Fälle öffnen wir zerstörungsfrei. Bei zugefallenen Türen ist das fast immer möglich; bei abgeschlossenen Türen informieren wir Dich vorher, falls ein Zylinder getauscht werden muss."),
        (f"Ist der Schlüsselnotdienst in {k} auch nachts und am Wochenende erreichbar?",
         f"Ja, wir sind 24 Stunden am Tag, 7 Tage die Woche erreichbar – auch an Feiertagen. Ruf einfach an: {TEL}."),
        ("Muss ich mich ausweisen?",
         "Ja, wir öffnen nur für Berechtigte. Hast Du Deinen Ausweis gerade nicht dabei, kannst Du ihn im Nachgang zeigen oder Deine Berechtigung rechtsverbindlich versichern. Details stehen in unseren AGB."),
        ("Kann ich mit Karte oder PayPal bezahlen?",
         "Ja. Neben Barzahlung akzeptieren wir EC- und Kreditkarte sowie PayPal direkt vor Ort. Geschäftskunden können auch auf Rechnung zahlen."),
        (f"Woran erkenne ich einen seriösen Schlüsseldienst in {k}?",
         "An einem festen Preis vor Auftragserteilung, einer regionalen Adresse im Impressum, einer Festnetznummer und daran, dass keine Barzahlung erzwungen wird. All das findest Du bei uns – wir sitzen in Bad Bevensen und sind seit Jahren in der Region tätig."),
    ]
    start = pick(o["slug"], "faq", len(pool))
    idx = [0, 1] + [(start + i) % len(pool) for i in range(2, 6)]
    seen, out = set(), []
    for i in idx:
        if i not in seen:
            seen.add(i)
            out.append(pool[i])
    return out[:5]


def nachbarn_links(o):
    return [(ORTE[n]["name"], f"{DOMAIN}/{n}") for n in o["nachbarn"] if n in ORTE]


def jsonld(o):
    k = kurz(o)
    f = faq(o)
    data = [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "@id": f"{DOMAIN}/{o['slug']}#service",
            "name": f"Schlüsseldienst {k} – Türöffnung & Schlüsselnotdienst",
            "serviceType": "Schlüsselnotdienst / Türöffnung",
            "url": f"{DOMAIN}/{o['slug']}",
            "description": desc_for(o),
            "provider": {"@id": f"{DOMAIN}/#locksmith"},
            "areaServed": {"@type": "City", "name": k, "address": {"@type": "PostalAddress", "addressLocality": k, "postalCode": o.get("plz", ""), "addressRegion": "Niedersachsen", "addressCountry": "DE"}},
            "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": B["telefon_e164"], "contactType": "customer service", "availableLanguage": "de"}},
            "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"},
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


def render(o):
    k = kurz(o)
    t, d = title_for(o), desc_for(o)
    url = f"{DOMAIN}/{o['slug']}"
    L = []
    L.append(f"# {o['name']} – SEO-Inhalte für `/{o['slug']}`\n")
    if o.get("neu"):
        L.append("> **Neue Seite** – existiert noch nicht in OnePage. Seite anlegen (Vorlage: eine bestehende Ortsseite duplizieren), Slug exakt wie oben setzen.\n")
    if o.get("pruefen"):
        L.append(f"> ⚠️ **Bitte prüfen:** {o['pruefen']}\n")
    L.append("## 1. Seiten-Einstellungen → SEO (OnePage: Seite öffnen → Einstellungen → SEO)\n")
    L.append("| Feld | Wert | Länge |\n|---|---|---|")
    L.append(f"| URL / Slug | `{o['slug']}` | |")
    L.append(f"| Seitentitel (Page Title) | {t} | {len(t)} |")
    L.append(f"| Beschreibung (Description) | {d} | {len(d)} |")
    L.append(f"| Keywords | Schlüsseldienst {k}, Schlüsselnotdienst {k}, Türöffnung {k}, Schlüsseldienst {k} 24h, Aufsperrdienst {k}, Schlüsseldienst {k} Kosten | |")
    L.append(f"| Vorschaubild (OG) | Foto Einsatzfahrzeug/Jannes Baumann, 1200×630, Alt-Text: „Schlüsselnotdienst Baumann – Schlüsseldienst in {k}“ | |")
    L.append("| Indexierung | **erlaubt** (an) | |\n")
    L.append("> Hinweis: In **Einstellungen → SEO → Page Title Pattern** muss `{{page_title}}` (ohne Website-Namen) stehen, sonst hängt OnePage „| Schlüsselnotdienst ProVision Infra“ an und der Titel wird zu lang.\n")

    L.append("## 2. Seitenstruktur & Texte\n")
    L.append(f"### H1\nSchlüsseldienst {k} – Schlüsselnotdienst 24/7 zum Festpreis\n")
    L.append(f"**Unterzeile (kein Heading, normaler Text):** Türöffnung in {k} & Umgebung · fair · transparent · in ca. {o['eta']} Min. vor Ort · ☎ {TEL}\n")
    L.append(f"**Button:** „Jetzt anrufen – {TEL}“ (Link `tel:{B['telefon_e164']}`)\n")
    L.append("### Einleitung (direkt unter der H1)\n" + intro(o) + "\n")
    L.append(f"### H2: Schlüsselnotdienst Baumann für {k} – aus der Region, für die Region\n" + lokal_abschnitt(o) + "\n")
    L.append(f"### H2: Unsere Leistungen in {k}\n")
    for name, txt in leistungen(o):
        L.append(f"- **H3: {name}** – {txt}")
    L.append("")
    L.append(f"### H2: Was kostet der Schlüsseldienst in {k}?\n" + preise(o) + "\n")
    L.append(f"### H2: So läuft Deine Türöffnung in {k} ab\n")
    for i, s in enumerate(ablauf(o), 1):
        L.append(f"{i}. {s}")
    L.append("")
    L.append("### H2: Deine Vorteile auf einen Blick\n")
    L.append("- Festpreis vorab am Telefon – keine versteckten Kosten\n- Keine separaten An- und Abfahrtskosten\n- 24/7 erreichbar: nachts, am Wochenende, an Feiertagen\n- In über 90 % der Fälle zerstörungsfreie Öffnung\n- Regionaler Betrieb aus Bad Bevensen mit Festnetznummer und Impressum\n- Bar, EC-/Kreditkarte oder PayPal\n")
    L.append(f"### H2: Häufige Fragen zum Schlüsseldienst in {k}\n")
    for q, a in faq(o):
        L.append(f"**H3: {q}**  \n{a}\n")
    L.append("### H2: Kundenbewertungen\n(bestehenden Bewertungs-Block beibehalten – jede Bewertung nur **einmal**, aktuell sind alle sechs doppelt eingebaut)\n")
    L.append(f"### H2: Schlüsseldienst in der Nähe von {k}\n")
    L.append(f"Wir sind auch in diesen Orten für Dich im Einsatz (jeder Ort als **interner Link**):\n")
    for name, link in nachbarn_links(o):
        L.append(f"- [Schlüsseldienst {name}]({link})")
    L.append(f"- [Alle Einsatzorte & Preise]({DOMAIN}/#einsatzgebiet) · [Infos zur Türöffnung]({DOMAIN}/turoffnung)\n")
    L.append("### Kontaktblock (Footer-Bereich der Seite)\n")
    L.append(f"{B['firma_lang']} · {B['strasse']}, {B['plz']} {B['ort']} · ☎ {TEL} · 24 Stunden erreichbar, 7 Tage die Woche\n")

    L.append("## 3. Bilder (Alt-Texte)\n")
    L.append(f"- Hero-Bild: „Schlüsseldienst Baumann öffnet eine Haustür in {k}“\n- Logo: „Schlüsselnotdienst Baumann – Logo“\n- Fahrzeug/Team: „Mobiler Schlüsselnotdienst Baumann im Einsatz in {k}“\n")

    L.append("## 4. Page Code → `<head>` (OnePage: Code-Symbol links → Spalte „Page Code“ → Bereich `<head>`)\n")
    L.append("```html\n" + jsonld(o) + "\n```\n")
    L.append("## 5. Prüfen nach dem Veröffentlichen\n")
    L.append(f"1. `{url}` im Browser öffnen, Titel/Description im Quelltext prüfen.\n2. https://search.google.com/test/rich-results?url={url} → keine Fehler.\n3. Google Search Console → URL-Prüfung → **Indexierung beantragen**.\n")
    return "\n".join(L)


rows = []
for o in D["orte"]:
    md = render(o)
    open(os.path.join(OUT, f"{o['slug']}.md"), "w", encoding="utf-8").write(md)
    k = kurz(o)
    rows.append([o["slug"], f"{DOMAIN}/{o['slug']}", f"Schlüsseldienst {k}", f"Schlüsselnotdienst {k}; Türöffnung {k}; Schlüsseldienst {k} 24h; Aufsperrdienst {k}; Schlüsseldienst {k} Kosten; Autoöffnung {k}", title_for(o), len(title_for(o)), desc_for(o), len(desc_for(o)), "neu" if o.get("neu") else "bestehend"])

with open(os.path.join(HERE, "..", "05-keyword-map.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["slug", "url", "haupt_keyword", "neben_keywords", "title", "title_len", "description", "desc_len", "status"])
    w.writerow(["(home)", DOMAIN + "/", "Schlüsselnotdienst Bad Bevensen / Uelzen / Lüneburg", "Schlüsseldienst Bad Bevensen; Schlüsseldienst Uelzen Lüneburg; Türöffnung Festpreis; Schlüsselnotdienst 24h Landkreis Uelzen", "Schlüsselnotdienst Baumann – Bad Bevensen, Uelzen, Lüneburg 24/7", 59, "Schlüsseldienst für Bad Bevensen, Uelzen, Lüneburg & Umgebung: Türöffnung zum Festpreis, zerstörungsfrei, 24/7, keine Anfahrtskosten. ☎ 05821 4049049", 150, "bestehend"])
    w.writerow(["turoffnung", DOMAIN + "/turoffnung", "Türöffnung Kosten", "Was kostet eine Türöffnung; Türöffnung Festpreis; Schlüsseldienst Preise; seriöser Schlüsseldienst erkennen", "Was kostet eine Türöffnung? Festpreis & Ablauf | Baumann", 56, "Was darf eine Türöffnung kosten? Faire Preise zwischen 80 und 200 €, Festpreisgarantie am Telefon, zerstörungsfreie Öffnung. So arbeitet der Schlüsselnotdienst Baumann.", 155, "bestehend"])
    w.writerows(rows)

# interne Verlinkung
with open(os.path.join(HERE, "..", "06-interne-verlinkung.md"), "w", encoding="utf-8") as f:
    f.write("# Interne Verlinkung – Linkplan\n\n")
    f.write("Aktuell verweist **keine einzige interne Seite** auf die Ortsseiten (die Ortsliste auf der Startseite ist reiner Text). Google erreicht sie nur über die Sitemap – das ist der Hauptgrund für schwache/fehlende Indexierung.\n\n")
    f.write("## A. Startseite – Abschnitt „Unser Einsatzgebiet“\n\nJede Kachel wird ein Link (in OnePage: Text markieren → Link → interne Seite wählen). Reihenfolge nach Nähe/Relevanz:\n\n")
    order = ["bad-bevensen", "uelzen", "lueneburg", "bienenbuettel", "altenmedingen", "barum", "himbergen", "ebstorf", "wriedel", "melbeck", "adendorf", "barendorf", "dahlenburg", "amelinghausen", "bleckede", "rosche", "suderburg", "wieren", "bad-bodenteich", "zernien", "dannenberg", "hitzacker", "luechow", "munster", "fassberg", "eschede", "celle", "bavendorf"]
    for s in order:
        o = ORTE[s]
        f.write(f"- Schlüsseldienst {o['name']} → `/{s}`\n")
    f.write("\nDem Abschnitt die Anker-ID `einsatzgebiet` geben (Custom attributes → ID), damit `/#einsatzgebiet` funktioniert.\n\n")
    f.write("## B. Jede Ortsseite – Abschnitt „Schlüsseldienst in der Nähe“\n\n| Seite | verlinkt auf |\n|---|---|\n")
    for o in D["orte"]:
        f.write(f"| /{o['slug']} | " + ", ".join(f"/{n}" for n in o["nachbarn"]) + ", /turoffnung, / |\n")
    f.write("\n## C. Footer (Site-weit)\n\n- Impressum → `/impressum` (aktuell extern auf provision-infra.de!)\n- Datenschutz → `/datenschutzerklarung` (aktuell extern)\n- AGB → `/agb` (aktuell extern)\n- Türöffnung & Preise → `/turoffnung`\n- Kurze Ortsliste: Bad Bevensen · Uelzen · Lüneburg · Bienenbüttel · Ebstorf · Dannenberg · Celle (je Link)\n\n## D. Navigation\n\n- „Einsatzgebiete“ → `/#einsatzgebiet` (Anker auf der Startseite)\n- „Türöffnung & Preise“ → `/turoffnung`\n- „Geschäftskunden“ nur anzeigen, wenn die Seite wieder existiert (aktuell 404)\n\n## E. Kaputte Links entfernen/ersetzen\n\n- `/geschaftskunden` (404) – auf AGB, Datenschutz, Impressum, Türöffnung verlinkt\n- `/simonsvosstechnologies` (404) – im Footer von Türöffnung/AGB\n")

print(f"{len(D['orte'])} Seiten geschrieben nach {os.path.abspath(OUT)}")
