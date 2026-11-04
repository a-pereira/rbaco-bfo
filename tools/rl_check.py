"""A partial OWL 2 RL consistency check that needs no Java. The complete check is HermiT, in the DL step of
run_all.sh (run_dl.sh); this one also runs the two witness tests for the is-about bridge, which that step does not.
Usage: rl_check.py <rbaco-bfo-dir>

Materializes a subset of the OWL 2 RL/RDF rules over the ontology closure plus each dataset (data/*.ttl
and data/derived/*.ttl; the probes with purchase.ttl), then reports clashes. Rules applied, named as in the OWL 2 RL profile tables:
  scm-sco/cax-sco (subClassOf), cax-eqc1/2 (equivalentClass), prp-spo1 (subPropertyOf),
  prp-eqp1/2 (equivalentProperty), prp-dom, prp-rng, prp-inv1/2 (inverseOf), prp-symp, prp-trp,
  cls-int1/2 (intersectionOf), cls-uni (unionOf), cls-svf1 (someValuesFrom), cls-avf (allValuesFrom),
  cls-hv1/2 (hasValue).
Clashes reported: cax-dw (disjointWith), cax-adc (AllDisjointClasses), cls-com (complementOf), cls-nothing2.
Not applied: anything producing owl:sameAs (functional properties, max cardinality), cls-maxc, keys,
property chains, datatype reasoning. A clean run therefore does not show consistency; a clash shows
inconsistency."""
import glob, os, sys
from collections import defaultdict
from rdflib import Graph, URIRef, BNode, RDF, RDFS, OWL
from rdflib.collection import Collection

d = sys.argv[1]
onto = Graph()
for f in ["rbaco-bfo.ttl", "rbaco-bfo-domain.ttl"] + sorted(glob.glob(os.path.join(d, "imports", "*.ttl"))):
    onto.parse(f if os.path.isabs(f) else os.path.join(d, f), format="turtle")


def lst(g, node):
    return list(Collection(g, node))


def tbox(g):
    T = {"sub": defaultdict(set), "subp": defaultdict(set), "dom": defaultdict(set), "rng": defaultdict(set),
         "inv": defaultdict(set), "sym": set(), "trans": set(), "inter": {}, "union": {}, "svf": {},
         "avf": {}, "hv": {}, "disj": [], "comp": []}
    for a, b in g.subject_objects(RDFS.subClassOf):
        T["sub"][a].add(b)
    for a, b in g.subject_objects(OWL.equivalentClass):
        T["sub"][a].add(b); T["sub"][b].add(a)
    for a, b in g.subject_objects(RDFS.subPropertyOf):
        T["subp"][a].add(b)
    for a, b in g.subject_objects(OWL.equivalentProperty):
        T["subp"][a].add(b); T["subp"][b].add(a)
    for a, b in g.subject_objects(RDFS.domain):
        T["dom"][a].add(b)
    for a, b in g.subject_objects(RDFS.range):
        T["rng"][a].add(b)
    for a, b in g.subject_objects(OWL.inverseOf):
        T["inv"][a].add(b); T["inv"][b].add(a)
    T["sym"] = set(g.subjects(RDF.type, OWL.SymmetricProperty))
    T["trans"] = set(g.subjects(RDF.type, OWL.TransitiveProperty))
    for c, l in g.subject_objects(OWL.intersectionOf):
        T["inter"][c] = lst(g, l)
    for c, l in g.subject_objects(OWL.unionOf):
        T["union"][c] = lst(g, l)
    for r in g.subjects(RDF.type, OWL.Restriction):
        p = g.value(r, OWL.onProperty)
        for key, pred in (("svf", OWL.someValuesFrom), ("avf", OWL.allValuesFrom), ("hv", OWL.hasValue)):
            v = g.value(r, pred)
            if v is not None:
                T[key][r] = (p, v)
    for a, b in g.subject_objects(OWL.disjointWith):
        T["disj"].append((a, b))
    for x in g.subjects(RDF.type, OWL.AllDisjointClasses):
        T["disj"] += [(a, b) for i, a in enumerate(lst(g, g.value(x, OWL.members)))
                      for b in lst(g, g.value(x, OWL.members))[i + 1:]]
    for a, b in g.subject_objects(OWL.complementOf):
        T["comp"].append((a, b))
    return T


T = tbox(onto)


def materialize(abox):
    types = defaultdict(set)
    edges = set()
    for s, p, o in abox:
        if p == RDF.type:
            types[s].add(o)
        elif isinstance(o, (URIRef, BNode)) and p not in (RDFS.label,):
            edges.add((s, p, o))
    changed = True
    while changed:
        changed = False
        new_edges = set()
        for s, p, o in edges:
            for q in T["subp"].get(p, ()):
                new_edges.add((s, q, o))
            for q in T["inv"].get(p, ()):
                new_edges.add((o, q, s))
            if p in T["sym"]:
                new_edges.add((o, p, s))
        if T["trans"]:
            by = defaultdict(set)
            for s, p, o in edges:
                if p in T["trans"]:
                    by[(p, s)].add(o)
            for (p, s), os_ in list(by.items()):
                for o in list(os_):
                    for o2 in by.get((p, o), ()):
                        new_edges.add((s, p, o2))
        if not new_edges <= edges:
            edges |= new_edges; changed = True
        add = defaultdict(set)
        out = defaultdict(list)
        for s, p, o in edges:
            out[s].append((p, o))
            for c in T["dom"].get(p, ()):
                add[s].add(c)
            for c in T["rng"].get(p, ()):
                add[o].add(c)
        for x, cs in list(types.items()):
            for c in list(cs):
                for b in T["sub"].get(c, ()):
                    add[x].add(b)
                if c in T["inter"]:
                    add[x].update(T["inter"][c])
                if c in T["avf"]:
                    p, v = T["avf"][c]
                    for q, o in out.get(x, ()):
                        if q == p:
                            add[o].add(v)
                if c in T["hv"]:
                    p, v = T["hv"][c]
                    if (x, p, v) not in edges:
                        edges.add((x, p, v)); changed = True
            for c, members in T["inter"].items():
                if all(m in cs for m in members):
                    add[x].add(c)
            for c, members in T["union"].items():
                if any(m in cs for m in members):
                    add[x].add(c)
        for r, (p, v) in T["svf"].items():
            for s, q, o in edges:
                if q == p and (v == OWL.Thing or v in types.get(o, ())):
                    add[s].add(r)
        for r, (p, v) in T["hv"].items():
            for s, q, o in edges:
                if q == p and o == v:
                    add[s].add(r)
        for x, cs in add.items():
            if not cs <= types[x]:
                types[x] |= cs; changed = True
    return types, edges


def label(n):
    l = onto.value(n, RDFS.label)
    return f"{l} ({str(n).rsplit('/', 1)[-1]})" if l else str(n)


def clashes(types):
    found = []
    for x, cs in types.items():
        for a, b in T["disj"]:
            if a in cs and b in cs:
                found.append((x, "disjoint", a, b))
        for a, b in T["comp"]:
            if a in cs and b in cs:
                found.append((x, "complement", a, b))
        if OWL.Nothing in cs:
            found.append((x, "Nothing", OWL.Nothing, OWL.Nothing))
    return found


lines = ["## Partial OWL 2 RL check (tools/rl_check.py)", "",
         f"TBox: {sum(len(v) for v in T['sub'].values())} subclass edges, {len(T['disj'])} disjoint pairs, "
         f"{len(T['svf'])} someValuesFrom, {len(T['inter'])} intersections, {len(T['union'])} unions.", ""]
for f in sorted(glob.glob(os.path.join(d, "data", "*.ttl"))):
    name = os.path.basename(f)[:-4]
    ab = Graph(); ab.parse(f, format="turtle")
    if name == "probes":  # the regression probes extend the purchase workflow
        ab.parse(os.path.join(d, "data", "purchase.ttl"), format="turtle")
    der = os.path.join(d, "data", "derived", f"{name}-derived.ttl")
    if os.path.exists(der):
        ab.parse(der, format="turtle")
    types, edges = materialize(ab)
    cl = clashes(types)
    lines.append(f"{name}: {len(types)} typed nodes, {sum(len(c) for c in types.values())} type assertions after "
                 f"closure, {len(edges)} edges; clashes: {len(cl)}.")
    for x, kind, a, b in cl[:20]:
        lines.append(f"  CLASH {x} : {kind} {label(a)} / {label(b)}")
    cp = sorted(str(x).rsplit("/", 1)[-1] for x, cs in types.items()
                if URIRef("https://w3id.org/rbaco/bfo/RBACO_0001023") in cs)
    if cp:
        lines.append(f"  classified as classroom printer (RBACO_0001023, a defined class): {', '.join(cp)}")
lines.append("")

IAO_ICE, CCO_ICE = URIRef("http://purl.obolibrary.org/obo/IAO_0000030"), URIRef("https://www.commoncoreontologies.org/ont00000958")
IAO_ABOUT, CCO_ABOUT = URIRef("http://purl.obolibrary.org/obo/IAO_0000136"), URIRef("https://www.commoncoreontologies.org/ont00001808")
ENT = URIRef("http://purl.obolibrary.org/obo/BFO_0000001")
W = "https://example.org/rbaco/work#"
for start, about, other in ((IAO_ICE, IAO_ABOUT, CCO_ICE), (CCO_ICE, CCO_ABOUT, IAO_ICE)):
    ab = Graph(); x, y = URIRef(W + "x"), URIRef(W + "y")
    ab.add((x, RDF.type, start)); ab.add((x, about, y)); ab.add((y, RDF.type, ENT))
    types, _ = materialize(ab)
    lines.append(f"Bridge witness: x a {label(start)}, x {label(about)} y  =>  x a {label(other)}: {other in types[x]}.")
lines.append("")
RBACO = "https://w3id.org/rbaco/bfo/RBACO_"
controls = [
    ("asserted: a permission that is also a prohibition", [(RBACO + "0000007",), (RBACO + "0000008",)]),
    ("via the complement in assigned role's definition: an assigned role typed active role",
     [(RBACO + "0000002",), (RBACO + "0000003",)]),
    ("inferred: a role definition (Prescriptive ICE) typed SSD report (Descriptive ICE)",
     [(RBACO + "0000001",), (RBACO + "0000019",)]),
    ("inferred: an access request (a process) typed information content entity (a continuant)",
     [(RBACO + "0000024",), ("https://www.commoncoreontologies.org/ont00000958",)]),
]
for text, cls in controls:
    ab = Graph(); x = URIRef(W + "control")
    for (c,) in cls:
        ab.add((x, RDF.type, URIRef(c)))
    n = len(clashes(materialize(ab)[0]))
    lines.append(f"Negative control ({text}): clashes found: {n}.")
lines.append("")
print("\n".join(lines))
with open(os.path.join(d, "docs", "query-results.md"), "a", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
