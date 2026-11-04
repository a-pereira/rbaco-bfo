"""Check a hand-specified finite interpretation against a LADR theory, for scenarios Mace4 does not finish, and test
every formula in it with LADR's clausetester as well.
Usage: check_hand_model.py <theory.in> <spec.py> <clausetester> <out-dir>

<theory.in> is a Mace4 input as run_fol.py writes it. <spec.py> defines N (domain size), CONST (constant -> element)
and EXTRA (atoms to add, as (predicate, (elements...))), and may define GOALS (formulas to evaluate in the
interpretation) and DROP (labels of assumptions to leave out). Primitive predicates hold the facts' positive atoms,
EXTRA, and what forward chaining over atom-to-atom implications adds. A closure written as a biconditional is not
read for atoms, and the consequences of defined predicates are not chained, so EXTRA states both. Defined
predicates (an axiom 'all vars (P(vars) <-> body)', possibly under a condition) are computed by iteration from
empty. Every assumption and goal is then evaluated, and the false ones are printed.

The interpretation is written to <out-dir>/<spec>.interp in Mace4's format, the assumptions as one list to
<spec>-formulas.in (clausetester reads only the first list of a file) and the goals to <spec>-goals.in, and
clausetester evaluates both independently. A clean result (every formula true) shows the theory satisfiable; no
search is involved.

<clausetester> is the path of the binary (clausetester.exe on Windows). On Windows it is linked with a 512 MB stack
(tools/ladr/build_ladr.sh); elsewhere the soft stack limit sets a program's stack, so it is raised to 512 MB for
clausetester when it starts, or to the hard limit if that is lower (tools/ladr/build_ladr_linux.sh)."""
import itertools, os, re, subprocess, sys
from collections import defaultdict
if os.name == "posix":
    import resource
STACK = 512 * 1024 * 1024


def raise_stack():
    """Run in the child before clausetester starts (POSIX only): raise the soft stack limit to STACK, or to the hard
    limit if that is lower."""
    soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
    want = STACK if hard == resource.RLIM_INFINITY else min(STACK, hard)
    if soft != resource.RLIM_INFINITY and soft < want:
        resource.setrlimit(resource.RLIMIT_STACK, (want, hard))


THEORY, SPEC, CT, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
TAG = os.path.splitext(os.path.basename(SPEC))[0]
spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
N, CONST, EXTRA = spec["N"], spec["CONST"], spec.get("EXTRA", [])
GOALS, DROP = spec.get("GOALS", []), set(spec.get("DROP", []))

TOK = re.compile(r"<->|->|!=|[()=,&|-]|[A-Za-z_][A-Za-z0-9_]*|\d+")


class Parser:
    def __init__(self, text):
        self.t, self.i = TOK.findall(text), 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, x=None):
        tok = self.peek()
        if x is not None and tok != x:
            raise SyntaxError(f"expected {x}, got {tok}: {' '.join(self.t)}")
        self.i += 1
        return tok

    def formula(self):
        a = self.imp()
        if self.peek() == "<->":
            self.eat()
            return ("iff", a, self.imp())
        return a

    def imp(self):
        a = self.disj()
        if self.peek() == "->":
            self.eat()
            return ("imp", a, self.imp())
        return a

    def disj(self):
        xs = [self.conj()]
        while self.peek() == "|":
            self.eat(); xs.append(self.conj())
        return xs[0] if len(xs) == 1 else ("or", xs)

    def conj(self):
        xs = [self.unary()]
        while self.peek() == "&":
            self.eat(); xs.append(self.unary())
        return xs[0] if len(xs) == 1 else ("and", xs)

    def unary(self):
        tok = self.peek()
        if tok == "-":
            self.eat()
            return ("not", self.unary())
        if tok in ("all", "exists"):
            self.eat()
            v = self.eat()
            return (tok, v, self.unary())
        if tok == "(":
            self.eat()
            f = self.formula()
            self.eat(")")
            return f
        a = self.term()
        if self.peek() in ("=", "!="):
            op = self.eat()
            e = ("eq", a, self.term())
            return e if op == "=" else ("not", e)
        return ("atom", a[1], a[2] if a[0] == "app" else [])

    def term(self):
        name = self.eat()
        if self.peek() == "(":
            self.eat()
            args = [self.term()]
            while self.peek() == ",":
                self.eat(); args.append(self.term())
            self.eat(")")
            return ("app", name, args)
        return ("sym", name)


# ---------- read the assumptions and the goals ----------
src = open(THEORY, encoding="utf-8").read()
lines, forms = [], []  # lines: the assumption lines as written; forms: (label, text, ast), one per formula
for body in re.findall(r"formulas\(assumptions\)\.\n(.*?)end_of_list\.", src, re.S):
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.search(r"#\s*label\(([^)]*)\)\s*\.\s*$", line)
        label = m.group(1) if m else None
        if label in DROP:
            continue
        lines.append(line)
        text = line[:m.start()] if m else line
        for part in [p.strip() for p in text.split(".") if p.strip()]:
            forms.append((label, part, Parser(part).formula()))
goals = [(g, Parser(g.rstrip(". ")).formula()) for g in GOALS]

used = set(re.findall(r"\bc_[A-Za-z0-9_]+", " ".join(lines + GOALS)))
if used - set(CONST):
    sys.exit(f"no element for {sorted(used - set(CONST))}")
numerals = [int(x) for x in re.findall(r"[(,]\s*(\d+)\s*[),]", " ".join(lines + GOALS))]
if numerals and max(numerals) >= N:
    sys.exit(f"numeral {max(numerals)} is not a domain element when N = {N}")

ARITY = {}


def scan(f):
    k = f[0]
    if k == "atom":
        ARITY[f[1]] = len(f[2])
    elif k == "not":
        scan(f[1])
    elif k in ("and", "or"):
        for x in f[1]:
            scan(x)
    elif k in ("imp", "iff"):
        scan(f[1]); scan(f[2])
    elif k in ("all", "exists"):
        scan(f[2])


for f in [f for _, _, f in forms] + [f for _, f in goals]:
    scan(f)

R = defaultdict(set)
MISSING = object()


def val(t, env):
    name = t[1]
    if name in env:
        return env[name]
    if name in CONST:
        return CONST[name]
    if name.isdigit():
        return int(name)
    raise KeyError(f"no value for {name}")


def ev(f, env):
    k = f[0]
    if k == "atom":
        return tuple(val(a, env) for a in f[2]) in R[f[1]]
    if k == "eq":
        return val(f[1], env) == val(f[2], env)
    if k == "not":
        return not ev(f[1], env)
    if k == "and":
        return all(ev(x, env) for x in f[1])
    if k == "or":
        return any(ev(x, env) for x in f[1])
    if k == "imp":
        return (not ev(f[1], env)) or ev(f[2], env)
    if k == "iff":
        return ev(f[1], env) == ev(f[2], env)
    v, old = f[1], env.get(f[1], MISSING)
    want = k == "exists"
    res = not want
    for e in range(N):
        env[v] = e
        if ev(f[2], env) == want:
            res = want
            break
    if old is MISSING:
        env.pop(v, None)
    else:
        env[v] = old
    return res


def strip_all(f):
    vs = []
    while f[0] == "all":
        vs.append(f[1]); f = f[2]
    return vs, f


# ---------- definitions ----------
DEFS = defaultdict(list)  # P -> [(argvars, cond, rhs)]


def as_def(body, qv):
    if body[0] == "iff" and body[1][0] == "atom":
        args = body[1][2]
        if args and all(a[0] == "sym" and a[1] in qv for a in args) and len({a[1] for a in args}) == len(args):
            return body[1][1], [a[1] for a in args], None, body[2]
    if body[0] == "imp":
        d = as_def(body[2], qv)
        if d and d[2] is None:
            return d[0], d[1], body[1], d[3]
    return None


for label, text, f in forms:
    qv, body = strip_all(f)
    for part in (body[1] if body[0] == "and" else [body]):
        d = as_def(part, set(qv))
        if d:
            P, args, cond, rhs = d
            if set(args) != set(qv):
                continue
            DEFS[P].append((args, cond, rhs))
DEFINED = set(DEFS)

# ---------- primitives: facts, EXTRA, forward chaining ----------
for label, text, f in forms:
    if f[0] == "atom" and f[1] not in DEFINED:
        R[f[1]].add(tuple(val(a, {}) for a in f[2]))
for p, tup in EXTRA:
    R[p].add(tuple(tup))


def atoms_of(f):
    if f[0] == "atom":
        return [f]
    if f[0] == "and" and all(x[0] == "atom" for x in f[1]):
        return f[1]
    return None


HORN = []
for label, text, f in forms:
    qv, body = strip_all(f)
    if body[0] == "imp":
        a, b = atoms_of(body[1]), atoms_of(body[2])
        if a and b and all(x[1] not in DEFINED for x in a + b):
            HORN.append((qv, a, b))
changed = True
while changed:
    changed = False
    for qv, a, b in HORN:
        for combo in itertools.product(range(N), repeat=len(qv)):
            env = dict(zip(qv, combo))
            if all(ev(x, env) for x in a):
                for x in b:
                    tup = tuple(val(t, env) for t in x[2])
                    if tup not in R[x[1]]:
                        R[x[1]].add(tup); changed = True

# ---------- defined predicates, iterated from empty ----------
for P in DEFINED:
    R[P] = set()
for it in range(60):
    changed = False
    for P, defs in DEFS.items():
        new = set()
        for tup in itertools.product(range(N), repeat=ARITY[P]):
            for args, cond, rhs in defs:
                env = dict(zip(args, tup))
                if (cond is None or ev(cond, env)) and ev(rhs, env):
                    new.add(tup)
                    break
        if new != R[P]:
            R[P] = new; changed = True
    if not changed:
        break
print(f"elements {N}; formulas {len(forms)}; {len(DEFINED)} defined predicates, settled after {it + 1} passes; "
      f"{len(HORN)} implications chained")
false = [(label, text) for label, text, f in forms if not ev(f, {})]
print(f"false here: {len(false)}")
for label, text in false:
    print(f"FALSE: {label}: {text[:300]}")
for g, f in goals:
    print(f"goal {g}: {'true' if ev(f, {}) else 'false'} here")

# ---------- write the interpretation and test with clausetester ----------
parts = [f"function({c}, [{CONST[c]}])" for c in sorted(used)]
for p, k in sorted(ARITY.items()):
    cells = [1 if combo in R[p] else 0 for combo in itertools.product(range(N), repeat=k)]
    parts.append(f"relation({p}({','.join('_' for _ in range(k))}), [{','.join(map(str, cells))}])")
ipath = os.path.join(OUT, f"{TAG}.interp")
open(ipath, "w", encoding="utf-8", newline="\n").write(f"interpretation({N}, [number=1, seconds=0], [\n  " + ",\n  ".join(parts) + "]).\n")


def clausetester(name, formulas):
    path = os.path.join(OUT, f"{TAG}-{name}.in")
    open(path, "w", encoding="utf-8", newline="\n").write("formulas(assumptions).\n" + "\n".join(formulas) + "\nend_of_list.\n")
    with open(path, encoding="utf-8") as fin:
        res = subprocess.run([CT, ipath, "commands"], stdin=fin, capture_output=True, text=True,
                             preexec_fn=raise_stack if os.name == "posix" else None)
    out = res.stdout.splitlines()
    summary = [l for l in out if l.startswith("% interp")]
    return (summary[-1] if summary else res.stderr[-500:]), [l for l in out if re.search(r"\.\s+%\s*$", l)]


summary, bad = clausetester("formulas", lines)
print(f"clausetester: {summary}")
for l in bad[:40]:
    m = re.search(r"label\(([^)]*)\)", l)
    print("FALSE:", m.group(1) if m else l[:200])
if GOALS:
    summary, bad = clausetester("goals", [g if g.rstrip().endswith(".") else g + "." for g in GOALS])
    print(f"clausetester, goals: {summary}")
    for l in bad:
        print("FALSE:", l[:200])
