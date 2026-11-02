# provision-infra.de: SEO-Audit Phase 1 (Stand 2. November 2026)

Umfang: komplette Domain, 36 WordPress-Seiten (19 indexierbar), gemessen mit eigenem Crawler, Lighthouse 12 (mobil und Desktop, Laborwerte), WordPress-REST-API, Yoast-Daten, Google Suggest und Branchenverzeichnissen. Keine Zahl in diesem Bericht ist geschätzt; wo Daten fehlen (Search Console, Analytics, echte Google-Rankings), steht das ausdrücklich dabei.

## 1. Kurzfassung

Die Seite ist technisch sauber indexierbar (Sitemap, robots.txt, Canonicals, Weiterleitungen, 404 in Ordnung, Lighthouse SEO 100), aber sie ist langsam, inhaltlich schmal für acht Geschäftsfelder und baut auf 15 nahezu identischen Ortsseiten, die von keiner Hauptseite verlinkt sind. Dazu kommen drei Punkte, die sofort geklärt werden sollten: der Hoster blockt nach wenigen Anfragen mit HTTP 429 (trifft Besucher wie Crawler), auf jeder Seite liegt ein Product-Markup mit Sternebewertung für das Unternehmen (Verstoß gegen Googles Richtlinien für strukturierte Daten) und ein Feedback-Werkzeug (BugHerd) läuft mit Fehlermeldung im Live-Betrieb.

| Bereich | Bewertung | Kernbefund |
|---|---|---|
| Indexierung | gut | 19 Seiten in Sitemap, alle 200, Canonicals korrekt, noindex sinnvoll gesetzt |
| Hosting | kritisch prüfen | HTTP 429 nach einem vollständigen Seitenaufruf plus Folgeseite innerhalb weniger Sekunden |
| Performance | schlecht | Lighthouse mobil 26 bis 52, Seitengewicht 3 bis 13 MB, Videos bis 6,2 MB, Drittskripte blockieren 2,5 s |
| Strukturierte Daten | fehlerhaft | Product mit AggregateRating 5,0 (128) für die Firma; LocalBusiness, Service, FAQ korrekt |
| Inhalte und Architektur | lückenhaft | 2 Leistungsseiten für 8 Geschäftsfelder, keine Zutrittskontroll-, Wartungs-, Branchen- oder Herstellerseiten |
| Ortsseiten | riskant | 15 Seiten, 72 bis 81 Prozent Textgleichheit, identisches Titel- und H1-Muster, intern verwaist |
| Interne Verlinkung | schwach | Hauptnavigation der Startseite besteht aus Sprungankern, Leistungsseiten kaum verlinkt |
| Conversion | ausbaufähig | keine klickbare Telefonnummer auf Start- und Leistungsseiten, ein CTA-Ziel, Testseiten online |
| Tracking | prüfen | GTM, Facebook-Pixel und Google Ads laden im Test ohne Einwilligung; Consent-Gating unklar |
| Local SEO | offen | Google Business Profile nicht einsehbar, zwei Telefonnummern im Einsatz |

## 2. Werkzeuge und Zugänge

Verfügbar und genutzt: eigener Crawler (Status, Weiterleitungen, Meta, Überschriften, Links, Bilder, JSON-LD), Lighthouse 12 mit Chromium (mobil und Desktop), WordPress-REST-API (öffentlich lesbar, Yoast-Daten enthalten), Google Suggest (echte Suchanfragen, keine Volumina), Branchenverzeichnisse per Abruf.

Nicht verfügbar in dieser Umgebung: Google Search Console, Google Analytics 4, Google Business Profile, WordPress-Admin, PageSpeed-Insights-API (Tageskontingent ohne Schlüssel erschöpft, daher keine CrUX-Felddaten), Suchmaschinen-Rankings (Google, Bing und DuckDuckGo liefern aus der Sandbox keine verwertbaren Ergebnisseiten; das Werkzeug WebSearch ist nicht regional). Es gibt keinen Claude-Connector für Search Console oder Analytics; der Connector „WordPress.com“ gilt nur für wordpress.com-Hosting, nicht für Raidboxes.

Benötigte Zugänge, jeweils ohne Passwörter im Chat (als Secret in den Umgebungseinstellungen dieser Cloud-Umgebung hinterlegen, Menü „Cloud environment“ → Edit → Network secrets bzw. Umgebungsvariablen; eine neue Sitzung liest sie ein):

| Zweck | Weg | Variable |
|---|---|---|
| Search Console (16 Monate Daten, Indexierung, Crawl-Statistiken) und GA4 | Google-Cloud-Dienstkonto anlegen, JSON-Schlüssel erzeugen, Dienstkonto-E-Mail in der Search Console als Nutzer „Vollständig“ und in GA4 als „Betrachter“ hinzufügen | `GOOGLE_SERVICE_ACCOUNT_JSON` |
| WordPress lesen und schreiben (Yoast-Felder, Alt-Texte, Menüs, Medien; Elementor über das installierte Plugin „Elementor MCP Composer“ zu prüfen) | Anwendungspasswort für einen eigenen Benutzer (Profil → Anwendungspasswörter) | `WP_APP_USER`, `WP_APP_PASSWORD` |
| Laufende Performance-Messung mit Felddaten | PageSpeed-Insights-API-Schlüssel (kostenlos, Google Cloud Console) | `PSI_API_KEY` |
| Hosting (Ratenbegrenzung, Cache, Bildoptimierung) | Prüfung im Raidboxes-Dashboard durch Dich oder Support-Ticket; optional Raidboxes-API-Token | `RAIDBOXES_TOKEN` (optional) |
| Google Business Profile | Phase 7; Zugriff per Google-Konto, Export der Statistiken reicht zunächst | später |

Kostenpflichtige Werkzeuge: Für echte Rankings und Suchvolumina wäre ein Rank-Tracker nötig (im Connector-Verzeichnis zum Beispiel OpenRush oder Ubersuggest). Empfehlung: erst Search Console anbinden, dann entscheiden.

## 3. URL-Inventar

Quelle: WordPress-REST-API (36 Seiten, 0 Beiträge), Yoast-Sitemap (19 URLs), Crawl (27 URLs erreicht, alle Status 200, zwei Weiterleitungen ohne Schrägstrich auf Schrägstrich). Vollständige Tabelle mit Titeln, Descriptions und Index-Status: `daten/inventory_rest.csv`.

### Indexierbare Seiten (19)

| URL | Funktion | Wörter | H1 | Bilder ohne Alt |
|---|---|---|---|---|
| / | Startseite, Schwerpunkt digitale Schließanlage | 2.445 | „Wir installieren in deinem Unternehmen ein digitales Schließsystem“ | 20 von 94 |
| /zutrittssystem/ | Leistungsseite elektronische Schließanlage mit Servicepaketen | 937 | „Wir betreuen deine elektronische Schließanlage und das Thema ist für dich dauerhaft abgeschlossen!“ | 32 von 58 |
| /kamerasysteme/ | Leistungsseite Videoüberwachung | 1.907 | „Wir schützen dein Unternehmen mit Kamera- & Videoüberwachung“ | 14 von 54 |
| /karriere/ | Stellen, JobPosting-Markup | 1.691 | „Komm ins Team von ProVision Infra …“ | 0 von 9 |
| 15 Ortsseiten: /lueneburg/, /uelzen/, /bad-bevensen/, /celle/, /bienenbuettel/, /bleckede/, /dannenberg/, /ebstorf/, /gifhorn/, /hitzacker/, /luechow/, /wieren/, /winsen-luhe/, /wittingen/, /bad-bodenteich/ | lokale Landingpages | 1.965 bis 2.260 | „Mechanische & elektronische Schließanlagen sowie Videoüberwachung in {Ort}“ | je 14 von 52 |

### Nicht indexierbare Seiten (17, noindex)

Kontakt-Varianten (/kontakt/, /kontakt-kamerasysteme/, /kontakt-kombiniert/, /kontakt-test/, /anfrage-auswahl/), Termin-Varianten (/termin/, /termin-kamerasysteme/, /termin-gebucht/, /termin-gebucht-kamerasysteme/), Danke-Seiten (/danke/, /danke-seite/), Rechtsseiten (/impressum/, /datenschutz/, /agb/), /wartung/ („Diese Seite befindet sich im Aufbau“), Testseiten (/elementor-3524/, /opt-2/).

Bewertung je Seitentyp (technischer Zustand, Keyword-Fokus, Suchintention, Content-Qualität, Ranking-Potenzial, Conversion-Potenzial, Bedarf):

| Seite | Technik | Keyword-Fokus | Intention | Qualität | Ranking-Potenzial | Conversion | Bedarf |
|---|---|---|---|---|---|---|---|
| Startseite | langsam (43) | breit, Slogan-H1 | gemischt | gut geschrieben, aber lang und doppelte Abschnitte | hoch für Marke und „digitale Schließanlage Unternehmen“ | mittel (CTA ja, Telefon nein) | mittel |
| /zutrittssystem/ | sehr langsam (26, 13 MB) | elektronische Schließanlage, Service | kommerziell | kurz, Pakete gut, Erklärung dünn | hoch | mittel | hoch |
| /kamerasysteme/ | langsam (40) | Videoüberwachung Unternehmen | kommerziell | ausführlich | hoch | mittel | mittel |
| Ortsseiten | langsam (52) | {Ort} + Schließanlagen + Videoüberwachung | lokal | textreich, aber austauschbar | nur Lüneburg, Uelzen, Celle realistisch | mittel (Telefon vorhanden) | hoch (Konsolidierung) |
| /karriere/ | ok | Jobs | Bewerbung | gut | nicht SEO-relevant | ja | gering |

## 4. Technische Befunde

### 4.1 Indexierung und Crawling (in Ordnung)
- robots.txt erlaubt alles und verweist auf `sitemap_index.xml`; die Sitemap enthält genau die 19 indexierbaren Seiten.
- http → https und www → ohne www per 301, URL ohne Schrägstrich → mit Schrägstrich per 301, unbekannte URL liefert 404, Canonicals zeigen bei Großschreibung und UTM-Parametern auf die saubere URL.
- Keine Weiterleitungsketten, keine defekten internen Links im Crawl, `lang="de"`, Viewport gesetzt, keine hreflang (nicht nötig).
- Kleinigkeiten: Großschreibung in URLs liefert 200 statt 301 (Canonical fängt es ab), der Feed /feed/ ist aktiv ohne Beiträge, Yoast setzt og:type „article“ auf statischen Seiten.

### 4.2 Hosting: Ratenbegrenzung (kritisch prüfen)
Nach einem vollständigen Seitenaufruf (rund 100 Ressourcen) beantwortete der Server den nächsten Seitenaufruf sechs Sekunden später mit HTTP 429 „Too Many Requests“. Dasselbe passierte bei zwölf kurz aufeinanderfolgenden Einzelabrufen. Ein gedrosselter Crawl mit einer Anfrage alle 3,5 Sekunden lief fehlerfrei. Wenn die Schwelle so niedrig liegt, trifft das auch Besucher, die zwei Seiten hintereinander öffnen, und Crawler beim Rendern. Zu klären bei Raidboxes: Regeln für Rate Limiting und Bot-Schutz, Ausnahme für Googlebot, danach Kontrolle in den Crawl-Statistiken der Search Console (Anteil 429/5xx).

### 4.3 Performance (schlecht, größter technischer Hebel)
Lighthouse 12, Laborwerte aus dieser Umgebung, mobil simuliert; Felddaten (CrUX) fehlen bis ein PSI-Schlüssel vorliegt.

| Seite | Performance | LCP | TBT | CLS | Gesamtgewicht |
|---|---|---|---|---|---|
| / mobil | 43 | 4,3 s | 3.390 ms | 0,002 | 4,1 MB |
| /zutrittssystem/ mobil | 26 | 14,3 s | 4.270 ms | 0,214 | 13,1 MB |
| /kamerasysteme/ mobil | 40 | 7,9 s | 1.560 ms | 0,046 | 3,1 MB |
| /lueneburg/ mobil | 52 | 3,6 s | 1.880 ms | 0,033 | 3,9 MB |
| / Desktop | 45 | 8,3 s | 370 ms | 0,004 | 8,7 MB |

Ursachen, nach Gewicht sortiert:
1. Videos: /zutrittssystem/ lädt zwei MP4 mit 6,2 MB und 3,7 MB, die Startseite ein Hero-Video mit 0,8 MB. Dazu eine Lottie-Animation als JSON mit 0,5 MB.
2. Bilder als PNG: Untitled-design-1.png 697 KB, Ellipse-3.png 449 KB (zweimal in verschiedenen Uploads), Ellipse-4.png 238 KB, 1.png und 2.png je 217 KB; Lighthouse beziffert die Ersparnis durch WebP/AVIF mit 930 bis 960 KB je Seite. 32 PNG stehen 8 WebP gegenüber.
3. Drittskripte: Google Tag Manager (323 KB, 1,76 s Blockierzeit), Facebook-Pixel samt CAPI-Skript (210 KB, 0,6 s), BugHerd (76 KB, läuft mit „Unauthenticated Error“ im Live-Betrieb), ProvenExpert-Widget. Drittcode blockiert den Hauptthread 1,4 bis 2,5 s je Seite.
4. HTML: 500 bis 611 KB pro Seite. Auf der Startseite: 187 KB Inline-SVG (61 Grafiken), 148 KB Base64-Bilder (22), 68 KB Elementor-`data-settings`, 63 KB Inline-CSS, 55 KB Inline-JS, 763 `div`-Elemente, 44 Elemente, die nur für einzelne Breakpoints eingeblendet werden (doppelte Abschnitte für Desktop und Mobil).
5. JavaScript: 300 bis 334 KB ungenutzt, DOM 1.263 bis 2.147 Elemente, Interaktivität erst nach 16 bis 19 s (mobil simuliert).
Positiv: TTFB 210 bis 220 ms, Varnish-Cache greift, WP Rocket 3.23 ist aktiv, Fonts mit `font-display: swap`, keine renderblockierenden Ressourcen gemeldet, Barrierefreiheit 98 bis 99, Lighthouse-SEO 100.

### 4.4 Strukturierte Daten
Yoast liefert WebPage, WebSite, BreadcrumbList, ImageObject (Organization nur auf /karriere/). Zusätzlich steckt auf Start-, Leistungs- und Ortsseiten ein eigener JSON-LD-Block mit:
- `LocalBusiness` + `Locksmith` (Name, Adresse Klein Hesebecker Straße 11, Telefon +49 5821 4049040, E-Mail, Geo, Öffnungszeiten, sameAs Instagram/Facebook/LinkedIn): gut.
- `Service` mit areaServed (Hamburg, Lüneburg, Winsen, Buchholz, Uelzen, Bad Bevensen, Soltau, Celle, Hannover, Niedersachsen): gut, auf Ortsseiten teilweise doppelt.
- `FAQPage`: gültig, Antworten enthalten HTML-Tags; Google zeigt FAQ-Rich-Results nur noch für Behörden und Gesundheitsseiten, Nutzen also gering, Schaden keiner.
- `Product` „ProVision Infra“ mit `AggregateRating` 5,0 aus 128 Bewertungen (ProvenExpert-Bild): Ein Unternehmen ist kein Produkt, und selbst erhobene Bewertungen dürfen nicht als Rich Result für die eigene Organisation ausgespielt werden. Das ist ein Verstoß gegen die Richtlinien zu Bewertungs-Snippets und kann zu einer manuellen Maßnahme „Strukturierte Daten“ führen. Entfernen.
- /karriere/: 4 × JobPosting (Prüfung im Rich-Results-Test nach WordPress-Zugang).

### 4.5 On-Page
- Titel: alle 19 indexierbaren Seiten unter 60 Zeichen, eindeutig; Ortsseiten folgen einem Muster („Schließanlagen & Videoüberwachung {Ort} | ProVision Infra“). Descriptions überall gesetzt (144 bis 158 Zeichen).
- H1: genau eine je Seite, aber als Werbesatz formuliert; die Suchbegriffe „Schließanlage“, „Zutrittskontrolle“, „Videoüberwachung“ plus Region fehlen in den H1 der Haupt- und Leistungsseiten weitgehend.
- H2: doppelte Blöcke durch Desktop- und Mobilvarianten („Der Gründer von ProVision Infra“, FAQ-Überschrift jeweils zweimal), Lighthouse meldet nicht absteigende Überschriftenebenen.
- Bilder: 14 bis 32 Bilder ohne Alt-Text je Seite, Hero-Grafiken als PNG.
- Texte: Du-Ansprache konsequent, Nutzenargumentation gut; Inhalte zu Technik, Herstellern, Kosten, Ablauf und Wartung fehlen oder sind nur im FAQ angerissen.

### 4.6 Interne Verlinkung und Navigation
- Auf der Startseite besteht das Hauptmenü aus Sprungankern (#digitalen, #arbeiten, #mehr, #Über, #FAQ) plus Karriere; auf Unterseiten lautet es Schließanlagen, Videoüberwachung, So arbeiten wir, Über uns, FAQ. Zwei Navigationen, kein durchgängiger Weg zu den Leistungen.
- /zutrittssystem/ wird von der Startseite nur über einen einzigen Textlink erreicht; es gibt keine Footer-Links auf Leistungen.
- Die 15 Ortsseiten erhalten keinen einzigen Link von Startseite, Leistungsseiten oder Footer; sie verlinken nur untereinander. Google findet sie nur über die Sitemap.
- Zur Schwesterseite schluesselnotdienst-baumann.de gibt es keinen Link, umgekehrt schon.

### 4.7 Conversion
- Haupt-CTA „Unverbindliches Erstgespräch vereinbaren“ fünfmal auf der Startseite, Ziel /kontakt (Gravity Forms), dazu Terminseiten.
- Keine klickbare Telefonnummer auf Startseite und beiden Leistungsseiten (0 tel-Links); Ortsseiten und Karriere haben sie.
- Fünf Kontakt- und vier Termin-Varianten sowie Testseiten (/kontakt-test/, /opt-2/, /elementor-3524/) sind erreichbar; Danke-Seiten vorhanden (gut für Zielmessung).
- Vertrauenssignale vorhanden (ProvenExpert 5,0 bei 128 Bewertungen, Kundenstimmen, Gründer-Vorstellung), aber keine Referenzprojekte, keine Zertifikate oder Partnerlogos mit Erklärung auf den Leistungsseiten.

### 4.8 Tracking und Einwilligung
Google Tag Manager (GTM-KV75JXFB) lädt gtag (GT-NC8XZMMS), Facebook-Pixel (1882223199102262) samt CAPI-Automations-Skript und Google Ads/DoubleClick; Borlabs Cookie ist installiert. In der Testumgebung wurden Anfragen an connect.facebook.net und googleads.g.doubleclick.net ohne jede Interaktion mit dem Cookie-Banner ausgelöst. Ob die Tags über den Consent-Status gesteuert werden, muss im GTM geprüft werden (Datenschutz-Risiko, keine Rechtsberatung). BugHerd gehört nicht auf die Live-Seite.

### 4.9 Local SEO
- NAP im Markup vollständig, Telefon +49 5821 4049040; die Schlüsselnotdienst-Seite nutzt 05821 4049049. Beide Nummern sind legitim, müssen aber im Google Business Profile und in Verzeichnissen konsistent zugeordnet sein.
- Google Business Profile, Kategorien, Bewertungen und Einträge in Verzeichnissen konnten nicht geprüft werden (Zugang fehlt).

## 5. Ortsseiten: Bewertung des Doorway-Risikos

Die 15 Ortsseiten haben 1.965 bis 2.260 Wörter, dasselbe H1-Muster, 18 H2 in gleicher Reihenfolge und dieselben Bausteine (mechanische und elektronische Schließanlagen, smarte Türschlösser, Umrüstung, Videoüberwachung, Leistungen, Zielgruppen, Technik, Kundenstimmen). Nach Neutralisierung der Ortsnamen liegt die Wortgleichheit zwischen zwei beliebigen Seiten im Mittel bei 72,5 Prozent, maximal 81,1 Prozent (Bad Bodenteich/Wieren). Nur 19 bis 23 Prozent der Wörter einer Seite kommen nicht auf allen anderen vor. Orte wie Wieren, Wittingen oder Hitzacker haben für Zutrittssysteme kaum eigenes Suchvolumen (Google Suggest liefert für „Schließanlagen Uelzen“ als Nächstes „Schließanlagen Lüneburg“, für kleinere Orte nichts).

Google wertet solche Seiten als Doorway-Muster, wenn sie allein dem Ranking für Ortsvarianten dienen. Empfehlung: drei bis fünf regionale Seiten mit echtem Mehrwert behalten (Lüneburg, Uelzen, Celle, Lüchow-Dannenberg, Hamburg-Süd/Winsen als strategischer Ausbau) und mit Referenzen, Anfahrtszeiten, Ansprechpartnern, regionalen Branchen und Bildern füllen; die übrigen per 301 auf die zuständige Regionalseite leiten oder auf noindex setzen und einen „Einsatzgebiet“-Hub mit Karte und Links anlegen. URL-Änderungen nur mit Deiner Freigabe.

## 6. Keyword- und Content-Architektur

Abgleich Geschäftsfelder gegen vorhandene Seiten:

| Geschäftsfeld | Seite heute | Lücke |
|---|---|---|
| Elektronische/digitale Schließanlagen | Startseite, /zutrittssystem/ | Erklärung der Systeme, Kosten, Ablauf, Hersteller fehlen |
| Mechanische Schließanlagen | nur Abschnitt auf Ortsseiten | eigene Seite fehlt |
| Elektronische Zutrittskontrolle | nur im Markup und FAQ | eigene Seite fehlt (Suchbegriff mit eigener Nachfrage) |
| Videoüberwachung | /kamerasysteme/ | Rechtslage/DSGVO, Kostenrahmen, Branchen fehlen |
| Sicherheitsberatung/Einbruchschutz | keine | eigene Seite fehlt |
| Wartung, Service, Managed Access | /wartung/ „im Aufbau“, noindex | fertigstellen, indexieren |
| Schlüsselnotdienst/Türöffnung | eigene Domain | Verweis und Übergabe fehlen |
| Vermietung/Finanzierung | keine | eigene Seite fehlt |
| Hersteller EVVA Xesar, AirKey, SimonsVoss | Logos | eigene Systemseiten fehlen |
| Branchen (Hausverwaltung, Praxis, Hotel, Pflege, Industrie, Kommune) | Aufzählung | eigene Seiten fehlen |
| Referenzen/Projekte | Kundenstimmen | Projektberichte fehlen |

Nachfrage laut Google Suggest (echte Anfragen, Volumina folgen mit Search Console):
- Kosten: „schließanlage kosten“, „schließanlage kosten mehrfamilienhaus“, „digitale schließanlage kosten“, „zutrittskontrollsystem kosten“, „schließanlage hotel kosten“, „elektronische schließanlage mit chip kosten“, „schließanlage kostengruppe DIN 276“, „digitale schließanlage abschreibung“.
- Technik: „elektronische schließanlage mit chip / transponder“, „zutrittskontrolle rfid“, „digitale schließanlage simonsvoss“, „schließanlage nachträglich erweitern“, „digitale schließanlage vergleich“.
- Recht und Betrieb: „videoüberwachung gewerbe rechtslage“, „videoüberwachung unternehmen dsgvo“, „schild videoüberwachung gewerbe pflicht“, „wartung schließanlage umlagefähig“, „wartungsvertrag schließanlage“.
- Hersteller: „evva xesar software / beschlag / zylinder / wandleser“, „evva airkey app / transponder / batterie“, „simonsvoss transponder / zylinder / batteriewechsel / mobilekey“.
- Regional: „zutrittskontrolle hamburg“, „schließsysteme hannover“, „überwachungskamera lüneburg“, „sicherheitstechnik lüneburg / uelzen“, „schließanlagen lüneburg“ (als Vorschlag zu „Schließanlagen Uelzen“).

Vorschlag Seitenplan (primäres Keyword, Intention, Ziel-URL): siehe `02-keyword-plan.md` nach Freigabe der Architektur. Die Reihenfolge für neue Inhalte: Zutrittskontrolle Unternehmen → Wartung & Managed Access → Mechanische Schließanlagen → EVVA Xesar → SimonsVoss → EVVA AirKey → Videoüberwachung Rechtslage DSGVO → Kosten-Ratgeber Schließanlage → Branchen Hausverwaltung, Praxis, Hotel → Referenzen.

## 7. Wettbewerb (erste Einordnung, ohne Rankingdaten)

Echte Google-Positionen lassen sich aus dieser Umgebung nicht messen. Aus Verzeichnissen (Gelbe Seiten, Trustlocal) und Ausschreibungen ergibt sich das Feld:
- Lokal Lüneburg: a-z Elbe Schlüsselzentrum 24/7 (Sicherheitstechnik, 24 h, Premium-Eintrag), Heym GmbH (Alarmanlagen), Haus für Sicherheit Eric Henß, MS Schlüsseldienst Lüneburg (Schließanlagen mit patentiertem Profil), Lüneburger Schlüsseldienst Alznauer, Hano Sicherheitstechnik GmbH, SHUR Sicherheit & Service, Schlüsseldienst & Sicherheitstechnik Thobe.
- Uelzen: Mocek Schlüsseldienst (EVVA, ABUS, DOM).
- Öffentliche Auftraggeber: Heidenreich Elektrotechnik (Lüneburg) erhielt 2021 den Auftrag für die elektronische Schließanlage der Kreisverwaltung Lüneburg; die Leuphana betreibt ASSA-ABLOY-Technik.
- Überregional: Herstellerseiten (EVVA, SimonsVoss, dormakaba, ABUS) und Portale für Kostenfragen (schliessanlage-kaufen.de, schliessanlagen-direkt.de, dieschliessanlage.de, kostencheck.de).
Ableitung: Kein lokaler Anbieter besetzt die Themen Zutrittskontrolle für Unternehmen, Managed Access und Videoüberwachung mit tiefen Inhalten; Portale gewinnen die Kostenfragen mit Rechnern und Tabellen. Beides ist mit fachlich besseren Inhalten erreichbar. Vollständige Analyse (Phase 3) nach Anbindung der Search Console oder eines Rank-Trackers.

## 8. Die zehn Maßnahmen mit dem größten Geschäftsnutzen

| Nr. | Maßnahme | SEO-Nutzen | Geschäftsnutzen | Aufwand | Risiko | Freigabe nötig |
|---|---|---|---|---|---|---|
| 1 | Ratenbegrenzung beim Hoster prüfen und für Besucher sowie Googlebot entschärfen | sehr hoch (Crawling, Rendering) | hoch (Abbrüche) | gering | gering | Hosting-Einstellung |
| 2 | Performance-Paket: Videos komprimieren und erst bei Interaktion laden, Poster-Bild, PNG zu WebP/AVIF, Lottie reduzieren, BugHerd entfernen, Drittskripte nach Einwilligung und verzögert laden, ungenutztes JS/CSS | hoch (Core Web Vitals) | hoch (Absprünge mobil) | mittel | gering | WordPress/Elementor |
| 3 | Product-Markup entfernen, LocalBusiness/Service bereinigen, Organization zusammenführen, og:type | hoch (Richtlinien) | mittel | gering | gering | Code |
| 4 | Ortsseiten konsolidieren: 3 bis 5 Regionalseiten mit echtem Lokalbezug, übrige weiterleiten oder noindex, Einsatzgebiet-Hub | hoch (Qualität, Doorway-Risiko) | mittel | mittel | mittel | URL-Änderungen |
| 5 | Navigation und Footer: Leistungen, Branchen, Regionen, Referenzen, Kontakt, Schlüsselnotdienst durchgängig verlinken | hoch (interne Links) | mittel | gering | gering | Navigation |
| 6 | Leistungsseiten: Zutrittskontrolle neu, Wartung & Managed Access fertigstellen, Mechanische Schließanlagen, Sicherheitsberatung, Vermietung/Finanzierung; H1 und Titel mit Keyword und Region | sehr hoch | sehr hoch (B2B-Anfragen) | hoch | gering | neue Inhalte |
| 7 | Systemseiten EVVA Xesar, EVVA AirKey, SimonsVoss (Einsatz, Betrieb, Batteriewechsel, Kosten, Service) | hoch | hoch | mittel | gering | neue Inhalte |
| 8 | Ratgeber-Cluster: Kosten, DSGVO/Rechtslage Videoüberwachung, Schließanlage erweitern, Wartung umlagefähig, Abschreibung; Frage-Antwort-Struktur für KI-Suche | hoch | mittel bis hoch | hoch | gering | neue Inhalte |
| 9 | Conversion: klickbare Telefonnummer und Kontaktleiste überall, Ziel-Messung in GA4 über GTM (Formular, Telefonklick, Termin), Consent-Gating prüfen, Testseiten entfernen | mittel | hoch | gering | gering | GTM/GA4, Seiten |
| 10 | Local SEO: Google Business Profile (Kategorien, Leistungen, Einzugsgebiet, Fotos), NAP-Konsistenz, Branchen- und Herstellerverzeichnisse, Bewertungsstrategie, Link von und zur Schlüsselnotdienst-Seite | hoch (lokal) | hoch | mittel | gering | externe Einträge |

## 9. 90-Tage-Fahrplan

| Zeitraum | Schwerpunkt | Inhalte |
|---|---|---|
| Woche 1 bis 2 | Kritische Technik und Messbasis | Zugänge einrichten (Search Console, GA4, WordPress, PSI-Schlüssel), Ratenbegrenzung klären, Product-Markup und BugHerd entfernen, Alt-Texte, Telefon-CTA, Testseiten entfernen, Ausgangswerte dokumentieren |
| Woche 3 bis 4 | Performance und Architektur | Videos, Bilder, Drittskripte, Navigation und Footer, Einsatzgebiet-Hub, Entscheidung zur Ortsseiten-Konsolidierung, Search-Console-Auswertung (Quick Wins Position 4 bis 20) |
| Woche 5 bis 8 | Leistungs- und Systemseiten | Zutrittskontrolle, Wartung & Managed Access, Mechanische Schließanlagen, EVVA Xesar, SimonsVoss; Ortsseiten umsetzen; interne Verlinkung |
| Woche 9 bis 12 | Ratgeber, Local SEO, Autorität | Kosten- und Rechtsratgeber, Branchenseiten, Google Business Profile, Verzeichnisse, erste Referenzberichte, Reporting-Routine |

Erfolgskontrolle: wöchentlicher Bericht mit erledigten Aufgaben, Veränderungen in Klicks, Impressionen, Positionen (Search Console), Anfragen (GA4-Ereignisse), Core Web Vitals (CrUX/PSI) und Indexierungsstatus; Ausgangsbasis wird nach Zugang zur Search Console festgehalten.

## 10. Freigabeliste

Sofort umsetzbar nach WordPress-Zugang (gering riskant, kein Design-Eingriff):
1. Product-Markup aus dem JSON-LD-Block entfernen, Service-Dubletten bereinigen.
2. BugHerd-Skript entfernen.
3. Alt-Texte für alle Bilder ohne Alt (Medienbibliothek).
4. Klickbare Telefonnummer im Header/Footer, Testseiten (/kontakt-test/, /opt-2/, /elementor-3524/) in den Entwurf oder löschen (Löschen nur mit Freigabe).
5. Footer um Leistungen, Regionen und Schlüsselnotdienst-Link erweitern; Hauptnavigation vereinheitlichen.

Freigabepflichtig mit Entscheidung:
6. Ortsseiten-Konsolidierung (welche bleiben, Weiterleitungen).
7. Video- und Bildoptimierung (Austausch von Medien, ggf. Bildoptimierungs-Plugin oder WP-Rocket-Einstellungen).
8. GTM-Anpassungen (Consent-Gating, Ziel-Ereignisse).
9. Neue Seiten und Texte (Entwürfe liefere ich vor Veröffentlichung).
10. Raidboxes-Einstellungen (Rate Limiting, Bot-Schutz).

Rohdaten: `daten/audit_summary.json`, `daten/lighthouse_summary.json`, `daten/crawl_summary.json`, `daten/inventory_rest.csv`, `daten/google_suggest.json`, Screenshots unter `daten/screenshots/`.
