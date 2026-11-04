"""Measurements for the verification report. Usage: measure.py <rbaco-bfo-dir>

Triple counts per file; declared RBACO terms by kind; every borrowed IRI (obo:, cco:) used in rbaco-bfo.ttl
or rbaco-bfo-domain.ttl checked against what the imports declare; ontology metadata."""
import glob, os, sys
from collections import Counter
from rdflib import Graph, URIRef, RDF, OWL

d = sys.argv[1]
OBO, CCO, RBACO = "http://purl.obolibrary.org/obo/", "https://www.commoncoreontologies.org/", "https://w3id.org/rbaco/bfo/"
files = ["rbaco-bfo.ttl", "rbaco-bfo-domain.ttl"] + [os.path.relpath(f, d) for f in sorted(glob.glob(os.path.join(d, "imports", "*.ttl")))] \
    + [os.path.relpath(f, d) for f in sorted(glob.glob(os.path.join(d, "data", "*.ttl")) + glob.glob(os.path.join(d, "data", "derived", "*.ttl")))]
graphs = {}
for f in files:
    g = Graph(); g.parse(os.path.join(d, f), format="turtle"); graphs[f] = g
    print(f"{f.replace(os.sep, '/')}: {len(g)} triples")
for f in ("rbaco-bfo.owl", "rbaco-bfo-domain.owl"):
    g = Graph(); g.parse(os.path.join(d, f), format="xml")
    t = graphs[f.replace(".owl", ".ttl")]
    from rdflib.compare import isomorphic
    print(f"{f}: {len(g)} triples; isomorphic to the Turtle: {isomorphic(g, t)}")

imports = Graph()
for f in files:
    if f.startswith("imports"):
        imports += graphs[f]
declared = {s for s, o in imports.subject_objects(RDF.type)
            if o in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, OWL.NamedIndividual)}
KINDS = {OWL.Class: "class", OWL.ObjectProperty: "object property", OWL.DatatypeProperty: "data property",
         OWL.AnnotationProperty: "annotation property"}
for f in ("rbaco-bfo.ttl", "rbaco-bfo-domain.ttl"):
    g = graphs[f]
    own = Counter(KINDS[o] for s, o in g.subject_objects(RDF.type) if o in KINDS and str(s).startswith(RBACO))
    print(f"{f}: declared RBACO terms: " + ", ".join(f"{v} {k}" for k, v in sorted(own.items())))
    borrowed = {n for tr in g for n in tr if isinstance(n, URIRef) and str(n).startswith((OBO, CCO))}
    missing = sorted(str(n) for n in borrowed if n not in declared and (n, None, None) not in imports)
    print(f"{f}: borrowed IRIs used: {len(borrowed)}; not declared in imports/: {len(missing)}" +
          (f" -> {missing}" if missing else ""))
    for o in g.subjects(RDF.type, OWL.Ontology):
        print(f"{f}: ontology {o}; versionIRI {g.value(o, OWL.versionIRI)}; imports {len(list(g.objects(o, OWL.imports)))}")
