"""Serialize Turtle ontology files to RDF/XML beside them. Usage: to_rdfxml.py <in.ttl> <out.owl> [...pairs]

rdflib's pretty-xml writer sometimes mangles RDF lists, depending on blank node order (seen on 2026-10-30:
rbaco-bfo-domain.owl, 169 triples in, 173 out). Each file is therefore checked by parsing it back; a failed round
trip is retried, and after three failures the plain xml writer, which does not nest lists, is used instead."""
import sys
from rdflib import Graph
args = sys.argv[1:]
for src, dst in zip(args[0::2], args[1::2]):
    g = Graph(); g.parse(src, format="turtle")
    for attempt, fmt in enumerate(["pretty-xml"] * 3 + ["xml"], 1):
        g.serialize(dst, format=fmt)
        back = Graph(); back.parse(dst, format="xml")
        if g.isomorphic(back):
            break
    print(dst.replace("\\", "/").split("/")[-1], len(g), "triples; round trip",
          "isomorphic" if g.isomorphic(back) else "DIFFERS", f"({fmt}, attempt {attempt})")
