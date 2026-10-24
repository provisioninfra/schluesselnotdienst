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
        f"Schlüsseldienst {k}: 24h Notdienst zum Festpreis",
        f"Schlüsseldienst {k}: Notdienst zum Festpreis",
        f"Schlüsseldienst {k} 24h",
    ]
    for c in cands:
        if len(c) <= 60:
            return c
    return cands[-1]


def desc_for(o):
    k, eta, p = kurz(o), o["eta"], o["preis_tueroeffnung"]
    v = pick(o["slug"], "desc", 3)
    cands = [
        f"Ausgesperrt in {k}? Wir öffnen Deine Tür ohne Schaden, Festpreis {p} € inkl. Anfahrt. Tag und Nacht erreichbar, in etwa {eta} Minuten vor Ort. ☎ {TEL}",
        f"Schlüsseldienst {k}: Türöffnung für {p} € inkl. Anfahrt und MwSt., rund um die Uhr erreichbar, in etwa {eta} Minuten bei Dir. ☎ {TEL}",
        f"Schlüsselnotdienst für {k} und Umgebung: Türöffnung zum Festpreis von {p} €, 24 Stunden erreichbar, in etwa {eta} Minuten vor Ort. ☎ {TEL}",
    ]
    order = [cands[v]] + [c for i, c in enumerate(cands) if i != v]
    for d in order:
        if len(d) <= 155:
            return d
    return f"Schlüsseldienst {k}: Türöffnung für {p} € inkl. Anfahrt, Tag und Nacht erreichbar, in etwa {eta} Minuten bei Dir. ☎ {TEL}"


def intro(o):
    k, eta = kurz(o), o["eta"]
    v = pick(o["slug"], "intro", 4)
    sg = o.get("samtgemeinde")
    lage = f"{k} ({o['art']}, {o['kreis']}" + (f", {sg})" if sg else ")")
    if o["slug"] == "bad-bevensen":
        return (
            "Du stehst in Bad Bevensen vor verschlossener Tür? Dann ist Hilfe nah. Der ProVision Infra Schlüsselnotdienst hat seinen Sitz in der "
            f"{B['strasse']}, mitten in der Kurstadt. Kein Callcenter und keine Vermittlung, sondern Jannes Heino Baumann und sein Team. "
            f"Meist sind wir innerhalb von {eta} Minuten bei Dir, in der Innenstadt, im Kurviertel oder in den Ortsteilen von Medingen bis Seedorf. "
            f"Die Öffnung gelingt in über 90 Prozent der Fälle ohne Schaden, zum Festpreis von {o['preis_tueroeffnung']} €."
        )
    texte = [
        f"Die Tür ist zu und der Schlüssel liegt drinnen? In {k} hilft der ProVision Infra Schlüsselnotdienst aus Bad Bevensen. "
        f"Wir sind Tag und Nacht erreichbar und brauchen bis zu Dir etwa {eta} Minuten. Was die Öffnung kostet, sagen wir Dir am Telefon, bevor wir losfahren.",
        f"Der Schlüsseldienst für {lage}. Wenn die Tür zugefallen ist oder das Schloss klemmt, kommt der ProVision Infra Schlüsselnotdienst, auch nachts, am Wochenende und an Feiertagen. "
        f"Von Bad Bevensen aus sind wir in rund {eta} Minuten in {k}. Geöffnet wird zum vorher genannten Festpreis, Anfahrtskosten gibt es nicht.",
        f"In {k} und Umgebung ist der ProVision Infra Schlüsselnotdienst Dein Ansprechpartner für Türöffnungen, Schlosswechsel und Einbruchschutz. "
        f"Der Betrieb sitzt in Bad Bevensen im Landkreis Uelzen. Der Festpreis steht vor der Anfahrt fest, und nach etwa {eta} Minuten stehen wir vor Deiner Tür.",
        f"Ausgesperrt in {k}? Das lässt sich schnell lösen. Der ProVision Infra Schlüsselnotdienst erreicht {k} von Bad Bevensen aus in rund {eta} Minuten "
        f"und öffnet Deine Tür in den meisten Fällen ohne jeden Schaden. Den Preis kennst Du vorher, einen Aufschlag für die Anfahrt gibt es nicht.",
    ]
    return texte[v]


def lokal_abschnitt(o):
    k = kurz(o)
    teile = o.get("ortsteile") or []
    s = o["lokal"] + " "
    if teile and o["slug"] != "bad-bevensen":
        liste = ", ".join(teile[:-1]) + f" und {teile[-1]}" if len(teile) > 1 else teile[0]
        s += f"Wir kommen in alle Stadt- und Ortsteile, darunter {liste}. "
    v = pick(o["slug"], "lokal", 3)
    s += [
        f"Im Fahrzeug haben wir das komplette Werkzeug und gängige Profilzylinder dabei. Die meisten Aufträge in {k} erledigen wir deshalb in einem Termin.",
        f"Weil wir aus der Region kommen, kennen wir die Wege nach {k}. Das spart Zeit, wenn es eilt.",
        f"Unser Einsatzfahrzeug ist so bestückt, dass wir in {k} eine Tür öffnen und bei Bedarf gleich einen neuen Zylinder einbauen können.",
    ][v]
    return s


def leistungen(o):
    k = kurz(o)
    return [
        ("Türöffnung", f"Wohnungs-, Haus- und Zimmertüren in {k}, zugefallen oder abgeschlossen. Festpreis inklusive Anfahrt; nachts, am Wochenende und an Feiertagen mit vorher genanntem Zuschlag."),
        ("Fensteröffnung", "Gekippte oder zugefallene Fenster und Terrassentüren öffnen wir ohne Beschädigung."),
        ("Fahrzeugöffnung", f"Autoschlüssel eingeschlossen? Wir öffnen abgeschlossene Fahrzeuge in {k} schonend."),
        ("Schließzylinder und Schlösser", "Austausch und Reparatur von Profilzylindern, Einbau von Sicherheitszylindern mit Sicherungskarte. Hochwertige Zylinder haben wir vorrätig."),
        ("Schließanlagen und Zutrittssysteme", "Planung und Montage von Schließanlagen und digitalen Zutrittslösungen, zum Beispiel von SimonsVoss oder EVVA, für Mehrfamilienhäuser, Praxen und Betriebe."),
        ("Einbruchschutz", f"Beratung bei Dir vor Ort in {k}: Beschläge, Zusatzschlösser, Panzerriegel und ein Blick auf Fenster und Nebeneingänge."),
    ]


def preise(o):
    k = kurz(o)
    v = pick(o["slug"], "preis", 3)
    p = o["preis_tueroeffnung"]
    konkret = (f" Konkret: Die Türöffnung in {k} kostet montags bis freitags von 8 bis 18 Uhr {p} €, inklusive Anfahrt und Mehrwertsteuer. "
               "Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Fenster- und Fahrzeugöffnung kosten dasselbe. Der Austausch eines Profilzylinders beginnt bei 60 € zuzüglich Material.")
    return [x + konkret for x in [
        f"Du bekommst den Festpreis für Deine Türöffnung in {k} am Telefon genannt, inklusive Anfahrt und Mehrwertsteuer. "
        "Nachts, am Wochenende und an Feiertagen gilt ein fester Zuschlag, den wir Dir ebenfalls vorher sagen. Nur wenn Material nötig ist, etwa ein neuer Zylinder, kommen Materialkosten dazu. "
        "Zahlen kannst Du bar, mit EC- oder Kreditkarte oder per PayPal.",
        f"Für eine Türöffnung am Tag hält die Verbraucherzentrale Gesamtpreise im unteren dreistelligen Bereich für angemessen. In diesem Rahmen bewegen wir uns in {k}. "
        "Den konkreten Preis erfährst Du vor der Auftragserteilung. Es gibt keine getrennten Anfahrtskosten und keinen Aufschlag für schwierige Öffnungen. Barzahlung ist keine Pflicht, Karte und PayPal gehen genauso.",
        f"Festpreis am Telefon, Anfahrt nach {k} inklusive, Zuschlag für Nacht, Wochenende und Feiertag vorher benannt. "
        "Du entscheidest erst, wenn Du den Preis kennst. Bezahlt wird nach der Arbeit, bar, mit Karte oder per PayPal; Geschäftskunden auch auf Rechnung.",
    ]][v]


def ablauf(o):
    k = kurz(o)
    return [
        f"**Anruf:** Du rufst an unter {TEL}. Wir fragen nach Türart und Situation und nennen Dir Festpreis und Ankunftszeit.",
        f"**Anfahrt:** Wir fahren sofort los. Nach etwa {o['eta']} Minuten sind wir in {k}.",
        "**Berechtigung:** Vor Ort zeigst Du uns Deinen Ausweis oder einen anderen Nachweis, dass Du hier wohnst.",
        "**Öffnung:** Mit Spezialwerkzeug öffnen wir die Tür, in über 90 Prozent der Fälle ohne Schaden. Falls ein Zylinder getauscht werden muss, haben wir Ersatz dabei.",
        "**Bezahlung:** Du zahlst den vorher genannten Preis, bar, mit Karte oder per PayPal, und bekommst eine Quittung oder Rechnung.",
    ]


def faq(o):
    k, eta, p = kurz(o), o["eta"], o["preis_tueroeffnung"]
    pool = [
        (f"Wie schnell ist der Schlüsseldienst in {k} vor Ort?",
         f"Von Bad Bevensen nach {k} brauchen wir in der Regel etwa {eta} Minuten. Die genaue Ankunftszeit nennen wir Dir am Telefon."),
        (f"Was kostet eine Türöffnung in {k}?",
         f"Montags bis freitags von 8 bis 18 Uhr {p} €, inklusive Anfahrt und Mehrwertsteuer. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Den Preis bestätigen wir Dir vor dem Auftrag am Telefon."),
        ("Wird meine Tür beim Öffnen beschädigt?",
         "In über 90 Prozent der Fälle öffnen wir ohne Schaden. Bei zugefallenen Türen gelingt das fast immer. Ist die Tür abgeschlossen, sagen wir Dir vorher, falls ein Zylinder getauscht werden muss."),
        (f"Ist der Schlüsselnotdienst in {k} auch nachts und am Wochenende erreichbar?",
         f"Ja, an jedem Tag und zu jeder Uhrzeit, auch an Feiertagen. Ruf einfach an: {TEL}."),
        ("Muss ich mich ausweisen?",
         "Ja, wir öffnen nur für Berechtigte. Hast Du Deinen Ausweis gerade nicht dabei, kannst Du ihn im Nachgang zeigen oder Deine Berechtigung schriftlich versichern. Die Details stehen in unseren AGB."),
        ("Kann ich mit Karte oder PayPal bezahlen?",
         "Ja. Neben Barzahlung akzeptieren wir EC- und Kreditkarte sowie PayPal direkt vor Ort. Geschäftskunden können auf Rechnung zahlen."),
        (f"Woran erkenne ich einen seriösen Schlüsseldienst in {k}?",
         "An einem festen Gesamtpreis vor dem Auftrag, einer Adresse in der Region, einer Festnetznummer und daran, dass niemand Barzahlung erzwingt. Wir sitzen in Bad Bevensen und arbeiten seit Jahren in der Region."),
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
            "offers": {"@type": "Offer", "name": f"Türöffnung {k} zum Festpreis", "price": o["preis_tueroeffnung"], "priceCurrency": "EUR", "description": "Festpreis inkl. Anfahrt und MwSt. (Mo–Fr 08:00–18:00 Uhr); nachts, am Wochenende und an Feiertagen + 54 €", "availability": "https://schema.org/InStock", "areaServed": k},
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
    L.append(f"| Vorschaubild (OG) | Foto Einsatzfahrzeug/Jannes Baumann, 1200×630, Alt-Text: „ProVision Infra Schlüsselnotdienst – Schlüsseldienst in {k}“ | |")
    L.append("| Indexierung | **erlaubt** (an) | |\n")
    L.append("> Hinweis: In **Einstellungen → SEO → Page Title Pattern** muss `{{page_title}}` (ohne Website-Namen) stehen, sonst hängt OnePage „| Schlüsselnotdienst ProVision Infra“ an und der Titel wird zu lang.\n")

    L.append("## 2. Seitenstruktur & Texte\n")
    L.append(f"### H1\nSchlüsseldienst {k}: Notdienst rund um die Uhr zum Festpreis\n")
    L.append(f"**Unterzeile (kein Heading, normaler Text):** Türöffnung in {k} & Umgebung · fair · transparent · in ca. {o['eta']} Min. vor Ort · ☎ {TEL}\n")
    L.append(f"**Button:** „Jetzt anrufen – {TEL}“ (Link `tel:{B['telefon_e164']}`)\n")
    L.append("### Einleitung (direkt unter der H1)\n" + intro(o) + "\n")
    L.append(f"### H2: ProVision Infra Schlüsselnotdienst für {k} – aus der Region, für die Region\n" + lokal_abschnitt(o) + "\n")
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
    L.append(f"- Hero-Bild: „ProVision Infra Schlüsseldienst öffnet eine Haustür in {k}“\n- Logo: „ProVision Infra Schlüsselnotdienst – Logo“\n- Fahrzeug/Team: „Mobiler ProVision Infra Schlüsselnotdienst im Einsatz in {k}“\n")

    L.append("## 4. Page Code → `<head>` (OnePage: Code-Symbol links → Spalte „Page Code“ → Bereich `<head>`)\n")
    L.append("```html\n" + jsonld(o) + "\n```\n")
    L.append("## 5. Prüfen nach dem Veröffentlichen\n")
    L.append(f"1. `{url}` im Browser öffnen, Titel/Description im Quelltext prüfen.\n2. https://search.google.com/test/rich-results?url={url} → keine Fehler.\n3. Google Search Console → URL-Prüfung → **Indexierung beantragen**.\n")
    return "\n".join(L)


def main():
    rows = []
    for o in D["orte"]:
        md = render(o)
        open(os.path.join(OUT, f"{o['slug']}.md"), "w", encoding="utf-8").write(md)
        k = kurz(o)
        rows.append([o["slug"], f"{DOMAIN}/{o['slug']}", f"Schlüsseldienst {k}", f"Schlüsselnotdienst {k}; Türöffnung {k}; Schlüsseldienst {k} 24h; Aufsperrdienst {k}; Schlüsseldienst {k} Kosten; Autoöffnung {k}", title_for(o), len(title_for(o)), desc_for(o), len(desc_for(o)), "neu" if o.get("neu") else "bestehend"])

    with open(os.path.join(HERE, "..", "05-keyword-map.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["slug", "url", "haupt_keyword", "neben_keywords", "title", "title_len", "description", "desc_len", "status"])
        w.writerow(["(home)", DOMAIN + "/", "Schlüsselnotdienst Bad Bevensen / Uelzen / Lüneburg", "Schlüsseldienst Bad Bevensen; Schlüsseldienst Uelzen Lüneburg; Türöffnung Festpreis; Schlüsselnotdienst 24h Landkreis Uelzen", "ProVision Infra Schlüsselnotdienst – Bad Bevensen, Uelzen, Lüneburg 24/7", 59, "Schlüsseldienst für Bad Bevensen, Uelzen, Lüneburg & Umgebung: Türöffnung zum Festpreis, zerstörungsfrei, 24/7, keine Anfahrtskosten. ☎ 05821 4049049", 150, "bestehend"])
        w.writerow(["turoffnung", DOMAIN + "/turoffnung", "Türöffnung Kosten", "Was kostet eine Türöffnung; Türöffnung Festpreis; Schlüsseldienst Preise; seriöser Schlüsseldienst erkennen", "Was kostet eine Türöffnung? Festpreis & Ablauf | ProVision Infra", 56, "Was darf eine Türöffnung kosten? Faire Preise zwischen 80 und 200 €, Festpreisgarantie am Telefon, zerstörungsfreie Öffnung. So arbeitet der ProVision Infra Schlüsselnotdienst.", 155, "bestehend"])
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


if __name__ == "__main__":
    main()
