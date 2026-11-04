"""Translate CLIF modules in the BFO 2020 style into Prover9/Mace4 (LADR) formulas.

Conventions of the translation:
  - Each (cl:comment '... [id]' FORMULA) becomes one LADR formula labelled with its axiom ID.
  - (instance-of x U t) with U a constant becomes isa_U(x, t). Universals are then predicates, so a
    model cannot identify two of them, which is what makes Mace4 models of BFO subsets readable.
  - A variable that occurs only in universal positions (the second argument of instance-of, the
    argument of universal, or an equation with another such variable) is expanded over a finite list
    of universals: forall becomes a conjunction and exists a disjunction. (universal U) is then true.
    The translated theory is therefore BFO restricted to the universals in that list. An axiom in which
    such a variable also occurs elsewhere is not translated, and is reported.
  - Hyphens become underscores. Bound variables become x_<name>; other individual constants c_<name>.
Usage as a module: parse_file(path) -> [(id, text, sexpr)]; Translator(universals).formula(sexpr)."""
import itertools, re

TOKEN = re.compile(r"\s+|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|\(|\)|[^\s()]+")


def tokens(text):
    for m in TOKEN.finditer(text):
        t = m.group(0)
        if not t.isspace():
            yield t


def parse(text):
    stack = [[]]
    for t in tokens(text):
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop(); stack[-1].append(done)
        else:
            stack[-1].append(t)
    if len(stack) != 1:
        raise ValueError("unbalanced parentheses")
    return stack[0]


AXIOM_ID = re.compile(r"\[([a-z0-9-]+)\]\s*'?$")


def parse_file(path):
    with open(path, encoding="utf-8") as fh:
        tree = parse(fh.read())
    out = []

    def walk(node):
        if not isinstance(node, list) or not node:
            return
        if node[0] == "cl:comment":
            if len(node) == 3 and isinstance(node[2], list) and node[2] and node[2][0] in ("cl:ttl", "cl:text"):
                walk(node[2])  # the BFO modules wrap the whole text in their header comment
            elif len(node) == 3 and isinstance(node[2], list):
                text = node[1].strip("'")
                m = AXIOM_ID.search(node[1])
                out.append((m.group(1) if m else None, text, node[2]))
            return
        if node[0] in ("cl:outdiscourse", "cl:imports"):
            return
        for child in node[1:] if node[0] in ("cl:ttl", "cl:text") else node:
            walk(child)
    for top in tree:
        walk(top)
    return out


def name(s):
    return s.replace("-", "_").replace(".", "_")


class Untranslatable(Exception):
    pass


class Translator:
    def __init__(self, universals):
        self.universals = list(universals)

    # which positions a variable occupies inside a formula
    def usage(self, f, var, acc):
        if not isinstance(f, list):
            return acc
        head = f[0]
        if head in ("forall", "exists"):
            if var in f[1]:
                return acc
            return self.usage(f[2], var, acc)
        if head in ("and", "or", "not", "if", "iff"):
            for g in f[1:]:
                self.usage(g, var, acc)
            return acc
        args = f[1:]
        for i, a in enumerate(args):
            if a == var:
                if head == "instance-of" and i == 1:
                    acc.add("univ")
                elif head == "universal":
                    acc.add("univ")
                elif head == "=":
                    acc.add("eq")
                else:
                    acc.add("other")
        return acc

    def formula(self, f, env=None, bound=None):
        env = env or {}
        bound = bound or set()
        if not isinstance(f, list):
            raise Untranslatable(f"bare atom {f}")
        head = f[0]
        if head in ("forall", "exists"):
            vs, body = f[1], f[2]
            uvars = [v for v in vs if "univ" in self.usage(body, v, set())]
            for v in uvars:
                if "other" in self.usage(body, v, set()):
                    raise Untranslatable(f"variable {v} is used both as a universal and otherwise")
            ivars = [v for v in vs if v not in uvars]
            combos = list(itertools.product(self.universals, repeat=len(uvars)))
            if len(combos) > 5000:
                raise Untranslatable(f"{len(combos)} expansions")
            parts = []
            for combo in combos:
                env2 = dict(env); env2.update(zip(uvars, combo))
                parts.append(self.formula(body, env2, bound | set(ivars)))
            if not parts:
                inner = "$T" if head == "forall" else "$F"
            else:
                inner = parts[0] if len(parts) == 1 else "(" + (" & " if head == "forall" else " | ").join(parts) + ")"
            q = "all" if head == "forall" else "exists"
            prefix = "".join(f"{q} x_{name(v)} " for v in ivars)
            return f"({prefix}{inner})" if prefix else inner
        if head == "and":
            return "(" + " & ".join(self.formula(g, env, bound) for g in f[1:]) + ")" if len(f) > 1 else "$T"
        if head == "or":
            return "(" + " | ".join(self.formula(g, env, bound) for g in f[1:]) + ")" if len(f) > 1 else "$F"
        if head == "not":
            return "-(" + self.formula(f[1], env, bound) + ")"
        if head == "if":
            return "(" + self.formula(f[1], env, bound) + " -> " + self.formula(f[2], env, bound) + ")"
        if head == "iff":
            return "(" + self.formula(f[1], env, bound) + " <-> " + self.formula(f[2], env, bound) + ")"
        return self.atom(f, env, bound)

    def univ_of(self, a, env, bound):
        if isinstance(a, list):
            raise Untranslatable("function term in universal position")
        if a in env:
            return env[a]
        if a in bound:
            return None
        return a  # a constant universal

    def term(self, a, env, bound):
        if isinstance(a, list):
            raise Untranslatable("function term")
        if a in env:
            raise Untranslatable(f"universal {env[a]} in an individual position")
        if a in bound:
            return f"x_{name(a)}"
        if re.fullmatch(r"\d+", a):
            return a
        return f"c_{name(a)}"

    def atom(self, f, env, bound):
        head, args = f[0], f[1:]
        if head == "instance-of":
            u = self.univ_of(args[1], env, bound)
            if u is None:
                raise Untranslatable("instance-of with a non-universal variable")
            return f"isa_{name(u)}({self.term(args[0], env, bound)}, {self.term(args[2], env, bound)})"
        if head == "universal":
            u = self.univ_of(args[0], env, bound)
            if u is None:
                raise Untranslatable("universal of a non-universal variable")
            return "$T"
        if head == "=":
            ua, ub = (a in env for a in args)
            if ua or ub:
                if not (ua and ub):
                    raise Untranslatable("equation between a universal and an individual")
                return "$T" if env[args[0]] == env[args[1]] else "$F"
            return f"({self.term(args[0], env, bound)} = {self.term(args[1], env, bound)})"
        return f"{name(head)}(" + ", ".join(self.term(a, env, bound) for a in args) + ")"


def signature(f, bound=frozenset(), acc=None):
    """Predicate arities and the constants used in universal positions, from a CLIF formula."""
    acc = acc if acc is not None else {"preds": {}, "univs": set()}
    if not isinstance(f, list):
        return acc
    head = f[0]
    if head in ("forall", "exists"):
        return signature(f[2], bound | set(f[1]), acc)
    if head in ("and", "or", "not", "if", "iff"):
        for g in f[1:]:
            signature(g, bound, acc)
        return acc
    acc["preds"].setdefault(head, set()).add(len(f) - 1)
    if head == "instance-of" and isinstance(f[2], str) and f[2] not in bound:
        acc["univs"].add(f[2])
    if head == "universal" and isinstance(f[1], str) and f[1] not in bound:
        acc["univs"].add(f[1])
    return acc
