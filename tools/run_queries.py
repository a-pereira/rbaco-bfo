"""Run every query in queries/ against the example datasets and record the results.

Usage: run_queries.py <rbaco-bfo-dir>

For each dataset, first close its rdf:type triples under rdfs:subClassOf, as the path a/rdfs:subClassOf*
reads them, so that the queries match types with plain rdf:type; the reports and decisions written later
get the same closure. Then give each permission its content (operation, object, object description), and
each conflicting agent designation the agents it counts as one and the constraints and instances it
applies to. Then, at each time at which an assignment, policy issuing act, activation request or access
request occurs: mark what is in force at that time and build the hierarchy snapshot, write SSD conflict
reports, decide the access requests one at a time in IRI order (each after its permission DSD conflict
reports), write task and role DSD conflict reports, and check activation verdicts. Then run the checks and
competency questions, the worklists at the times a dataset names, the regression probes (data/probes.ttl
over data/purchase.ttl, checked against the results each must give), and for the RT policy derive
membership and the analysis bounds to a fixpoint and test three counter-states.

?evalTime in a query file is a placeholder for an xsd:dateTime literal. A query called with a time is
translated once, with a stand-in literal in that place, and each call writes its time over the stand-in,
which gives the algebra the substituted text would (prepare and q below). rdflib evaluates the queries with
two changes to the order of its work, neither of which changes a result (rbaco_eval below). Both rely on how
rdflib stores a translated query, and were checked against its own evaluation under rdflib 7.6.0 only; under
another version the text is parsed at each call and rdflib's evaluator works unchanged, more slowly.
Writes data/derived/<dataset>-derived.ttl, with label comments (annotate_ttl.py), and docs/query-results.md, and
prints the report and the elapsed time, which changes from run to run and so is left out of the file.
Exits 1 if a regression probe fails, after writing both.
"""
import glob, os, re, sys, time
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, XSD, BNode, Variable
from rdflib.plugins.sparql import CUSTOM_EVALS
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.evaluate import evalBGP, evalPart
from rdflib.plugins.sparql.evalutils import _ebv
from rdflib.plugins.sparql.operators import and_
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from pyparsing import ParseResults
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import annotate_ttl

RBACO = Namespace("https://w3id.org/rbaco/bfo/")
RBACOW = Namespace("https://example.org/rbaco/work#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
CCO = Namespace("https://www.commoncoreontologies.org/")
EX = Namespace("https://example.org/rbaco/data/")

d = sys.argv[1]
qdir = os.path.join(d, "queries")
LABELS = annotate_ttl.load_labels(d)
QUERIES = {os.path.basename(f)[:-3]: open(f, encoding="utf-8").read()
           for f in glob.glob(os.path.join(qdir, "*.rq")) if not os.path.basename(f).startswith("_")}
report = []
used = set()


# Two changes to the order in which rdflib does a query's work. Neither changes a solution.
EXISTS = ("Builtin_EXISTS", "Builtin_NOTEXISTS")
LEFT = {"Join": "p1", "LeftJoin": "p1", "Minus": "p1", "Filter": "p", "Extend": "p", "RbacoFilter": "p"}


def join_order(ctx, part):
    """A basic graph pattern's triples in a greedy join order. rdflib's own evaluator sorts them only by how
    many terms are unbound before the first one runs, so two patterns that each bind a variable shared with
    a later pattern are enumerated as a cross product. Here the next pattern is the one with the fewest
    terms unbound by the context and the patterns before it, ties in the order rdflib gives."""
    todo, order, known = list(part.triples), [], set()

    def unbound(t):
        return sum(1 for n in t if isinstance(n, (Variable, BNode)) and n not in known and ctx[n] is None)

    while todo:
        t = todo.pop(min(range(len(todo)), key=lambda i: unbound(todo[i])))
        order.append(t)
        known.update(n for n in t if isinstance(n, (Variable, BNode)))
    return order


def mentioned(e, found):
    """Add to found every variable e mentions, EXISTS patterns included. rdflib keeps a translated EXISTS
    pattern as an attribute of the expression, not as an item, so it is read from there."""
    if isinstance(e, Variable):
        found.add(e)
    elif isinstance(e, dict):
        graph = e.__dict__.get("graph") if isinstance(e, CompValue) and e.name in EXISTS else None
        for k, v in dict.items(e):
            if k != "_vars" and not (graph is not None and k == "graph"):
                mentioned(k, found)
                mentioned(v, found)
        if graph is not None:
            mentioned(graph, found)
    elif isinstance(e, (list, tuple, set, ParseResults)):
        for x in e:
            mentioned(x, found)
    return found


def certain(p):
    """The variables every solution of pattern p binds, as far as its shape shows; a kind of part not
    named here counts as binding none."""
    if p.name == "BGP":
        return {x for t in dict.__getitem__(p, "triples") for x in t if isinstance(x, Variable)}
    if p.name == "Join":
        return certain(dict.__getitem__(p, "p1")) | certain(dict.__getitem__(p, "p2"))
    if p.name == "Union":
        return certain(dict.__getitem__(p, "p1")) & certain(dict.__getitem__(p, "p2"))
    return certain(dict.__getitem__(p, LEFT[p.name])) if p.name in LEFT else set()


def conjuncts(e):
    if isinstance(e, CompValue) and e.name == "ConditionalAndExpression" and dict.get(e, "other"):
        return [x for c in [dict.__getitem__(e, "expr")] + list(dict.__getitem__(e, "other")) for x in conjuncts(c)]
    return [e]


def costly(e):
    if isinstance(e, CompValue):
        return e.name in EXISTS or any(costly(v) for k, v in dict.items(e) if k != "_vars")
    return isinstance(e, (list, tuple)) and any(costly(x) for x in e)


def pushdown(part):
    """Filter part rewritten so that each conjunct of its condition is tested as early as its variables
    allow, or False if that changes nothing. rdflib tests a group's FILTERs after all of the group's joins,
    and evaluates every conjunct, EXISTS patterns included, even when one is already false. Here a conjunct
    goes down the chain of left-hand parts (the first operand of a join, left join or minus, the pattern of
    a filter or BIND), each of whose solutions extends one of the next part's, to the deepest part every
    solution of which binds every variable of the conjunct that the group can bind at all. A conjunct's
    other variables are bound, or not, by the context alone, the same at every part of the chain. Where
    conjuncts meet, those without EXISTS are tested together first, then those with EXISTS one at a time.
    A test keeps the scope rdflib gives the filter: it sees the same bindings, so it has the same value."""
    chain = [dict.__getitem__(part, "p")]
    while chain[-1].name in LEFT:
        chain.append(dict.__getitem__(chain[-1], LEFT[chain[-1].name]))
    may, sure = mentioned(chain[0], set()), [certain(p) for p in chain]
    placed = [[] for _ in chain]
    for c in conjuncts(dict.__getitem__(part, "expr")):
        need = mentioned(c, set()) & may
        placed[max([i for i, s in enumerate(sure) if need <= s], default=0)].append(c)
    if not any(placed[1:]) and (len(placed[0]) < 2 or not any(map(costly, placed[0]))):
        return False
    node = chain[-1]
    for i in range(len(chain) - 1, -1, -1):
        if i < len(chain) - 1:
            node = clone(chain[i], {LEFT[chain[i].name]: node})
        cheap = [c for c in placed[i] if not costly(c)]
        for group in ([cheap] if cheap else []) + [[c] for c in placed[i] if costly(c)]:
            node = CompValue("RbacoFilter", expr=and_(*group), p=node, _vars=dict.get(node, "_vars"),
                             scope=dict.get(part, "_vars"), isolated=not part.no_isolated_scope)
    return node


def clone(p, items):
    c = p.clone()
    c.update(items)
    if p.name == "Filter" and p.no_isolated_scope:
        c["no_isolated_scope"] = True
    return c


def rbaco_filter(ctx, part):
    """rdflib's evalFilter, with the scope of the filter it replaces."""
    expr, scope = dict.__getitem__(part, "expr"), dict.__getitem__(part, "scope")
    isolated = dict.__getitem__(part, "isolated")
    for c in evalPart(ctx, dict.__getitem__(part, "p")):
        if _ebv(expr, c.forget(ctx, _except=scope) if isolated else c):
            yield c


def rbaco_eval(ctx, part):
    if part.name == "BGP":
        return evalBGP(ctx, join_order(ctx, part))
    if part.name == "RbacoFilter":
        return rbaco_filter(ctx, part)
    if part.name == "Filter":
        rewritten = part.__dict__.get("rbaco_pushdown")
        if rewritten is None:
            rewritten = part.__dict__["rbaco_pushdown"] = pushdown(part)
        if rewritten is not False:
            return evalPart(ctx, rewritten)
    raise NotImplementedError()


# The rdflib version the hooks and the prepared queries were checked under (module docstring).
CHECKED = rdflib.__version__ == "7.6.0"
if CHECKED:
    CUSTOM_EVALS["rbaco"] = rbaco_eval


def out(line=""):
    report.append(line)
    print(line)


def time_literal(at):
    """at as an xsd:dateTime literal, built as rdflib's parser builds one, from a plain literal, which keeps
    the lexical form as written ("Z" stays "Z")."""
    return Literal(Literal(f"{at}"), datatype=XSD.dateTime)


EVAL_TIME = re.compile(r"\?evalTime\b")
STAND_IN = time_literal("0001-01-01T00:00:00Z")
PREPARED = {}


def read_in(e, seen):
    """How many literals the parser read from STAND_IN in parse tree e."""
    if isinstance(e, Literal):
        return int(e == STAND_IN)
    if id(e) in seen or not isinstance(e, (dict, list, tuple, ParseResults)):
        return 0
    seen.add(id(e))
    if isinstance(e, CompValue) and e.name == "literal":
        return int(str(dict.get(e, "string")) == str(STAND_IN))
    return sum(read_in(x, seen) for x in (dict.values(e) if isinstance(e, dict) else e))


def walk(e, places, filters, seen):
    """Collect the places in algebra e that hold STAND_IN, as (container, key, index in the tuple there or
    None), and its Filter parts, reading e as rdflib evaluates it: a translated EXISTS pattern from the
    expression's attribute, not from the untranslated item of the same name."""
    if isinstance(e, ParseResults):
        raise TypeError("parse results in a translated query")
    if id(e) in seen or not isinstance(e, (dict, list)):
        return
    seen.add(id(e))
    graph = e.__dict__.get("graph") if isinstance(e, CompValue) and e.name in EXISTS else None
    if graph is not None:
        walk(graph, places, filters, seen)
    if isinstance(e, CompValue) and e.name == "Filter":
        filters.append(e)
    for k, v in (enumerate(e) if isinstance(e, list) else dict.items(e)):
        if k == "_vars" or (graph is not None and k == "graph"):
            continue
        for i, x in (enumerate(v) if isinstance(v, tuple) else [(None, v)]):
            if isinstance(x, Literal) and x == STAND_IN:
                places.append((e, k, i))
            else:
                walk(x, places, filters, seen)


def prepare(name):
    """The query translated once, with STAND_IN for ?evalTime, the places the literal went to and the
    Filter parts; or None, and the text is parsed at each call, if those places are not one for each
    literal the parser read, or rdflib is not the version they were checked under."""
    if not CHECKED:
        return None
    try:
        tree = parseQuery(EVAL_TIME.sub(STAND_IN.n3(), QUERIES[name]))
        n = read_in(tree, set())
        query, places, filters = translateQuery(tree), [], []
        walk(query.algebra, places, filters, set())
    except Exception:
        return None
    return (query, places, filters) if len(places) == n else None


def q(name, g, at=None):
    used.add(name)
    if at is None:
        return g.query(QUERIES[name])
    if name not in PREPARED:
        PREPARED[name] = prepare(name)
    if PREPARED[name] is None:
        return g.query(EVAL_TIME.sub(f'"{at}"^^<http://www.w3.org/2001/XMLSchema#dateTime>', QUERIES[name]))
    query, places, filters = PREPARED[name]
    lit = time_literal(at)
    for c, k, i in places:
        if i is None:
            c[k] = lit
        else:
            t = dict.__getitem__(c, k) if isinstance(c, dict) else c[k]
            c[k] = t[:i] + (lit,) + t[i + 1:]
    for f in filters:
        f.__dict__.pop("rbaco_pushdown", None)
    res = g.query(query)
    res.bindings  # evaluate a SELECT now, before a later call writes another time into the same algebra
    return res


def type_closure(g):
    """Add to g, for each of its rdf:type triples, the superclasses the path a/rdfs:subClassOf* reaches,
    blank nodes included, so that a query can read a type with plain rdf:type. Returns close(triples), which
    does the same for rdf:type triples added to g later. The hierarchy is g's own: no derivation writes
    rdfs:subClassOf, and the derivations whose triples the runner later removes write no rdf:type."""
    memo = {}

    def supers(c):
        if c not in memo:
            seen, todo = set(), [c]
            while todo:
                for p in g.objects(todo.pop(), RDFS.subClassOf):
                    if p not in seen:
                        seen.add(p)
                        todo.append(p)
            memo[c] = seen
        return memo[c]

    def close(triples):
        for s, p, o in triples:
            if p == RDF.type:
                for c in supers(o):
                    g.add((s, RDF.type, c))

    close(list(g.triples((None, RDF.type, None))))
    return close


def short(n):
    if n is None:
        return ""
    s = str(n)
    for pre, ns in (("ex:", EX), ("rbaco:", RBACO)):
        s = s.replace(str(ns), pre)
    return s


TERM = re.compile(r"^(?:[A-Za-z][\w-]*:[^\s,]+|https?://[^\s,]+)$")


def cell(v):
    """A cell's text. Concatenated terms (GROUP_CONCAT, cited regulations) come in no fixed order, so a cell
    whose space-separated tokens are all CURIEs or IRIs has them sorted."""
    s = short(v)
    toks = s.split(" ")
    return " ".join(sorted(toks)) if len(toks) > 1 and all(TERM.match(t) for t in toks) else s


def table(rows, headers, keys=()):
    """keys: the column indexes the rows arrive ordered by; rows tied on them are sorted by their text.
    None sorts every row by its text, for queries without ORDER BY; () keeps the order given."""
    rows = [(r, [cell(v) for v in r]) for r in rows]
    if keys is None:
        rows.sort(key=lambda x: x[1])
    elif keys:
        runs = []
        for r in rows:
            if runs and all(runs[-1][0][0][k] == r[0][k] for k in keys):
                runs[-1].append(r)
            else:
                runs.append([r])
        rows = [x for run in runs for x in sorted(run, key=lambda x: x[1])]
    out("| " + " | ".join(headers) + " |")
    out("|" + "---|" * len(headers))
    for _, cells in rows:
        out("| " + " | ".join(cells) + " |")
    if not rows:
        out("| (no rows) |" + " |" * (len(headers) - 1))
    out()
    return len(rows)


def qtable(name, res):
    """Write a query's result: rows sorted unless the query orders them, and ties broken when it does."""
    names = [str(v) for v in res.vars]
    m = re.search(r"\bORDER\s+BY\s+(.+)", QUERIES[name], re.I)
    order = re.findall(r"\?(\w+)", m.group(1)) if m else None
    if order is None:
        keys = None
    else:
        keys = tuple(names.index(v) for v in order) if all(v in names for v in order) else ()
    return table(list(res), names, keys)


t0 = time.time()
onto = Graph()
for f in ["rbaco-bfo.ttl", "rbaco-bfo-domain.ttl"] + sorted(glob.glob(os.path.join(d, "imports", "*.ttl"))):
    onto.parse(os.path.join(d, f) if not os.path.isabs(f) else f, format="turtle")
out(f"Ontology closure loaded: {len(onto)} triples (rbaco-bfo, rbaco-bfo-domain, BFO 2020 core, 7 CCO modules, IAO extract).")
out()

TIMED = """PREFIX rbaco: <https://w3id.org/rbaco/bfo/> PREFIX obo: <http://purl.obolibrary.org/obo/>
SELECT DISTINCT ?t WHERE { VALUES ?c { rbaco:RBACO_0000024 rbaco:RBACO_0000025 rbaco:RBACO_0000028 rbaco:RBACO_0000031 }
  ?x a ?c ; obo:BFO_0000199/obo:BFO_0000222/rbaco:RBACO_0000205 ?t } ORDER BY ?t"""


def snapshot(g, at, prev):
    """Replace the previous time's in-force facts and hierarchy snapshot (prev) with those at time at.
    Returns the triples added and the number of hierarchy edges."""
    for tr in prev:
        g.remove(tr)
    force = list(q("derive-in-force", g, at))
    for tr in force:
        g.add(tr)
    edges = list(q("derive-hierarchy-snapshot", g, at))
    for tr in edges:
        g.add(tr)
    return force + edges, len(edges)


def run_rbac(name, title, retype=None, brief=False, worklists=(), extra=None, since=None, save_as=None):
    """extra: a second data file read with the first. since: report only what happens at or after this
    time (every time is still evaluated). save_as: write the derived triples under this name even if brief."""
    out(f"## {title}")
    out()
    data = Graph(); data.parse(os.path.join(d, "data", f"{name}.ttl"), format="turtle")
    if extra:
        data.parse(os.path.join(d, "data", f"{extra}.ttl"), format="turtle")
    if retype:
        node, old, new = retype
        data.remove((EX[node], RDF.type, old)); data.add((EX[node], RDF.type, new))
        out(f"Variant: {short(EX[node])} retyped from {short(old)} to {short(new)}.")
        out()
    g = onto + data
    close = type_closure(g)
    derived = Graph()
    for p, ns in (("rbaco", RBACO), ("ex", EX), ("obo", OBO), ("cco", CCO)):
        derived.bind(p, ns)
    for name_ in ("derive-permission-content", "derive-counted-as-one"):
        for tr in q(name_, g):
            g.add(tr)
    shown =lambda t_: since is None or t_ is None or str(t_) >= since
    times = [str(r.t) for r in g.query(TIMED)]
    snap, edges, verdicts = [], 0, []
    for at in times:
        keep = shown(at)
        snap, edges = snapshot(g, at, snap)

        def add(triples):
            n = 0
            for tr in triples:
                g.add(tr); close([tr]); n += 1
                if keep:
                    derived.add(tr)
            return n
        add(q("derive-ssd-conflicts", g, at))
        cover = list(q("derive-regulation-coverage", g, at))
        for tr in cover:
            g.add(tr)
        for _ in range(1000):
            add(q("derive-permission-dsd-conflicts", g, at))
            if not add(q("decide-access", g, at)):
                break
        else:
            raise RuntimeError(f"decide-access did not finish the requests at {at}")
        for tr in cover:
            g.remove(tr)
        add(q("derive-task-dsd-conflicts", g, at))
        add(q("derive-dsd-conflicts", g, at))
        if keep:
            verdicts += [(at, r.areq, r["def"], r.verdict, r.constraint, r.fulfilled, r.consistent)
                         for r in q("decide-activation", g, at)]
    out(f"Evaluation times: {len(times)}; hierarchy snapshot edges at the last: {edges}."
        + (f" Results from {since} on." if since else ""))
    out()
    out("### Role activation requests (decide-activation.rq)")
    out()
    table(verdicts, ["time", "request", "definition", "verdict", "constraint", "fulfilled", "consistent"], keys=(0,))
    out("### Access decisions (decide-access.rq)")
    out()
    rows = g.query("""PREFIX rbaco: <https://w3id.org/rbaco/bfo/> PREFIX obo: <http://purl.obolibrary.org/obo/>
      SELECT ?req ?op ?obj ?cls ?t (GROUP_CONCAT(DISTINCT STR(?cite); separator=" ") AS ?cites) WHERE {
        ?dec rbaco:RBACO_0000112 ?req ; a ?cls . VALUES ?cls { rbaco:RBACO_0000022 rbaco:RBACO_0000023 }
        ?req rbaco:RBACO_0000108 ?op ; obo:BFO_0000199/obo:BFO_0000222/rbaco:RBACO_0000205 ?t .
        OPTIONAL { ?req rbaco:RBACO_0000109 ?obj } OPTIONAL { ?dec rbaco:RBACO_0000113 ?cite } }
      GROUP BY ?req ?op ?obj ?cls ?t ORDER BY ?t ?req""")
    table([(r.req, r.op, r.obj, "grant" if r.cls == RBACO.RBACO_0000022 else "denial",
            " ".join(short(URIRef(c)) for c in str(r.cites).split()) if r.cites else "")
           for r in rows if shown(r.t)],
          ["request", "operation", "object", "decision", "cites"])
    out("### Conflict reports (derive-ssd-conflicts.rq, derive-permission-dsd-conflicts.rq, "
        "derive-task-dsd-conflicts.rq, derive-dsd-conflicts.rq)")
    out()
    rows = g.query("""PREFIX rbaco: <https://w3id.org/rbaco/bfo/> PREFIX obo: <http://purl.obolibrary.org/obo/>
      SELECT ?rep ?cls ?who ?c ?act ?t (GROUP_CONCAT(DISTINCT STR(?r); separator=" ") AS ?members) ?why WHERE {
        ?rep a ?cls . VALUES ?cls { rbaco:RBACO_0000019 rbaco:RBACO_0000020 }
        ?rep rbaco:RBACO_0000124 ?who ; rbaco:RBACO_0000125 ?c ; rbaco:RBACO_0000128 ?act ;
             rbaco:RBACO_0000126|rbaco:RBACO_0000146|rbaco:RBACO_0000147 ?r ;
             rbaco:RBACO_0000204 ?why .
        OPTIONAL { ?act obo:BFO_0000199/obo:BFO_0000222/rbaco:RBACO_0000205 ?t } }
      GROUP BY ?rep ?cls ?who ?c ?act ?t ?why ORDER BY ?rep""")
    table([(r.rep, "SSD" if r.cls == RBACO.RBACO_0000019 else "DSD", r.who, r.c, r.act,
            " ".join(short(URIRef(x)) for x in str(r.members).split()), r.why) for r in rows if shown(r.t)],
          ["report", "kind", "subject", "constraint", "act", "members counted", "justification"], keys=(0,))
    last = times[-1]
    if brief:
        if save_as:
            save_derived(derived, save_as)
        return g, verdicts
    res = q("derive-authorized-members", g, last)
    out(f"### Authorized members at {last} (derive-authorized-members.rq)")
    out()
    table(sorted(((s_, o) for s_, p_, o in res), key=lambda r: (short(r[0]), short(r[1]))),
          ["role definition", "authorized member"])
    out(f"### Checks at {last}")
    out()
    for check in ("check-hierarchy-cycles", "check-limited-hierarchy", "check-constraint-shape",
                  "check-hierarchy-drift", "check-active-roles", "check-task-specs", "check-task-bound-roles",
                  "check-sod-hierarchy", "check-conflict-coverage", "check-designation-chains",
                  "check-asserted-closures"):
        res = q(check, g, last)
        out(f"**{check}.rq**")
        out()
        qtable(check, res)
    out("### Competency questions")
    out()
    for cq in ("cq-role-history", "cq-class-level-permissions", "cq-usable-objects", "cq-least-privilege-slack"):
        res = q(cq, g, last)
        # not len(res): rdflib counts the empty row an aggregate over no groups yields, which iterating skips
        if cq != "cq-role-history" and not list(res):
            continue
        out(f"**{cq}.rq**")
        out()
        qtable(cq, res)
    for at in worklists:
        snap, edges = snapshot(g, at, snap)
        res = q("cq-worklist", g, at)
        out(f"**cq-worklist.rq at {at}**")
        out()
        qtable("cq-worklist", res)
    save_derived(derived, save_as or name)
    return g, verdicts


def save_derived(derived, name):
    os.makedirs(os.path.join(d, "data", "derived"), exist_ok=True)
    derived_path = os.path.join(d, "data", "derived", f"{name}-derived.ttl")
    derived.serialize(derived_path, format="turtle")
    annotate_ttl.annotate_file(derived_path, LABELS)
    out(f"Derived triples written to data/derived/{name}-derived.ttl: {len(derived)}.")
    out()


# What each regression probe in data/probes.ttl must give (build_data.py describes the probes)
PROBE_DECISIONS = {  # access request: (decision, what it cites, or None not to check)
    "tom-req-create-requisition-probe-1": ("grant", None),
    "tom-req-approve-order-probe-1": ("denial", ["pdsd-perms"]),
    "tom-req-approve-order-probe-2": ("grant", None),
    "tom-req-approve-order-probe-3": ("grant", None),
    "tom-req-create-requisition-probe-3": ("denial", ["pdsd-perms"]),
    "harry-req-complete-order-form-probe-4": ("denial", []),
    "dick-req-create-requisition-probe-6": ("grant", None),
    "tom-req-approve-order-probe-6": ("grant", None),
}
PROBE_VERDICTS = {  # activation request: verdict, which must also agree with the data
    "dick-request-activate-sc-probe-5": "allowed",
    "tom-request-activate-apm-probe-5": "allowed",
    "harry-request-activate-apm-probe-8": "allowed",
    "harry-request-activate-sc-probe-8": "refused: task SoD",
}
PROBE_SSD = sorted(f"probe-issue-inh-ssd-conflict-{c}-{who}" for who in ("tom", "dick")
                   for c in ("ssd-auditor-apm", "pssd-approve-audit", "tssd-approve-audit"))
PROBE_ACTIVE = [("harry-manager-active-probe-4", "outlives the assigned role it depends on")]


def run_probes():
    g, verdicts = run_rbac("purchase", "Regression probes (data/probes.ttl over data/purchase.ttl)", brief=True,
                           extra="probes", since="2026-02-01", save_as="probes")
    local = lambda n: str(n).replace(str(EX), "")
    rows = []
    for req, (want, cites) in PROBE_DECISIONS.items():
        dec = EX[f"{req}-decision"]
        kinds = {"grant" for c in g.objects(dec, RDF.type) if c == RBACO.RBACO_0000022} | \
                {"denial" for c in g.objects(dec, RDF.type) if c == RBACO.RBACO_0000023}
        got_cites = sorted(local(c) for c in g.objects(dec, RBACO.RBACO_0000113))
        got = " ".join(sorted(kinds)) + (f" citing {' '.join(got_cites) or 'nothing'}" if cites is not None else "")
        exp = want + (f" citing {' '.join(cites) or 'nothing'}" if cites is not None else "")
        rows.append((req, exp, got))
    seen = {local(r[1]): (str(r[3]), r[6].toPython()) for r in verdicts}
    for areq, want in PROBE_VERDICTS.items():
        verdict, consistent = seen.get(areq, ("(no verdict)", False))
        rows.append((areq, f"{want}, consistent", f"{verdict}, {'consistent' if consistent else 'inconsistent'}"))
    act = EX["probe-issue-inh"]
    got_ssd = sorted(local(r) for r in g.subjects(RBACO.RBACO_0000128, act))
    rows.append(("SSD reports at probe-issue-inh", " ".join(PROBE_SSD), " ".join(got_ssd)))
    got_dsd = sorted(local(r) for r in g.subjects(RBACO.RBACO_0000128, EX["tom-request-activate-apm-probe-5"]))
    rows.append(("DSD reports on tom-request-activate-apm-probe-5", "(none)", " ".join(got_dsd) or "(none)"))
    res = q("check-active-roles", g)
    got_active = sorted((local(r.active), str(r.problem)) for r in res)
    rows.append(("check-active-roles.rq rows", "; ".join(f"{a}: {p}" for a, p in PROBE_ACTIVE),
                 "; ".join(f"{a}: {p}" for a, p in got_active)))
    out("### Probe expectations")
    out()
    failed = [r for r in rows if r[1] != r[2]]
    table([(r[0], r[1], r[2], "pass" if r[1] == r[2] else "FAIL") for r in rows],
          ["probe", "expected", "observed", "result"])
    out(f"Probe expectations: {len(rows) - len(failed)} of {len(rows)} pass.")
    out()
    return failed


def fixpoint(g, name, at, cap=50):
    total = 0
    for i in range(cap):
        new = [tr for tr in q(name, g, at) if tr not in g]
        if not new:
            return total, i
        for tr in new:
            g.add(tr)
        total += len(new)
    raise RuntimeError(f"{name} did not reach a fixpoint in {cap} rounds")


def members(g, role):
    return sorted(short(m) for m in g.objects(EX[role], RBACO.RBACO_0000131))


def rt_state(data, at, label):
    g = onto + data
    type_closure(g)
    for tr in q("derive-in-force", g, at):
        g.add(tr)
    n, rounds = fixpoint(g, "derive-rt-membership", at)
    out(f"*{label}*: {n} membership triples in {rounds} rounds.")
    out()
    table([(r, ", ".join(members(g, r))) for r in
           ("rt-HQ.marketing", "rt-HQ.ops", "rt-HQ.staff", "rt-HQ.marketingDelg", "rt-HR.employee",
            "rt-HR.managers", "rt-HR.manufacturing", "rt-HR.sales")], ["role", "members"])
    return g


def run_rt():
    out("## ROWLBAC Figure 4 RT policy")
    out()
    data = Graph(); data.parse(os.path.join(d, "data", "rt-policy.ttl"), format="turtle")
    at = "2026-01-02T00:00:00Z"
    g = rt_state(data, at, "Current state")
    res = q("check-rt-issuers", g, at)
    out("**check-rt-issuers.rq**"); out()
    table(list(res), [str(v) for v in res.vars])
    n, rounds = fixpoint(g, "derive-rt-bounds", at)
    out(f"derive-rt-bounds.rq: {n} triples in {rounds} rounds.")
    out()
    res = q("rt-security-properties", g, at)
    out("**rt-security-properties.rq**"); out()
    table(list(res), [str(v) for v in res.vars])
    within = sorted((short(a), short(b)) for a, b in g.subject_objects(RBACOW.alwaysWithin) if a != b)
    out("Derived alwaysWithin pairs (non-reflexive): " + "; ".join(f"{a} in {b}" for a, b in within))
    out()
    growth = set(g.objects(EX["rt-analysis"], RBACO.RBACO_0000129))
    shrink = set(g.objects(EX["rt-analysis"], RBACO.RBACO_0000130))
    later = "2026-01-03T00:00:00Z"

    def counter(label, add=None, retire=None):
        cs = Graph(); cs += data
        if add:
            head, member, issuer = add
            assert EX[head] not in growth, f"{head} is growth-restricted"
            st, act = EX["rt-stmt-cs"], EX["rt-cs-issue"]
            cs.add((st, RDF.type, RBACO.RBACO_0000035)); cs.add((st, RBACO.RBACO_0000116, EX[head]))
            cs.add((st, RBACO.RBACO_0000122, EX[member]))
            cs.add((EX[member], RDF.type, CCO.ont00001262))
            cs.add((act, RDF.type, RBACO.RBACO_0000031)); cs.add((act, CCO.ont00001986, st))
            cs.add((act, CCO.ont00001833, EX[issuer]))
        if retire:
            head = data.value(EX[retire], RBACO.RBACO_0000116)
            assert head not in shrink, f"{short(head)} is shrink-restricted"
            act = EX["rt-cs-retire"]
            cs.add((act, RDF.type, RBACO.RBACO_0000032)); cs.add((act, CCO.ont00001921, EX[retire]))
        act = EX["rt-cs-issue"] if add else EX["rt-cs-retire"]
        iv, i0 = EX["rt-cs-interval"], EX["rt-cs-start"]
        cs.add((act, OBO.BFO_0000199, iv)); cs.add((iv, OBO.BFO_0000222, i0))
        cs.add((i0, RBACO.RBACO_0000205, Literal(later, datatype=XSD.dateTime)))
        return rt_state(cs, later, label)

    out("### Counter-states (each respects the analysis's growth and shrink restrictions)")
    out()
    c1 = counter("Access: HR issues HR.manufacturing <- Carol (HR.manufacturing is not growth-restricted)",
                 add=("rt-HR.manufacturing", "rt-Carol", "rt-HR"))
    out(f"Carol in HQ.ops: {'ex:rt-Carol' in members(c1, 'rt-HQ.ops')}; "
        f"Carol in HQ.marketing: {'ex:rt-Carol' in members(c1, 'rt-HQ.marketing')}.")
    out()
    c2 = counter("Availability: HR revokes HR.managers <- Alice (HR.managers is not shrink-restricted)",
                 retire="rt-stmt-14")
    out(f"Alice in HQ.marketing: {'ex:rt-Alice' in members(c2, 'rt-HQ.marketing')}.")
    out()
    c3 = counter("Safety: HR issues HR.sales <- Carol (HR.sales is not growth-restricted)",
                 add=("rt-HR.sales", "rt-Carol", "rt-HR"))
    out(f"Carol in HQ.marketing: {'ex:rt-Carol' in members(c3, 'rt-HQ.marketing')}.")
    out()
    for label, cg in (("current", g), ("access counter-state", c1), ("availability counter-state", c2),
                      ("safety counter-state", c3)):
        emp = set(members(cg, "rt-HR.employee"))
        ok = set(members(cg, "rt-HQ.marketing")) <= emp and set(members(cg, "rt-HQ.ops")) <= emp
        out(f"Restriction holds in the {label}: {ok}.")
    out()


out("# Query results")
out()
out("Generated by tools/run_queries.py; do not edit by hand.")
out()
run_rbac("us-persons", "ROWLBAC section 3.1 scenario (data/us-persons.ttl)")
run_rbac("code-review", "Code change review CR-42 (data/code-review.ttl)")
run_rbac("code-review", "CR-42 variant with same-time DSD counting", brief=True,
         retype=("dsd-submitter-approver", RBACO.RBACO_0000016, RBACO.RBACO_0000015))
run_rbac("abac", "ROWLBAC section 4.1 attribute examples (data/abac.ttl)")
run_rbac("purchase", "Botha and Eloff 2001 purchase order workflow (data/purchase.ttl)",
         worklists=("2026-01-07T09:30:00Z", "2026-01-11T09:30:00Z", "2026-01-11T10:05:00Z"))
failed = run_probes()
run_rt()
unused = sorted(set(QUERIES) - used)
if not CHECKED:
    out(f"rdflib {rdflib.__version__}: queries parsed at each call and evaluated by rdflib alone "
        "(the runner's hooks were checked under 7.6.0 only).")
out(f"Queries run: {len(used)} of {len(QUERIES)}." + (f" Not run: {', '.join(unused)}." if unused else ""))
print(f"Elapsed: {time.time() - t0:.0f} s.")  # printed only: it changes from run to run
with open(os.path.join(d, "docs", "query-results.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(report) + "\n")
if failed:
    print(f"FAILED probe expectations: {len(failed)}", file=sys.stderr)
    sys.exit(1)
