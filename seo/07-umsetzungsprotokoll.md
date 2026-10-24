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

## Runde 3 (24.10.2026): Design, Texte, Preiszonen, Logo, technisches SEO, QA

### Design (angelehnt an provision-infra.de)
- Site-CSS (`seo/tools/onepage/design/site.css`, in OnePage unter *styles* gespeichert): Navy `#010D30`, Poppins, gelbe Pill-Buttons, blaue Karten, schwebende Header-Leiste, dezente Einblend-Animation (`design/body.js.html`, mit Fallback nach 3 s und `prefers-reduced-motion`).
- Startseiten-Hero neu: Foto der Türöffnung als Hintergrund (statt Bild mit eingebautem Schriftzug), dunkles Overlay 64 %, Text linksbündig in 14/24 Spalten, mobil eigener Abstand (Section-Padding wird mobil halbiert) und H1 28 px.
- Preiskarten ab 900 px als Raster mit drei Spalten, darunter weiter als Snap-Scroller. Mobiles Menü (Burger-Overlay) in Navy mit weißer Schrift.
- Header-Logo: `.con-kit-component-logo` bekommt feste Höhe 40 px (mobil 32 px) und `object-fit: contain`, kein Zuschnitt mehr.

### Logo und Bilder
- Media-Upload über die interne API: `POST /api/v1/media` → S3-Formular (das Feld `Content-Type` muss mitgeschickt werden) → `PATCH /api/v1/media/<id>`.
- Neue Medien: ProVision-Logo `media/4cce306e-55e9-4a38-8c50-e03da4d61e14`, Share-Bild 1200×630 `media/a1152861-f0bb-4a82-b64a-bc2ef9711404`, Logo-Kachel 600×600 `media/8fec4ad6-e809-4ca8-9f33-52ff07a297dc`, Favicon `media/1184b5ac-8efb-41f2-b4e7-fe0afa3ed466`.
- Logo-Atome aller Seiten getauscht (Alt-Text „ProVision Infra GmbH“); die Startseite hatte kein Logo-Atom mehr, es wurde über den Editor angelegt (Transaktion `create` braucht `value.entity` und `value.order`).
- `seoImage` aller 33 Seiten auf das Share-Bild gesetzt, Site-Schema (`schemaOrg`) nutzt Logo-Kachel und Share-Bild. Das alte Vorhängeschloss-Bild auf der Türöffnungsseite zeigt jetzt das Türfoto; auf 11 Ortsseiten wurde das Gründerfoto im Hero durch das Türfoto ersetzt, damit Alt-Text und Bild zusammenpassen.

### Preiszonen
- `orte.json` trägt pro Ort `preis_tueroeffnung`: 115 (Bad Bevensen), 135 (Altenmedingen, Barum, Bienenbüttel, Himbergen, Ebstorf, Uelzen, Melbeck, Wriedel, Rosche, Bavendorf), 169 (Dahlenburg, Suderburg, Wieren, Barendorf, Zernien, Lüneburg, Amelinghausen, Adendorf, Bad Bodenteich, Bleckede, Dannenberg, Hitzacker, Munster), 199 (Lüchow), 260 (Faßberg, Celle, Eschede). Nachts, am Wochenende und an Feiertagen plus 54 €, Zylinder ab 60 €.
- Preise stehen in Hero, Preiskarten, Textabschnitt, FAQ, Description und JSON-LD (`Service.offers.price`) jeder Ortsseite sowie in der Preistabelle der Türöffnungsseite und im Site-Schema.
- Annahmen, die bestätigt werden müssen: Lüneburg 169 €, Eschede 260 €, Bavendorf 135 €. Für Clenze (199 €) gibt es keine Seite.

### Texte
- Alle Ortsseiten, Startseite und Türöffnung redaktionell neu geschrieben (`generate_pages.py`, `oplib.py`, `build_special_ops.py`). Automatische Prüfung auf „ – “, „nicht nur“, „Experten“; Einsatzgebiet-Satz ohne Gedankenstrich und Dreiergruppe.
- Descriptions aller Seiten höchstens 155 Zeichen, Titel höchstens 60 Zeichen.

### Technisches SEO
- Überschriften-Hierarchie bereinigt: Ortsseiten h4/h5 → h3 (`build_heading_ops.py`), Startseite Abschnittstitel h2 und Kartentitel h3, Türöffnung-Block h2.
- Geprüft auf allen 33 Seiten: genau eine H1, Canonical, Open Graph, Viewport, `lang="de"`, JSON-LD (Locksmith, WebSite, Service, BreadcrumbList, FAQPage) gültig und konsistent zu Preis und URL, Sitemap mit 33 URLs, robots.txt.
- Tote Links korrigiert: `provision-infra.de/accesandsecurity` und `/infrastruktur` (404) → `https://provision-infra.de/`, Partnerlink Felgner → `https://www.felgner.de/`.
- Veröffentlichen immer mit `page._id`: bei duplizierten Seiten zeigt `storage.pages[].pageId` auf die Quellseite (Dahlenburg und Rosche waren deshalb zunächst nicht aktualisiert).

### Fehlerprüfung (QA)
- Headless-Crawl aller 33 Seiten in Desktop (1440 px) und Mobil (390 px): 0 Konsolenfehler, 0 defekte Bilder, 0 Bilder ohne Alt-Text, kein horizontaler Overflow, 34 interne Linkziele alle 200, Formulare und Footer-Links vorhanden.
- Fehlgeschlagene Requests nur für die Google-My-Maps-Einbettung (in der Sandbox blockiert); im Browser prüfen.
- Werkzeuge: `seo/tools/onepage/qa/crawl_check.py`, `seo/tools/onepage/qa/seo_check.py`, `seo/tools/onepage/qa/qa_crawl.js` (laufen im Playwright-Daemon; Screenshots landen im Scratchpad unter `bd/qa/`).

### Offen
- Preiszonen-Annahmen bestätigen (Lüneburg, Eschede, Bavendorf); Clenze-Seite anlegen, falls gewünscht.
- Impressum und AGB nennen „Schlüsselnotdienst Jannes Heino Baumann“ als Betreiber, Footer und Logo zeigen die ProVision Infra GmbH. Rechtlich abstimmen.
- Partnerlogos liegen nur in niedriger Auflösung vor (teils 85 px breit) und wirken auf Retina-Displays weich.
- Search-Console-Autorisierung in OnePage, Passwortwechsel des geteilten Google-Kontos, archivierte Seiten (Geschäftskunden, Schließanlagen, SimonsVoss, EVVA) weiterhin unveröffentlicht.
