"""Re-run three of ROWLBAC's own constructs, as the paper prints them, to test claims the critique makes.

Usage: rowlbac_checks.py <rbaco-bfo-dir>

1. Section 3.3.5 DSoD rule (roles as classes), translated from N3 to SPARQL, over the section 3.3
   assertions for Bob. Run twice: on the disjointWith triple as printed, and with its symmetric
   counterpart added (what an engine that materializes OWL's symmetric disjointness would see).
2. Section 3.4.2 ssod/dsod as owl:SymmetricProperty + owl:TransitiveProperty: the closure, and the
   section 3.4.4 SSoD rule fired over it.
3. Figure 5 OWL policy: every axiom is a Boolean combination of class names, so C SubClassOf D is
   entailed iff no truth assignment to the class names satisfies every axiom with C true and D false.
   Brute force over all 2^11 assignments.
Appends its output to docs/query-results.md.
"""
import itertools, os, sys
from rdflib import Graph

d = sys.argv[1]
lines = []


def out(s=""):
    lines.append(s)
    print(s)


PFX = "@prefix : <https://example.org/rowlbac#> . @prefix owl: <http://www.w3.org/2002/07/owl#> .\n" \
      "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
# Section 3.3 and 3.3.3, as printed (Bob's assertion from section 3.3; the hierarchy from 3.3.1).
CLASSES = PFX + """
:Visitor rdfs:subClassOf :USPerson ; :activeForm :ActiveVisitor .
:Resident rdfs:subClassOf :USPerson ; :activeForm :ActiveResident .
:TemporaryResident rdfs:subClassOf :Resident ; :activeForm :ActiveTemporaryResident .
:ActiveVisitor rdfs:subClassOf :ActiveRole, :Visitor .
:ActiveTemporaryResident rdfs:subClassOf :ActiveRole, :TemporaryResident .
:ActiveVisitor owl:disjointWith :ActiveTemporaryResident .
:Bob a :Visitor, :TemporaryResident .
:act1 a :ActivateRole ; :subject :Bob ; :object :Visitor .
:act2 a :ActivateRole ; :subject :Bob ; :object :TemporaryResident .
"""
DSOD_RULE = """PREFIX : <https://example.org/rowlbac#> PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?A ?RNEW ?RCURRENT WHERE {
  ?A a :ActivateRole ; :subject ?S ; :object ?RNEW .
  ?RNEW :activeForm ?ARNEW .
  ?S a ?RCURRENT .
  ?RCURRENT :activeForm ?ARCURRENT .
  ?ARNEW owl:disjointWith ?ARCURRENT . } ORDER BY ?A"""
ACTIVATION_RULE = """PREFIX : <https://example.org/rowlbac#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?ACTION ?ROLE WHERE {
  ?ACTION a :ActivateRole ; :subject ?SUBJ ; :object ?ROLE .
  ?SUBJ a ?ROLE . ?ROLE :activeForm ?AROLE . ?AROLE rdfs:subClassOf :ActiveRole . } ORDER BY ?ACTION"""


def local(n):
    return str(n).split("#")[-1]


out("## ROWLBAC's own rules, re-run (tools/rowlbac_checks.py)")
out()
out("### 1. Section 3.3.5 DSoD rule over Bob (assigned Visitor and Temporary Resident)")
out()
g = Graph(); g.parse(data=CLASSES, format="turtle")
for label, extra in (("disjointWith as printed (one direction)", ""),
                     ("with the symmetric triple added",
                      ":ActiveTemporaryResident owl:disjointWith :ActiveVisitor .")):
    h = Graph(); h += g
    if extra:
        h.parse(data=PFX + extra, format="turtle")
    fired = [(local(r.A), local(r.RNEW), local(r.RCURRENT)) for r in h.query(DSOD_RULE)]
    out(f"*{label}*: ProhibitedRoleActivation fires for " +
        ("; ".join(f"{a} (activating {n}, because Bob is a {c})" for a, n, c in fired) or "nothing") + ".")
    out()
permitted = [(local(r.ACTION), local(r.ROLE)) for r in g.query(ACTIVATION_RULE)]
out("Role activation rule: PermittedRoleActivation fires for " +
    "; ".join(f"{a} (activating {r})" for a, r in permitted) + ".")
out()
out("The rule's ?S a ?RCURRENT matches an assigned role, not an active one, so Bob's first activation "
    "is prohibited although nothing is active. The same act is also classified PermittedRoleActivation.")
out()

out("### 2. Section 3.4.2 ssod as symmetric and transitive")
out()
VALUES = PFX + """
:Resident :ssod :Citizen .
:Visitor :dsod :TemporaryResident .
:Alice :role :Citizen .
"""
g = Graph(); g.parse(data=VALUES, format="turtle")
# Closure of a symmetric + transitive property: (p|^p)+
closure = sorted((local(r.a), local(r.b)) for r in g.query(
    "PREFIX : <https://example.org/rowlbac#> SELECT ?a ?b WHERE { ?a (:ssod|^:ssod)+ ?b }"))
out("ssod closure: " + "; ".join(f"{a} ssod {b}" for a, b in closure) + ".")
dclosure = sorted((local(r.a), local(r.b)) for r in g.query(
    "PREFIX : <https://example.org/rowlbac#> SELECT ?a ?b WHERE { ?a (:dsod|^:dsod)+ ?b }"))
out("dsod closure: " + "; ".join(f"{a} dsod {b}" for a, b in dclosure) + ".")
out()
fired = sorted((local(r.S), local(r.R1), local(r.R2)) for r in g.query(
    """PREFIX : <https://example.org/rowlbac#> SELECT ?S ?R1 ?R2 WHERE {
       ?S :role ?R1 . ?S :role ?R2 . ?R1 (:ssod|^:ssod)+ ?R2 }"""))
out("Section 3.4.4 SSODConflict rule over the closure, with Alice holding only Citizen: fires for " +
    ("; ".join(f"{s} ({a}, {b})" for s, a, b in fired) or "nothing") + ".")
out()

out("### 3. Figure 5 entailments, by brute force")
out()
A = ["marketing", "ops", "marketingDelg", "manufacturersAccess", "employee", "staff", "managers",
     "researchDev", "manufacturing", "sales", "specialPanel"]


def tbox(v):
    m = v
    return all([
        m["marketing"] == (m["managers"] or m["staff"] or m["sales"] or (m["marketingDelg"] and m["employee"])),
        m["ops"] == (m["manufacturing"] or m["managers"]),
        m["marketingDelg"] == m["manufacturersAccess"],
        m["employee"] == (m["manufacturing"] or m["managers"] or m["sales"] or m["researchDev"]),
        (not m["staff"]) or m["marketing"],
        m["staff"] == (m["managers"] or (m["specialPanel"] and m["researchDev"])),
        (not m["managers"]) or (m["ops"] and m["employee"] and m["marketing"] and m["staff"]),
        (not m["researchDev"]) or m["employee"],
        (not m["manufacturing"]) or (m["ops"] and m["employee"]),
        (not (m["specialPanel"] and m["researchDev"])) or m["staff"],
        (not m["sales"]) or (m["employee"] and m["marketing"]),
        (not (m["marketingDelg"] and m["employee"])) or m["marketing"],
    ])


models = [dict(zip(A, bits)) for bits in itertools.product([False, True], repeat=len(A))]
models = [m for m in models if tbox(m)]
out(f"Assignments satisfying all 12 Figure 5 class axioms: {len(models)} of {2 ** len(A)}.")
out()
for label, sub, sup in (("Restriction: marketing SubClassOf employee", "marketing", "employee"),
                        ("Restriction: ops SubClassOf employee", "ops", "employee"),
                        ("Access: ops SubClassOf marketing", "ops", "marketing")):
    cex = [m for m in models if m[sub] and not m[sup]]
    if cex:
        true_ = sorted(k for k, v in cex[0].items() if v)
        out(f"{label}: NOT entailed; {len(cex)} counter-assignments, e.g. true = {{{', '.join(true_)}}}.")
    else:
        out(f"{label}: entailed.")
out()

path = os.path.join(d, "docs", "query-results.md")
with open(path, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
