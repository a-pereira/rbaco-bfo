"""Print figure labels with positions, and the straight line segments drawn on a page, for reading a figure's
edges without rendering it. Usage: fig_lines.py <pdf> <page-index> <y-min> <y-max>"""
import sys
from pypdf import PdfReader
from pypdf.generic import ContentStream

pdf, pi, ymin, ymax = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
page = PdfReader(pdf).pages[pi]
labels = []


def visit(text, cm, tm, font, size):
    t = text.strip()
    if t:
        x, y = tm[4] * cm[0] + cm[4], tm[5] * cm[3] + cm[5]
        if ymin <= y <= ymax:
            labels.append((round(y, 1), round(x, 1), t))


page.extract_text(visitor_text=visit)
for y, x, t in sorted(labels, key=lambda r: (-r[0], r[1])):
    print(f"LABEL y={y:7} x={x:7} {t}")

# line segments: track the CTM through q/Q/cm and collect m/l pairs
cs = ContentStream(page.get_contents(), page.pdf)
stack, ctm = [], [1, 0, 0, 1, 0, 0]
cur = None
segs = []


def mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return [a * A + b * C, a * B + b * D, c * A + d * C, c * B + d * D, e * A + f * C + E, e * B + f * D + F]


def apply(x, y):
    a, b, c, d, e, f = ctm
    return (a * x + c * y + e, b * x + d * y + f)


for ops, op in cs.operations:
    op = op.decode() if isinstance(op, bytes) else op
    if op == "q":
        stack.append(list(ctm))
    elif op == "Q":
        ctm = stack.pop() if stack else ctm
    elif op == "cm":
        ctm = mul([float(v) for v in ops], ctm)
    elif op == "m":
        cur = apply(float(ops[0]), float(ops[1]))
    elif op == "l" and cur is not None:
        nxt = apply(float(ops[0]), float(ops[1]))
        segs.append((cur, nxt)); cur = nxt
    elif op == "re":
        pass
for (x1, y1), (x2, y2) in segs:
    if ymin <= y1 <= ymax and ymin <= y2 <= ymax and (abs(x1 - x2) + abs(y1 - y2)) > 3:
        print(f"LINE ({x1:6.1f},{y1:6.1f}) -> ({x2:6.1f},{y2:6.1f})")
