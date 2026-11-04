"""Compare ROBOT/HermiT output with its input, and look for silent individual merging.
Usage: dl_diff.py <dlrun-dir>"""
import sys, os
from collections import defaultdict
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL

D = sys.argv[1]
RBACO = "https://w3id.org/rbaco/bfo/"


def load(name):
    g = Graph(); g.parse(os.path.join(D, name), format="xml"); return g


def lab(g, n):
    l = g.value(n, RDFS.label)
    short = str(n).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
    return f"{l} ({short})" if l else short


def named(n):
    return isinstance(n, URIRef)


for ont in ("rbaco-bfo", "rbaco-bfo-domain"):
    m, r = load(f"{ont}-merged.owl"), load(f"{ont}-reasoned.owl")
    print(f"== {ont}: merged {len(m)} triples, reasoned {len(r)}")
    for p in (RDFS.subClassOf, OWL.equivalentClass):
        new = [(s, o) for s, o in r.subject_objects(p) if named(s) and named(o) and (s, p, o) not in m]
        rbaco_new = [(s, o) for s, o in new if str(s).startswith(RBACO) or str(o).startswith(RBACO)]
        print(f"  new {p.split('#')[-1]} between named classes: {len(new)}; touching RBACO: {len(rbaco_new)}")
        for s, o in sorted(rbaco_new if p == RDFS.subClassOf else new):
            print(f"    {lab(r, s)}  ->  {lab(r, o)}")

for ds in ("us-persons", "code-review", "abac", "rt-policy", "purchase", "probes"):
    m, r = load(f"{ds}-merged.owl"), load(f"{ds}-reasoned.owl")
    inds = set(m.subjects(RDF.type, OWL.NamedIndividual)) | {s for s, o in m.subject_objects(RDF.type)
                                                             if str(s).startswith(RBACO) and "#" in str(s)}
    new = [(s, o) for s, o in r.subject_objects(RDF.type) if s in inds and named(o)
           and (s, RDF.type, o) not in m and o != OWL.NamedIndividual]
    rbaco_new = sorted({(s, o) for s, o in new if str(o).startswith(RBACO)})
    print(f"== {ds}: {len(inds)} individuals, {len(new)} inferred type assertions, {len(rbaco_new)} to RBACO classes")
    by = defaultdict(list)
    for s, o in rbaco_new:
        by[lab(m, o)].append(str(s).rsplit("#", 1)[-1])
    for c, xs in sorted(by.items()):
        print(f"    {c}: {len(xs)}  e.g. {', '.join(sorted(xs)[:4])}")

    # silent merging: properties limited to one value, used with two
    single = set(m.subjects(RDF.type, OWL.FunctionalProperty))
    restricted = defaultdict(set)
    for rr in m.subjects(RDF.type, OWL.Restriction):
        for card in (OWL.cardinality, OWL.maxCardinality, OWL.qualifiedCardinality, OWL.maxQualifiedCardinality):
            v = m.value(rr, card)
            if v is not None and int(v) <= 1:
                restricted[m.value(rr, OWL.onProperty)].add(rr)
    sub = defaultdict(set)
    for a, b in m.subject_objects(RDFS.subPropertyOf):
        sub[b].add(a)

    def down(p, seen=None):
        seen = seen or {p}
        for q in sub.get(p, ()):
            if q not in seen:
                seen.add(q); down(q, seen)
        return seen
    hits = []
    for p in single | set(restricted):
        vals = defaultdict(set)
        for q in down(p):
            for s, o in m.subject_objects(q):
                vals[s].add(o)
        for s, os_ in vals.items():
            if len(os_) > 1 and "#" in str(s):
                hits.append((lab(m, p), "functional" if p in single else "restricted", str(s).rsplit("#", 1)[-1],
                             sorted(str(o).rsplit("#", 1)[-1] for o in os_)))
    for p in m.subjects(RDF.type, OWL.InverseFunctionalProperty):
        vals = defaultdict(set)
        for q in down(p):
            for s, o in m.subject_objects(q):
                vals[o].add(s)
        for o, ss in vals.items():
            if len(ss) > 1:
                hits.append((lab(m, p), "inverse functional", str(o).rsplit("#", 1)[-1], sorted(map(str, ss))))
    print(f"    candidate merges (an individual with 2+ values for a single-valued property): {len(hits)}")
    for h in hits:
        print(f"      {h}")
