"""Ersetzt das alte Schlüsseldienst-Logo überall durch das ProVision Infra GmbH Logo.

Erzeugt pro Seite eine Ops-Datei (gleiches Format wie build_ops.py):
  - Header-Logo-Atome (type logo): src/name/alt
  - Türöffnung: Inhaltsbild mit altem Logo -> Foto der Türöffnung
  - seoImage (Vorschaubild beim Teilen) -> neues Share-Bild
Aufruf: python3 build_logo_ops.py <pages_dir> <ops_out_dir> <logo_media> <share_media> [door_media]
"""
import json, os, sys, glob

OLD_LOGOS = ("media/f9260dc5-936f-4aa4-8ef6-f6f67cd432c8", "media/a705f219-260e-422b-9c61-9bfcc96afd36")
OLD_SHARE = ("media/43162a4e-22d6-4146-9507-160d48450783", "media/e750b114-7612-4dbe-a7b2-d6ea753af2b9")
LOGO_ALT = "ProVision Infra GmbH"
LOGO_NAME = "provision-infra-gmbh-logo.png"
DOOR_ALT = "Schlüsseldienst öffnet eine Haustür ohne Schaden, ProVision Infra Schlüsselnotdienst"

def main():
    pages_dir, out_dir, logo, share = sys.argv[1:5]
    door = sys.argv[5] if len(sys.argv) > 5 else "media/0496d5a4-d79f-4e3d-80a7-5efcf913dc13"
    os.makedirs(out_dir, exist_ok=True)
    n_pages = 0
    for f in sorted(glob.glob(os.path.join(pages_dir, "*.json"))):
        slug = os.path.basename(f)[:-5]
        page = json.load(open(f, encoding="utf-8"))
        v = page["version"]
        patches = []
        for s in v["sections"]:
            for fr in s["layer"]["frames"]:
                for r in fr["rows"]:
                    for m in r["molecules"]:
                        for a in m["atoms"]:
                            d = a.get("data") or {}
                            if a["type"] == "logo" and d.get("src") != logo:
                                patches.append({"atomId": a["_id"], "value": {"data": {"src": logo, "name": LOGO_NAME, "alt": LOGO_ALT}, "styles": {"logo_size": 100}},
                                                "snapshot": {"data": {"src": d.get("src"), "name": d.get("name"), "alt": d.get("alt")}, "styles": {"logo_size": (a.get("styles") or {}).get("logo_size")}}, "note": "logo"})
                            elif a["type"] == "image" and d.get("src") in OLD_LOGOS:
                                patches.append({"atomId": a["_id"], "value": {"data": {"src": door, "name": "tueroeffnung-schluesseldienst.png", "alt": DOOR_ALT}},
                                                "snapshot": {"data": {"src": d.get("src"), "name": d.get("name"), "alt": d.get("alt")}}, "note": "content image (old logo) -> door photo"})
        seo = {}
        if v.get("seoImage") != share:
            seo["seoImage"] = share
        if not patches and not seo:
            continue
        ops = {"slug": slug, "pageId": v["pageId"], "patches": patches}
        if seo: ops["seo"] = seo
        json.dump(ops, open(os.path.join(out_dir, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        n_pages += 1
        print(f"{slug:24} patches={len(patches)} seo={seo}")
    print("pages with ops:", n_pages)

if __name__ == "__main__":
    main()
