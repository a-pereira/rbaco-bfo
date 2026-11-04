"""Write the DL negative controls, each a small ontology importing rbaco-bfo-domain.owl.
Usage: make_dl_controls.py <out-dir>"""
import os, sys

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
HEAD = """@prefix rbaco: <https://w3id.org/rbaco/bfo/> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix c: <https://example.org/rbaco/control#> .
<https://example.org/rbaco/control/{name}> a owl:Ontology ; owl:imports rbaco:rbaco-bfo-domain.owl .
"""
controls = {
    # disjoint classes, also caught by the RL pass
    "c1-permission-prohibition": "c:x a rbaco:RBACO_0000007 , rbaco:RBACO_0000008 .\n",
    # exactly-1 'is activated in', with the two instances declared distinct: needs cardinality reasoning
    "c2-two-instances": ("c:ar a rbaco:RBACO_0000003 ; rbaco:RBACO_0000106 c:bp1 , c:bp2 .\n"
                         "c:bp1 a rbaco:RBACO_0000004 . c:bp2 a rbaco:RBACO_0000004 .\n"
                         "c:bp1 owl:differentFrom c:bp2 .\n"),
    # functional datatype property with two different timestamps: needs datatype reasoning
    "c3-two-timestamps": ('c:t a obo:BFO_0000203 ; rbaco:RBACO_0000205 "2026-01-06T09:00:00+00:00"^^xsd:dateTime , '
                          '"2026-01-06T10:00:00+00:00"^^xsd:dateTime .\n'),
    # an unsatisfiable class, to show ROBOT fails on one
    "c4-unsat-class": "c:Both a owl:Class ; rdfs:subClassOf rbaco:RBACO_0000007 , rbaco:RBACO_0000008 .\n",
    # a task specification requiring two distinct role definitions: qualified cardinality exactly 1
    "c5-two-required-roles": ("c:s a rbaco:RBACO_0000040 ; rbaco:RBACO_0000132 c:d1 , c:d2 .\n"
                              "c:d1 a rbaco:RBACO_0000001 . c:d2 a rbaco:RBACO_0000001 . c:d1 owl:differentFrom c:d2 .\n"),
    # a constraint naming two roles and two permissions: it falls under both defined kinds, which are disjoint
    "c6-mixed-set": ("c:c a rbaco:RBACO_0000012 ; rbaco:RBACO_0000114 c:d1 , c:d2 ; rbaco:RBACO_0000134 c:p1 , c:p2 .\n"
                     "c:d1 a rbaco:RBACO_0000001 . c:d2 a rbaco:RBACO_0000001 . c:p1 a rbaco:RBACO_0000007 . c:p2 a rbaco:RBACO_0000007 .\n"
                     "[] a owl:AllDifferent ; owl:distinctMembers ( c:d1 c:d2 c:p1 c:p2 ) .\n"),
    # a same-time DSD over permissions: same-time counting is defined for role sets only
    "c7-same-time-permission-dsd": ("c:c a rbaco:RBACO_0000015 ; rbaco:RBACO_0000134 c:p1 , c:p2 .\n"
                                    "c:p1 a rbaco:RBACO_0000007 . c:p2 a rbaco:RBACO_0000007 . c:p1 owl:differentFrom c:p2 .\n"),
    # a task-bound operation requirement applying within two distinct plans: at most one
    "c8-binding-two-plans": ("c:h a rbaco:RBACO_0000050 ; rbaco:RBACO_0000148 c:o ; rbaco:RBACO_0000115 c:pl1 , c:pl2 .\n"
                             "c:o a obo:IAO_0000104 .\n"
                             "c:pl1 a rbaco:RBACO_0000005 . c:pl2 a rbaco:RBACO_0000005 . c:pl1 owl:differentFrom c:pl2 .\n"),
}
for name, body in controls.items():
    with open(os.path.join(out, name + ".ttl"), "w", encoding="utf-8") as fh:
        fh.write(HEAD.format(name=name) + body)
print("\n".join(controls))
