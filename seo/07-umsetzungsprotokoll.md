# Umsetzungsprotokoll – schluesselnotdienst-baumann.de (OnePage), 24.10.2026

Alle Änderungen wurden über den OnePage-Account technik@provision-infra.de (Projektmitglied) umgesetzt und veröffentlicht.
Vor jeder Änderung wurde eine Versionssicherung angelegt (OnePage → Seite → Versionsverlauf), die alten Stände lassen sich dort wiederherstellen.

## Live geschaltet

### Ortsseiten (28, davon 4 neu: Bad Bevensen, Suderburg, Wieren, Eschede)
- Titel „Schlüsseldienst {Ort} – 24h Notdienst zum Festpreis“ (≤ 60 Zeichen), Description mit Festpreis, Anfahrtszeit und Telefonnummer, Keywords.
- Genau eine H1 („Schlüsseldienst {Ort} – 24/7 Notdienst zum Festpreis“), H2 „ProVision Infra Schlüsselnotdienst für {Ort}“, Hero-Text mit Preis und Anfahrtszeit, Alt-Text des Hero-Bildes.
- Neuer Inhaltsblock je Ort (Einleitung, lokaler Abschnitt, Preise, Ablauf, Leistungen, 5 FAQ, Nachbarorte-Links, verlinktes Einsatzgebiet-Raster, Karte, Anruf-Button).
- Strukturierte Daten je Seite: Service (mit Festpreis), BreadcrumbList, FAQPage. Site-weit: Locksmith + WebSite (@graph) über „Information Schema“.
- Footer: Copyright ProVision Infra GmbH, interne Links (Startseite, Türöffnung & Preise, Einsatzgebiete, Impressum, Datenschutz, AGB). Header: „Leistungen“ → „Türöffnung & Preise“.
- Bad Bevensen: 115 € Festpreis, alle anderen Orte 135 €.

### Startseite
- Titel „Schlüsselnotdienst Bad Bevensen · Uelzen · Lüneburg 24/7“, neue Description (Tippfehler „Lüenburg“ entfernt).
- Nur noch eine H1 („Schlüsselnotdienst Bad Bevensen“), H2 ergänzt um „24/7 Notdienst zum Festpreis“.
- „Jetzt Kontaktieren“-Button ruft jetzt an (vorher Link auf provision-infra.de).
- Einsatzgebiet: Ortskacheln sind echte Links auf alle 28 Ortsseiten, Anker `#einsatzgebiet`, Textabschnitt mit Preisen.
- Footer-Links auf die eigenen Seiten statt provision-infra.de.

### Türöffnung
- H1 „Was kostet eine Türöffnung? Festpreise & Ablauf“, Preistabelle, Checkliste „seriöser Schlüsseldienst“, FAQ (+ FAQPage-Schema), Links zu den Ortsseiten.
- Tote Links (Geschäftskunden, SIMONSVOSS) aus Header/Footer entfernt.

### Impressum, AGB, Datenschutz
- Telefonnummer im Impressum korrigiert (05821-4049049), Titel/Description gesetzt, tote Links entfernt.

### Projekt
- Website-Name „ProVision Infra Schlüsselnotdienst“, Title-Pattern `{{page_title}}`.
- 14 Weiterleitungen (301) für alte URLs, u. a. /impressum-1, /badbodenteich, /geschaftskunden, /luneburg, /tueroeffnung, /home, /index.html.
- 404 bleibt die Standardseite von OnePage (liefert korrekt HTTP 404; eine eigene 404-Seite liefert bei OnePage HTTP 200 und wurde deshalb wieder entfernt).

## Nicht möglich / offen
- Umlaut-URLs (/lüneburg, /türöffnung, /lüchow, /bienenbüttel, /faßberg, /geschäftskunden) lassen sich in OnePage nicht als Weiterleitung anlegen (ungültige Zeichen). Sie laufen auf 404 und fallen aus dem Index; ggf. OnePage-Support fragen.
- www.schluesselnotdienst-baumann.de und schlusselnotdienst.onepage.me liefern die Seite mit Canonical auf die Hauptdomain (kein 301) – für Google ausreichend, ein 301 wäre sauberer (OnePage → Domain-Einstellungen).
- Google Search Console: in OnePage unter Einstellungen → SEO → Google Search Console mit dem Google-Konto verbinden, dann Sitemap einreichen und alle URLs zur Indexierung anmelden.
- Google-Unternehmensprofil: Name, Adresse, Telefon identisch zur Website pflegen, Kategorie „Schlüsseldienst“, Einsatzgebiete als Leistungsbereich, Website-Link, Bewertungen sammeln.
- Archivierte Seiten (Geschäftskunden, Sicherheitsberatung, Schließanlagen, SimonsVoss, EVVA, Emmendorf) wurden nicht reaktiviert – bei Bedarf wiederherstellen und auf das neue Schema bringen.

## Werkzeuge (Repository)
- `seo/tools/orte.json` – Ortsdaten (Anfahrtszeit, Ortsteile, Nachbarn, Preis).
- `seo/tools/generate_pages.py` – Texte/SEO je Ort (`seo/seiten/*.md`).
- `seo/tools/onepage/build_ops.py`, `build_special_ops.py`, `oplib.py` – erzeugen die OnePage-Patch-Operationen aus Seiten-Dumps (`pagesV2.fetchPage`); angewendet über `transactions.processV2` und `pagesV2.updateVersionData`, veröffentlicht mit `pagesV2.publishPage`.
