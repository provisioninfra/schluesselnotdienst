# Türöffnung – SEO-Inhalte für `/turoffnung`

Ziel-Keywords: „Was kostet eine Türöffnung“, „Türöffnung Kosten Schlüsseldienst“, „Türöffnung Festpreis“, „seriöser Schlüsseldienst erkennen“, „Schlüsseldienst Preise Uelzen/Lüneburg“.

## 1. Seiten-Einstellungen → SEO

| Feld | Wert | Länge |
|---|---|---|
| Seitentitel | Was kostet eine Türöffnung? Festpreis & Ablauf | ProVision Infra | 64 → Kurzform: Was kostet eine Türöffnung? Festpreise & Ablauf | 48 |
| Beschreibung | Was darf eine Türöffnung kosten? Bei uns 115 € in Bad Bevensen, 135 € im Umland – Festpreis inkl. Anfahrt, zerstörungsfrei, 24/7. So arbeitet ProVision Infra. | 152 |

## 2. Struktur

- **H1 (statt „Wichtig für DICH!“):** Was kostet eine Türöffnung? Festpreise & Ablauf beim ProVision Infra Schlüsselnotdienst
- **H2:** Was darf eine Türöffnung kosten? *(bestehender Text + Preistabelle: Bad Bevensen 115 € / Umland 135 € / Nacht, Wochenende, Feiertag + 54 € / Profilzylinder ab 60 €)*
- **H2:** Woran erkennst Du einen seriösen Schlüsseldienst? *(neu: Festpreis vorab, regionale Adresse, Festnetznummer, keine Barzahlungspflicht, Quittung/Rechnung; Verweis Verbraucherzentrale beibehalten)*
- **H2:** Wie öffnen wir Türen? *(bestehend)*
- **H2:** Häufige Fragen zur Türöffnung *(Dauer, Beschädigung, Ausweis, Zahlungsarten)*
- **H2:** Kundenbewertungen *(bestehend)*
- **H2:** Türöffnung in Deiner Nähe – Links zu Bad Bevensen, Uelzen, Lüneburg, Bienenbüttel, Ebstorf, Dannenberg, Celle

## 3. Kaputte Links auf dieser Seite

- Footer „SIMONSVOSS_Technologies“ → `/simonsvosstechnologies` (404) → auf https://www.simons-voss.com/ oder entfernen
- Navigation „Geschäftskunden“ → `/geschaftskunden` (404) → entfernen oder Seite neu anlegen
- Bild ohne Alt-Text ergänzen

## 4. Page Code → `<head>`

```html
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
 {"@type":"Question","name":"Was kostet eine Türöffnung beim Schlüsseldienst?","acceptedAnswer":{"@type":"Answer","text":"Beim ProVision Infra Schlüsselnotdienst kostet die Türöffnung montags bis freitags von 8 bis 18 Uhr 115 € in Bad Bevensen und 135 € im Umland – Festpreis inklusive Anfahrt und MwSt. Nachts, am Wochenende und an Feiertagen kommen 54 € dazu. Den Preis bestätigen wir vor dem Auftrag am Telefon."}},
 {"@type":"Question","name":"Wird die Tür bei der Öffnung beschädigt?","acceptedAnswer":{"@type":"Answer","text":"In über 90 % der Fälle öffnen wir zerstörungsfrei. Muss ein Zylinder getauscht werden, besprechen wir das vorher und haben Ersatz dabei."}},
 {"@type":"Question","name":"Muss ich mich ausweisen?","acceptedAnswer":{"@type":"Answer","text":"Ja, wir öffnen nur für Berechtigte. Ohne Ausweis kannst Du die Berechtigung im Nachgang nachweisen oder rechtsverbindlich versichern."}},
 {"@type":"Question","name":"Wie kann ich bezahlen?","acceptedAnswer":{"@type":"Answer","text":"Bar, mit EC- oder Kreditkarte oder per PayPal direkt vor Ort; Geschäftskunden auch auf Rechnung."}}
]}
</script>
```
