"""Write rbaco-bfo-terms.csv in the column layout of BFO 2020's terms document.

Usage: build_terms_csv.py <rbaco-bfo-dir>

Rows: every term RBACO mints (rbaco-bfo.ttl, rbaco-bfo-domain.ttl), then every external term either file
references, with label and definition taken from the imported artifacts in imports/.
"""
import csv, glob, os, sys
from rdflib import Graph, URIRef, BNode, Namespace, RDF, RDFS, OWL
from rdflib.namespace import SKOS, DC

d = sys.argv[1]
OBO = Namespace("http://purl.obolibrary.org/obo/")
RBACO = "https://w3id.org/rbaco/bfo/"
own = Graph()
for f in ("rbaco-bfo.ttl", "rbaco-bfo-domain.ttl"):
    own.parse(os.path.join(d, f), format="turtle")
ext = Graph()
for f in glob.glob(os.path.join(d, "imports", "*.ttl")):
    ext.parse(f, format="turtle")
both = own + ext


def label(n):
    if isinstance(n, BNode):
        return "(class expression)"
    lab = both.value(n, RDFS.label)
    loc = str(n).rsplit("/", 1)[-1]
    return f"{lab} [{loc}]" if lab else loc


def kind(g, s):
    types = set(g.objects(s, RDF.type))
    for t, k in ((OWL.Class, "class"), (OWL.ObjectProperty, "object property"),
                 (OWL.DatatypeProperty, "data property"), (OWL.AnnotationProperty, "annotation property")):
        if t in types:
            return k
    return ""


def named(g, s, p):
    return "; ".join(label(o) for o in g.objects(s, p) if isinstance(o, URIRef))


def text(g, s, *props):
    for p in props:
        v = g.value(s, p)
        if v is not None:
            return " ".join(str(v).split())
    return ""


rows = []
order = {"class": 1, "object property": 2, "data property": 3, "annotation property": 4}
mine = sorted({s for s in own.subjects(DC.identifier, None) if str(s).startswith(RBACO)}, key=str)
counters = {}
for s in sorted(mine, key=lambda s: (order[kind(own, s)], str(s))):
    k = kind(own, s)
    counters[k] = counters.get(k, 0) + 1
    module = "rbaco-bfo-domain" if str(s).split("_")[-1].startswith("0001") else "rbaco-bfo"
    eq = [o for o in own.objects(s, OWL.equivalentClass)]
    rows.append({
        "Section": f"{order[k]}.{counters[k]}",
        "Term/Relational Expression": str(own.value(s, RDFS.label)),
        "Elucidation": "",
        "Definition": text(own, s, SKOS.definition),
        "Examples": text(own, s, SKOS.example),
        "Domain": named(own, s, RDFS.domain),
        "Range": named(own, s, RDFS.range),
        "Synonyms": "",
        "RBACO ID": f"[{own.value(s, DC.identifier)}]",
        "IRI": str(s),
        "Kind": k,
        "Parent": named(own, s, RDFS.subClassOf) or named(own, s, RDFS.subPropertyOf)
                  or ("defined: see OWL" if eq else ""),
        "Provenance": f"new ({module})",
        "Note": text(own, s, SKOS.scopeNote),
    })

referenced = set()
for s, p, o in own:
    for n in (s, p, o):
        if isinstance(n, URIRef) and not str(n).startswith(RBACO) and (
                str(n).startswith(str(OBO)) or "commoncoreontologies" in str(n)) and (n, None, None) in ext \
                and (n, RDF.type, OWL.Ontology) not in ext:
            referenced.add(n)
for i, n in enumerate(sorted(referenced, key=lambda n: (order.get(kind(ext, n), 9), str(n))), 1):
    src = "BFO 2020 core" if "BFO_" in str(n) else "IAO (extract)" if "IAO_" in str(n) else "CCO v2.2"
    rows.append({
        "Section": f"5.{i}", "Term/Relational Expression": str(ext.value(n, RDFS.label)),
        "Elucidation": "", "Definition": text(ext, n, SKOS.definition, OBO.IAO_0000115),
        "Examples": "", "Domain": named(ext, n, RDFS.domain), "Range": named(ext, n, RDFS.range),
        "Synonyms": "", "RBACO ID": "", "IRI": str(n), "Kind": kind(ext, n),
        "Parent": named(ext, n, RDFS.subClassOf) or named(ext, n, RDFS.subPropertyOf),
        "Provenance": f"borrowed ({src})", "Note": "",
    })

out = os.path.join(d, "rbaco-bfo-terms.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print(out, len(rows), "rows:", ", ".join(f"{v} new {k}" for k, v in counters.items()),
      f"; {len(referenced)} borrowed")
missing = [s for s in own.subjects() if isinstance(s, URIRef) and str(s).startswith(RBACO + "RBACO_") and s not in mine]
print("RBACO IRIs without identifier:", [str(m) for m in missing] or "none")
