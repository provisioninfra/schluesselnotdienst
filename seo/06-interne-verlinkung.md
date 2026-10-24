# Interne Verlinkung – Linkplan

Aktuell verweist **keine einzige interne Seite** auf die Ortsseiten (die Ortsliste auf der Startseite ist reiner Text). Google erreicht sie nur über die Sitemap – das ist der Hauptgrund für schwache/fehlende Indexierung.

## A. Startseite – Abschnitt „Unser Einsatzgebiet“

Jede Kachel wird ein Link (in OnePage: Text markieren → Link → interne Seite wählen). Reihenfolge nach Nähe/Relevanz:

- Schlüsseldienst Bad Bevensen → `/bad-bevensen`
- Schlüsseldienst Uelzen → `/uelzen`
- Schlüsseldienst Lüneburg → `/lueneburg`
- Schlüsseldienst Bienenbüttel → `/bienenbuettel`
- Schlüsseldienst Altenmedingen → `/altenmedingen`
- Schlüsseldienst Barum → `/barum`
- Schlüsseldienst Himbergen → `/himbergen`
- Schlüsseldienst Ebstorf → `/ebstorf`
- Schlüsseldienst Wriedel → `/wriedel`
- Schlüsseldienst Melbeck → `/melbeck`
- Schlüsseldienst Adendorf → `/adendorf`
- Schlüsseldienst Barendorf → `/barendorf`
- Schlüsseldienst Dahlenburg → `/dahlenburg`
- Schlüsseldienst Amelinghausen → `/amelinghausen`
- Schlüsseldienst Bleckede → `/bleckede`
- Schlüsseldienst Rosche → `/rosche`
- Schlüsseldienst Suderburg → `/suderburg`
- Schlüsseldienst Wieren → `/wieren`
- Schlüsseldienst Bad Bodenteich → `/bad-bodenteich`
- Schlüsseldienst Zernien → `/zernien`
- Schlüsseldienst Dannenberg (Elbe) → `/dannenberg`
- Schlüsseldienst Hitzacker (Elbe) → `/hitzacker`
- Schlüsseldienst Lüchow (Wendland) → `/luechow`
- Schlüsseldienst Munster → `/munster`
- Schlüsseldienst Faßberg → `/fassberg`
- Schlüsseldienst Eschede → `/eschede`
- Schlüsseldienst Celle → `/celle`
- Schlüsseldienst Bavendorf → `/bavendorf`

Dem Abschnitt die Anker-ID `einsatzgebiet` geben (Custom attributes → ID), damit `/#einsatzgebiet` funktioniert.

## B. Jede Ortsseite – Abschnitt „Schlüsseldienst in der Nähe“

| Seite | verlinkt auf |
|---|---|
| /bad-bevensen | /altenmedingen, /barum, /bienenbuettel, /himbergen, /ebstorf, /uelzen, /turoffnung, / |
| /uelzen | /bad-bevensen, /bienenbuettel, /suderburg, /rosche, /wieren, /ebstorf, /turoffnung, / |
| /lueneburg | /adendorf, /melbeck, /barendorf, /bienenbuettel, /amelinghausen, /bad-bevensen, /turoffnung, / |
| /bienenbuettel | /bad-bevensen, /melbeck, /uelzen, /lueneburg, /altenmedingen, /ebstorf, /turoffnung, / |
| /himbergen | /bad-bevensen, /altenmedingen, /dahlenburg, /zernien, /rosche, /barum, /turoffnung, / |
| /ebstorf | /bad-bevensen, /wriedel, /uelzen, /bienenbuettel, /suderburg, /amelinghausen, /turoffnung, / |
| /melbeck | /lueneburg, /bienenbuettel, /bad-bevensen, /amelinghausen, /adendorf, /barendorf, /turoffnung, / |
| /barendorf | /lueneburg, /dahlenburg, /adendorf, /bleckede, /melbeck, /himbergen, /turoffnung, / |
| /adendorf | /lueneburg, /barendorf, /bleckede, /melbeck, /bienenbuettel, /dahlenburg, /turoffnung, / |
| /bavendorf | /bad-bevensen, /uelzen, /lueneburg, /bienenbuettel, /melbeck, /ebstorf, /turoffnung, / |
| /altenmedingen | /bad-bevensen, /himbergen, /barum, /bienenbuettel, /uelzen, /ebstorf, /turoffnung, / |
| /barum | /bad-bevensen, /altenmedingen, /uelzen, /himbergen, /rosche, /bienenbuettel, /turoffnung, / |
| /bleckede | /dahlenburg, /barendorf, /adendorf, /hitzacker, /lueneburg, /himbergen, /turoffnung, / |
| /hitzacker | /dannenberg, /bleckede, /zernien, /dahlenburg, /luechow, /himbergen, /turoffnung, / |
| /dannenberg | /hitzacker, /zernien, /luechow, /dahlenburg, /himbergen, /bleckede, /turoffnung, / |
| /luechow | /dannenberg, /hitzacker, /zernien, /bad-bodenteich, /rosche, /wieren, /turoffnung, / |
| /zernien | /dannenberg, /hitzacker, /dahlenburg, /himbergen, /luechow, /bad-bevensen, /turoffnung, / |
| /bad-bodenteich | /wieren, /uelzen, /suderburg, /rosche, /luechow, /bad-bevensen, /turoffnung, / |
| /celle | /eschede, /fassberg, /munster, /bad-bodenteich, /suderburg, /uelzen, /turoffnung, / |
| /fassberg | /munster, /eschede, /celle, /suderburg, /wriedel, /uelzen, /turoffnung, / |
| /munster | /fassberg, /wriedel, /ebstorf, /suderburg, /amelinghausen, /celle, /turoffnung, / |
| /wriedel | /ebstorf, /munster, /amelinghausen, /suderburg, /bad-bevensen, /uelzen, /turoffnung, / |
| /amelinghausen | /lueneburg, /melbeck, /wriedel, /ebstorf, /munster, /bienenbuettel, /turoffnung, / |
| /rosche | /uelzen, /himbergen, /bad-bevensen, /barum, /luechow, /wieren, /turoffnung, / |
| /dahlenburg | /himbergen, /barendorf, /bleckede, /zernien, /lueneburg, /bad-bevensen, /turoffnung, / |
| /suderburg | /uelzen, /ebstorf, /wriedel, /bad-bodenteich, /fassberg, /bad-bevensen, /turoffnung, / |
| /wieren | /uelzen, /bad-bodenteich, /rosche, /suderburg, /luechow, /bad-bevensen, /turoffnung, / |
| /eschede | /celle, /fassberg, /suderburg, /bad-bodenteich, /uelzen, /munster, /turoffnung, / |

## C. Footer (Site-weit)

- Impressum → `/impressum` (aktuell extern auf provision-infra.de!)
- Datenschutz → `/datenschutzerklarung` (aktuell extern)
- AGB → `/agb` (aktuell extern)
- Türöffnung & Preise → `/turoffnung`
- Kurze Ortsliste: Bad Bevensen · Uelzen · Lüneburg · Bienenbüttel · Ebstorf · Dannenberg · Celle (je Link)

## D. Navigation

- „Einsatzgebiete“ → `/#einsatzgebiet` (Anker auf der Startseite)
- „Türöffnung & Preise“ → `/turoffnung`
- „Geschäftskunden“ nur anzeigen, wenn die Seite wieder existiert (aktuell 404)

## E. Kaputte Links entfernen/ersetzen

- `/geschaftskunden` (404) – auf AGB, Datenschutz, Impressum, Türöffnung verlinkt
- `/simonsvosstechnologies` (404) – im Footer von Türöffnung/AGB
