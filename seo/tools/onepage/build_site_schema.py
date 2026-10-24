"""Baut aus seo/04-site-code-head.html (zwei JSON-LD-Blöcke) den @graph für die Site-Einstellung schemaOrg.
Aufruf: python3 build_site_schema.py <head_html> <out_json>"""
import json, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
nodes = []
for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', src, re.S):
    obj = json.loads(m.group(1)); obj.pop("@context", None)
    for k in ("sameAs",):
        if k in obj and (not obj[k] or any("TODO" in str(x) or "XXXX" in str(x) for x in (obj[k] if isinstance(obj[k], list) else [obj[k]]))):
            obj.pop(k)
    nodes.append(obj)
graph = {"@context": "https://schema.org", "@graph": nodes}
json.dump(graph, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("nodes:", [n.get("@type") for n in nodes], "| logo:", nodes[0].get("logo"), "| image:", nodes[0].get("image"))
