"""Syntax and signature check for a CLIF module in the BFO 2020 style. Usage: check_clif.py <file.cl>
Checks balanced parentheses, that every axiom is closed (no free variables), that every predicate is
declared in cl:outdiscourse, and that each predicate is used with one arity. Prints the counts."""
import re, sys
from collections import defaultdict
src = open(sys.argv[1], encoding="utf-8").read()
# strip quoted strings (comments), keep their IDs
ids = re.findall(r"\[([a-z0-9-]+)\]'", src)
text = re.sub(r"'(?:\\.|[^'\\])*'", "''", src)
tok = re.findall(r"\(|\)|[^\s()]+", text)
def parse(i):
    out = []
    while i < len(tok):
        t = tok[i]
        if t == "(":
            sub, i = parse(i + 1); out.append(sub)
        elif t == ")":
            return out, i + 1
        else:
            out.append(t); i += 1
    return out, i
tree, end = parse(0)
depth = 0
for t in tok:
    depth += t == "(" ; depth -= t == ")"
    assert depth >= 0, "unbalanced: extra )"
assert depth == 0, f"unbalanced: {depth} unclosed ("
KW = {"forall", "exists", "and", "or", "not", "if", "iff", "="}
declared, arity, problems, axioms = set(), defaultdict(set), [], []
def walk(node, bound, top):
    if not isinstance(node, list) or not node:
        return
    h = node[0]
    if h in ("cl:comment",):
        for n in node[2:]:
            if isinstance(n, list) and n and n[0] in ("forall", "exists", "if", "iff", "not", "and", "or"):
                axioms.append(n); walk(n, set(), top)
            else:
                walk(n, bound, top)
        return
    if h in ("cl:ttl", "cl:text"):
        for n in node[1:]:
            walk(n, bound, top)
        return
    if h == "cl:outdiscourse":
        declared.update(node[1:]); return
    if h in ("forall", "exists"):
        for n in node[2:]:
            walk(n, bound | set(node[1]), top)
        return
    if h in KW:
        for n in node[1:]:
            walk(n, bound, top)
        return
    arity[h].add(len(node) - 1)
    for k, a in enumerate(node[1:], 1):
        if isinstance(a, list):
            problems.append(f"nested term in {h}")
        elif h == "instance-of" and k == 2:
            continue  # the universal, a constant (BFO style)
        elif a not in bound and not a.startswith(("rbo-", "rt-", "cco-")) and not re.fullmatch(r"\d+", a):
            problems.append(f"free variable {a} in ({h} ...)")
for form in tree:
    walk(form, set(), True)
used = set(arity)
for p in sorted(used - declared):
    problems.append(f"undeclared predicate {p}")
for p, ar in arity.items():
    if len(ar) > 1:
        problems.append(f"{p} used with arities {sorted(ar)}")
print(f"axioms: {len(axioms)}; axiom IDs: {len(ids)} ({len(set(ids))} distinct); "
      f"predicates used: {len(used)}; declared: {len(declared)}; declared but unused: {sorted(declared - used)}")
for p in sorted(set(problems)):
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
