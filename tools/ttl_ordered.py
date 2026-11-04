"""Write a graph as Turtle with no forward references: every subject block that another block refers to
comes before it.

Blocks follow the order in which the graph's subjects were first added (OrderedGraph records it); before
each block, the blocks it refers to and that are not yet written are written, depth first, in the order
its triples name them. So an act's interval and instants sit just above the act, and the order otherwise
follows the script that built the data. A blank node is written inside the block that refers to it; one
nothing refers to (an owl:AllDifferent axiom) is a block of its own. Within a block, rdflib's formatting
is kept. A reference cycle cannot be ordered and raises ValueError. After writing, the file is parsed back
and must give a graph isomorphic to the one written; check_file reports any forward reference in a file.

Usage as a check: ttl_ordered.py <file.ttl> [...] exits 1 if any file has a forward reference.
"""
import sys
from rdflib import BNode, Graph, URIRef


class OrderedGraph(Graph):
    """A Graph that remembers the order in which subjects first appear in add()."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_seen = {}

    def add(self, triple):
        self.first_seen.setdefault(triple[0], len(self.first_seen))
        return super().add(triple)


def _closure(g, s, seen):
    """Triples of s and of the blank nodes reachable from it."""
    out = []
    for p, o in sorted(g.predicate_objects(s), key=lambda po: (str(po[0]), str(po[1]))):
        out.append((s, p, o))
        if isinstance(o, BNode) and o not in seen:
            seen.add(o)
            out.extend(_closure(g, o, seen))
    return out


def _units(g, first_seen):
    objects = set(g.objects())
    subjects = set(g.subjects())
    units = [s for s in subjects if isinstance(s, URIRef) or (isinstance(s, BNode) and s not in objects)]
    late = len(first_seen)
    return sorted(units, key=lambda s: (first_seen.get(s, late), str(s)))


def _deps(g, u, named):
    seen, deps = set(), []
    for _, _, o in _closure(g, u, set()):
        if isinstance(o, URIRef) and o in named and o != u and o not in seen:
            seen.add(o)
            deps.append(o)
    return deps


def order(g, first_seen=None):
    """The subject blocks of g in writing order."""
    first_seen = first_seen if first_seen is not None else getattr(g, "first_seen", {})
    units = _units(g, first_seen)
    named = {u for u in units if isinstance(u, URIRef)}
    done, active, out = set(), set(), []

    def visit(u):
        if u in done:
            return
        if u in active:
            raise ValueError(f"reference cycle through {u}")
        active.add(u)
        for d in _deps(g, u, named):
            visit(d)
        active.discard(u)
        done.add(u)
        out.append(u)

    for u in units:
        visit(u)
    return out


def check_file(path):
    """Parse a Turtle file and return its forward references: [(subject, later subject it refers to)].
    Block positions are read from the text: a block starts at a line beginning with a term."""
    import re
    g = Graph()
    g.parse(path, format="turtle")
    ns = dict(g.namespaces())
    pos = {}
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            m = re.match(r"([A-Za-z][\w-]*)?:([\w.-]*[\w-])\s", line) or re.match(r"<([^>]+)>\s", line)
            if not m:
                continue
            iri = URIRef(m.group(1)) if line.startswith("<") else URIRef(str(ns[m.group(1) or ""]) + m.group(2))
            pos.setdefault(iri, i)
    named = {s for s in g.subjects() if isinstance(s, URIRef)}
    missing = named - set(pos)
    if missing:
        raise ValueError(f"{path}: {len(missing)} subjects whose block start was not found")
    bad = []
    for s in named:
        for o in _deps(g, s, named):
            if pos[o] > pos[s]:
                bad.append((s, o))
    return bad


def write(g, path):
    """Write g to path in dependency order; return the number of blocks."""
    blocks = order(g)
    chunks = []
    for u in blocks:
        sub = Graph(bind_namespaces="none")
        for prefix, ns in g.namespaces():
            sub.bind(prefix, ns, override=True, replace=True)
        for t in _closure(g, u, set()):
            sub.add(t)
        text = sub.serialize(format="turtle")
        body = "\n".join(ln for ln in text.splitlines() if not ln.startswith("@prefix")).strip()
        chunks.append(body)
    head = [ln for ln in g.serialize(format="turtle").splitlines() if ln.startswith("@prefix")]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(head) + "\n\n" + "\n\n".join(chunks) + "\n")
    back = Graph()
    back.parse(path, format="turtle")
    if not back.isomorphic(g):
        raise ValueError(f"{path}: the ordered file does not parse to the graph written")
    return len(blocks)


if __name__ == "__main__":
    failed = 0
    for p in sys.argv[1:]:
        bad = check_file(p)
        name = p.replace("\\", "/").split("/")[-1]
        print(f"{name}: {len(bad)} forward references" + "".join(f"\n   {s} -> {o}" for s, o in bad[:5]))
        failed += bool(bad)
    sys.exit(1 if failed else 0)
