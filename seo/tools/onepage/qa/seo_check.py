import json, re, html, glob, os, collections
S="/tmp/claude-0/-home-user-schluesselnotdienst/b61433d6-4144-509c-9875-45e76cdc31dd/scratchpad"
orte=json.load(open("/home/user/schluesselnotdienst/seo/tools/orte.json")); towns={o["slug"]:o for o in (orte if isinstance(orte,list) else orte["orte"])}
problems=collections.defaultdict(list); stats=[]
for f in sorted(glob.glob(f"{S}/bd/live/*.html")):
    slug=os.path.basename(f)[:-5]
    if slug.endswith(".b") or slug.endswith(".c") or slug=="home.html": continue
    if slug not in towns and slug not in ("home","turoffnung","impressum","agb","datenschutzerklarung"): continue
    h=open(f,encoding="utf-8",errors="replace").read()
    url="https://schluesselnotdienst-baumann.de/"+("" if slug=="home" else slug)
    P=problems[slug]
    # canonical / robots / og / twitter / viewport
    can=re.search(r'<link rel="canonical" href="([^"]+)"',h); 
    if not can: P.append("no canonical")
    elif can.group(1).rstrip("/")!=url.rstrip("/"): P.append(f"canonical mismatch {can.group(1)}")
    rob=re.search(r'<meta name="robots" content="([^"]+)"',h)
    if rob and "noindex" in rob.group(1): P.append("noindex!")
    for prop in ("og:title","og:description","og:image","og:url","og:type"):
        if not re.search(rf'<meta property="{prop}" content="[^"]+"',h): P.append(f"missing {prop}")
    if not re.search(r'<meta name="viewport" content="[^"]*width=device-width',h): P.append("viewport")
    if 'lang="de"' not in h[:300]: P.append("lang")
    # headings outline
    heads=[(m.group(1).lower(), re.sub("<[^>]+>","",m.group(2)).strip()) for m in re.finditer(r"<(h[1-6])[^>]*>(.*?)</\1>",h,re.S)]
    levels=[int(t[1]) for t,_ in heads]
    if levels.count(1)!=1: P.append(f"h1 count {levels.count(1)}")
    if levels and levels[0]!=1: P.append(f"first heading is h{levels[0]}")
    prev=1
    for lv in levels:
        if lv>prev+1: P.append(f"heading skip h{prev}->h{lv}"); break
        prev=lv
    empties=[t for t,x in heads if not x]
    if empties: P.append(f"empty headings {len(empties)}")
    # images
    imgs=re.findall(r"<img[^>]*>",h)
    noalt=[i for i in imgs if not re.search(r'alt="[^"]+"',i) and "aria-hidden" not in i and "data-spacer" not in i]
    lazy_logo=[i for i in imgs if "4cce306e" in i]
    if noalt: P.append(f"img without alt: {len(noalt)}")
    # JSON-LD
    for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
        try: j=json.loads(x)
        except Exception as e: P.append("ld+json parse error"); continue
        nodes=j.get("@graph") or [j]
        for n in nodes:
            t=n.get("@type")
            if t=="Service":
                for k in ("name","provider","areaServed","offers"): 
                    if k not in n: P.append(f"Service missing {k}")
                off=n.get("offers",{}); 
                if isinstance(off,dict) and str(off.get("price"))!=str(towns.get(slug,{}).get("preis_tueroeffnung")): P.append(f"Service price {off.get('price')} != {towns.get(slug,{}).get('preis_tueroeffnung')}")
            if t=="FAQPage":
                me=n.get("mainEntity",[]); 
                if len(me)<3: P.append(f"FAQ only {len(me)}")
                for q in me:
                    if not q.get("acceptedAnswer",{}).get("text"): P.append("FAQ answer empty")
            if t=="BreadcrumbList":
                items=n.get("itemListElement",[])
                if not items or items[-1].get("item","").rstrip("/")!=url.rstrip("/"): P.append(f"breadcrumb last item {items[-1].get('item') if items else None}")
            if t=="Locksmith":
                for k in ("name","telephone","address","image","logo","url"):
                    if k not in n: P.append(f"Locksmith missing {k}")
    # FAQ visible text matches JSON-LD? (check that FAQ questions appear in HTML)
    for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
        try: j=json.loads(x)
        except: continue
        for n in (j.get("@graph") or [j]):
            if n.get("@type")=="FAQPage":
                for q in n.get("mainEntity",[]):
                    qt=html.escape(q.get("name",""),quote=False)
                    if q.get("name") not in html.unescape(h) : P.append(f"FAQ question not in page text: {q.get('name')[:40]}")
    # text stats
    txt=re.sub(r"<script.*?</script>|<style.*?</style>","",h,flags=re.S); txt=html.unescape(re.sub(r"<[^>]+>"," ",txt)); txt=re.sub(r"\s+"," ",txt)
    words=len(txt.split())
    internal=len(set(re.findall(r'href="(/[^"#]*|https://schluesselnotdienst-baumann\.de[^"#]*)"',h)))
    stats.append((slug,words,internal,len(imgs),len(noalt)))
    for pat,label in ((" – ","dash"),("nicht nur","nicht nur"),("Experten sagen","vage Autorität")):
        c=txt.count(pat)
        if c and label!="dash": P.append(f"{label} x{c}")
    if txt.count(" – ")>3: P.append(f"many dashes {txt.count(' – ')}")
for slug in sorted(problems):
    if problems[slug]: print(f"{slug:22} {problems[slug]}")
print("pages checked:", len(stats)); 
print("words/internal-links/imgs/noalt:", sorted(stats, key=lambda r:r[1])[:3], "...", sorted(stats, key=lambda r:r[1])[-2:])
