#!/usr/bin/env python3
"""Verteilt die Textfassungen so auf die Orte, dass sich keine zwei Ortsseiten zu stark ähneln.

Ausgangspunkt ist die Hash-Zuordnung aus generate_pages.pick(). Danach wird in einer lokalen Suche
jeweils das ähnlichste Seitenpaar genommen und eine Fassung einer der beiden Seiten getauscht, wenn
die größte Ähnlichkeit dadurch sinkt. Ergebnis: seo/tools/varianten.json (von pick() bevorzugt gelesen).

Aufruf: python3 seo/tools/optimize_variants.py [max_runden]
"""
import json, os, re, sys, random, difflib, itertools, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_pages as G

SLOTS = {"title": 4, "desc": 5, "h1": 4, "h2": 3, "herolines": 3, "vorteil0": 3, "vorteil1": 3, "vorteil2": 3, "egh": 4, "pph": 3,
         "hab": 3, "hle": 3, "hfa": 3, "hna": 3, "intro": 6, "teile": 3, "lokal": 4, "leist0": 2, "leist1": 2, "leist2": 2, "leist3": 2,
         "leist4": 2, "leist5": 2, "preis": 4, "konkret": 2, "ablauf": 3, "faqspeed": 2, "faqprice": 2, "faq": 8, "gebiet": 3}
ORDER = [o["slug"] for o in G.D["orte"]]


def words(o):
    k = G.kurz(o)
    t = " ".join(G.all_texts(o)).replace(o["name"], "ORT").replace(k, "ORT").replace(str(o["preis_tueroeffnung"]), "PREIS").replace(str(o["eta"]), "ETA")
    return re.sub(r"\s+", " ", t).split()


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def evaluate(cache, slugs):
    pairs = {}
    for a, b in itertools.combinations(slugs, 2):
        pairs[(a, b)] = sim(cache[a], cache[b])
    return pairs


def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    random.seed(7)
    # Start: aktuelle Zuordnung (Hash oder vorhandene varianten.json)
    G.VARIANTS = {s: {salt: G.pick(s, salt, n) for salt, n in SLOTS.items()} for s in ORDER}
    cache = {s: words(G.ORTE[s]) for s in ORDER}
    pairs = evaluate(cache, ORDER)
    best_max = max(pairs.values())
    print("Start: mean %.3f max %.3f" % (statistics.mean(pairs.values()), best_max))
    for it in range(rounds):
        (a, b), cur = max(pairs.items(), key=lambda kv: kv[1])
        victim = random.choice([a, b])
        salt = random.choice(list(SLOTS))
        old = G.VARIANTS[victim][salt]
        choices = [v for v in range(SLOTS[salt]) if v != old]
        if not choices:
            continue
        G.VARIANTS[victim][salt] = random.choice(choices)
        new_words = words(G.ORTE[victim])
        new_pairs = {}
        for s in ORDER:
            if s == victim:
                continue
            key = (s, victim) if ORDER.index(s) < ORDER.index(victim) else (victim, s)
            new_pairs[key] = sim(cache[s], new_words)
        trial = dict(pairs); trial.update(new_pairs)
        new_max = max(trial.values())
        # akzeptieren, wenn das Maximum sinkt oder gleich bleibt und die Summe der zehn ähnlichsten Paare sinkt
        top_old = sum(sorted(pairs.values())[-10:]); top_new = sum(sorted(trial.values())[-10:])
        if new_max < best_max or (new_max <= best_max and top_new < top_old):
            pairs, cache[victim], best_max = trial, new_words, new_max
        else:
            G.VARIANTS[victim][salt] = old
        if it % 50 == 0:
            print("  Runde %d: mean %.3f max %.3f" % (it, statistics.mean(pairs.values()), best_max))
    print("Ende: mean %.3f max %.3f" % (statistics.mean(pairs.values()), best_max))
    worst = sorted(pairs.items(), key=lambda kv: -kv[1])[:5]
    print("ähnlichste Paare:", [(round(v, 2), a, b) for (a, b), v in worst])
    json.dump(G.VARIANTS, open(os.path.join(HERE, "varianten.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("varianten.json geschrieben")


if __name__ == "__main__":
    main()
