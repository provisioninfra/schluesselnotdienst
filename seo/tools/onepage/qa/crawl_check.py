import json, re, subprocess, sys, html
S="/tmp/claude-0/-home-user-schluesselnotdienst/b61433d6-4144-509c-9875-45e76cdc31dd/scratchpad"
orte=json.load(open("/home/user/schluesselnotdienst/seo/tools/orte.json"))
towns={o["slug"]:o for o in orte["orte"]} if isinstance(orte,dict) and "orte" in orte else {o["slug"]:o for o in orte if isinstance(o,dict) and "slug" in o}
slugs=["", "turoffnung", "impressum", "agb", "datenschutzerklarung"]+sorted(towns.keys())
rows=[]; problems=[]
for s in slugs:
    url=f"https://schluesselnotdienst-baumann.de/{s}"
    out=subprocess.run(["curl","-sS","--compressed","-o",f"{S}/bd/live/{s or 'home'}.html","-w","%{http_code}",url],capture_output=True,text=True)
    code=out.stdout.strip(); h=open(f"{S}/bd/live/{s or 'home'}.html",encoding="utf-8",errors="replace").read()
    title=re.search(r"<title>(.*?)</title>",h,re.S); title=html.unescape(title.group(1).strip()) if title else ""
    desc=re.search(r'<meta name="description" content="(.*?)"',h); desc=html.unescape(desc.group(1)) if desc else ""
    og=re.search(r'<meta property="og:image" content="(.*?)"',h); og=og.group(1) if og else ""
    h1s=re.findall(r"<h1[^>]*>(.*?)</h1>",h,re.S); h1s=[re.sub("<[^>]+>","",x).strip() for x in h1s]
    logos=re.findall(r'<img[^>]*con-kit-component-logo__image[^>]*>',h)
    logo_src=re.search(r'src="([^"]+)"',logos[0]).group(1) if logos else ""
    old=[k for k in ("Inh. Jannes Heino Baumann\"","f9260dc5","a705f219","43162a4e","e750b114","Schlüsselnotdienst Baumann –") if k in h]
    lds=re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S); ldok=True; types=[]
    for x in lds:
        try:
            j=json.loads(x); types+= [n.get("@type") for n in (j.get("@graph") or [j])]
        except Exception as e: ldok=False
    price=towns.get(s,{}).get("preis_tueroeffnung")
    price_ok = (f"{price} €" in h or f"{price}&nbsp;€" in h or f"{price} €" in html.unescape(h)) if price else None
    stale135 = ("135 €" in h) if (price and str(price)!="135") else None
    rows.append((s or "/",code,len(title),len(desc),len(h1s),"4cce306e" in logo_src,"a1152861" in og,old,ldok,types,price,price_ok,stale135))
    if code!="200" or len(h1s)!=1 or "4cce306e" not in logo_src or old or not ldok or price_ok is False or stale135 or len(title)>60 or len(desc)>155 or "a1152861" not in og:
        problems.append(rows[-1])
print("pages:",len(rows),"| problems:",len(problems))
for r in problems: print("PROBLEM", r)
print("sample:", rows[0][:7], rows[0][8:10]); print("sample bleckede:", [r for r in rows if r[0]=="bleckede"][0])
