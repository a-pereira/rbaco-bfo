"""List inferred subClassOf links between named classes that RBACO does not touch, and which of them
also appear when the imports are reasoned without RBACO. Usage: dl_imported.py <dlrun-dir>"""
import sys, os
from rdflib import Graph, URIRef, RDFS
D = sys.argv[1]
def load(n):
    g = Graph(); g.parse(os.path.join(D, n), format="xml"); return g
m, r = load("rbaco-bfo-merged.owl"), load("rbaco-bfo-reasoned.owl")
base = load("imports-only-reasoned.owl") if os.path.exists(os.path.join(D, "imports-only-reasoned.owl")) else None
def lab(n):
    l = r.value(n, RDFS.label); return f"{l} ({str(n).rsplit('/',1)[-1]})"
for s, o in sorted(r.subject_objects(RDFS.subClassOf)):
    if isinstance(s, URIRef) and isinstance(o, URIRef) and (s, RDFS.subClassOf, o) not in m \
       and "/rbaco/" not in s and "/rbaco/" not in o:
        tag = "" if base is None else ("  [also without RBACO]" if (s, RDFS.subClassOf, o) in base else "  [ONLY WITH RBACO]")
        print(f"{lab(s)} -> {lab(o)}{tag}")
