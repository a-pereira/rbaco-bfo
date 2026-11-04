"""First-order checks of clif/rbo-access.cl with Prover9 and Mace4 (LADR 2009-11A).
Usage: run_fol.py <rbo-dir> <bin-dir-with-prover9-and-mace4> <work-dir> <rbo-domain-classified.owl>

The classified OWL is the output of a DL reasoner (HermiT through ROBOT) over rbo-domain.ttl and its imports;
it supplies the bridge axioms from RBO's universals to BFO's. Writes LADR inputs and outputs to <work-dir>
and the summary to docs/fol-results.md.

Theories:
  RBO     the axioms of rbo-access.cl. The Prover9 entailments after the first take access_axioms: all but
          [rbo-s6], which the first derives, and the RT axioms [rbo-t1] to [rbo-t5]
  BRIDGE  isa_<rbo universal>(x,t) -> isa_<bfo ancestor>(x,t), from the classified OWL, plus the OWL axiom
          that an active role specifically depends on an assigned role (rbo.ttl, RBO_0000003)
  BFO     the BFO 2020 CLIF modules that constrain RBO's signature (see MODULES), translated by clif2ladr.py,
          with universal variables expanded over the universals in play (see in_play)"""
import glob, itertools, os, re, subprocess, sys, time
from rdflib import Graph, URIRef, RDFS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clif2ladr import parse_file, signature, Translator, Untranslatable

R, BIN, W, OWLF = sys.argv[1:5]
os.makedirs(W, exist_ok=True)
CLIF = os.path.join(R, "imports", "bfo-clif")
MODULES = ["existence-instantiation", "specific-dependency", "generic-dependence", "participation",
           "occurrent-mereology", "temporal-region", "order", "continuant-mereology", "universal-declaration"]
# universal-declaration axioms satisfied by construction under the isa encoding, or not translatable
BY_CONSTRUCTION = {"xtf-1": "universals are pairwise distinct: they are predicate names, not domain elements",
                   "qkp-1": "universals are not particulars: they are not domain elements at all"}
RBO_IRI = {}  # CLIF name -> RBO IRI, from the name-mapping header of rbo-access.cl
with open(os.path.join(R, "clif", "rbo-access.cl"), encoding="utf-8") as fh:
    for a, b in re.findall(r"(rbo-[a-z-]+)\s+(RBO_\d{7})", fh.read()):
        RBO_IRI[a] = "https://example.org/rbac-bfo/" + b

# ---------- bridge from the classified OWL ----------
g = Graph(); g.parse(OWLF, format="xml")
OBO = "http://purl.obolibrary.org/obo/BFO_"


def ancestors(c):
    seen, todo = set(), [c]
    while todo:
        x = todo.pop()
        for y in g.objects(x, RDFS.subClassOf):
            if isinstance(y, URIRef) and y not in seen:
                seen.add(y); todo.append(y)
    return seen


rbo_univs = sorted(set().union(*(signature(sx)["univs"] for _, _, sx in parse_file(os.path.join(R, "clif", "rbo-access.cl")))))
bridge = []
for u in rbo_univs:
    if u not in RBO_IRI:
        continue
    for a in sorted(ancestors(URIRef(RBO_IRI[u]))):
        if str(a).startswith(OBO):
            bfo = str(g.value(a, RDFS.label)).replace(" ", "-")
            bridge.append((f"owl-{u}-{bfo}", f"(all x all t (isa_{u.replace('-', '_')}(x, t) -> isa_{bfo.replace('-', '_')}(x, t)))"))
bridge.append(("owl-active-role-sdep",
               "(all a all t (isa_rbo_active_role(a, t) -> (exists r (isa_rbo_assigned_role(r, t) & specifically_depends_on(a, r)))))"))
bridge_univs = {m.group(1).replace("_", "-") for _, f in bridge for m in re.finditer(r"isa_([a-z_]+)\(", f)}

# ---------- BFO, restricted to the universals in play ----------
mods = {m: parse_file(os.path.join(CLIF, m + ".cl")) for m in MODULES}
decl = mods["universal-declaration"]
sup = {}
for aid, text, sx in decl:
    m = re.match(r"([a-z-]+) is subclass of ([a-z-]+) \[", text)
    if m:
        sup.setdefault(m.group(1), set()).add(m.group(2))
# in play: RBO's universals, their BFO ancestors, the temporal regions the time arguments range over,
# material entity for the bearers, and every BFO superclass of those
in_play = set(rbo_univs) | bridge_univs | {"temporal-instant", "temporal-interval", "material-entity"}
changed = True
while changed:
    changed = False
    for u in list(in_play):
        for s in sup.get(u, ()):
            if s not in in_play:
                in_play.add(s); changed = True
tr = Translator(sorted(in_play))
# BFO-SIG: the BFO axioms stated wholly in RBO's BFO vocabulary, i.e. using no relation outside RBO_PREDS
# besides instance-of. The full set (BFO) is also kept; Mace4 cannot search it at the sizes the scenarios need.
RBO_PREDS = {"exists-at", "concretizes", "is-concretized-by", "inheres-in", "bearer-of", "specifically-depends-on",
             "specifically-depended-on-by", "participates-in", "has-participant", "occurrent-part-of",
             "has-occurrent-part", "occupies-temporal-region", "temporal-part-of", "has-temporal-part",
             "has-first-instant", "precedes", "particular", "universal", "="}
bfo_sig = []
bfo, skipped = [], []
for m, axs in mods.items():
    for aid, text, sx in axs:
        if aid in BY_CONSTRUCTION:
            skipped.append((m, aid, BY_CONSTRUCTION[aid])); continue
        if m == "universal-declaration" and not signature(sx)["univs"] <= in_play:
            skipped.append((m, aid, "names a universal not in play")); continue
        try:
            f = tr.formula(sx)
        except Untranslatable as e:
            skipped.append((m, aid, str(e))); continue
        bfo.append((aid, f))
        if set(signature(sx)["preds"]) - {"instance-of"} <= RBO_PREDS:
            bfo_sig.append((aid, f))
rbo = [(aid, tr.formula(sx)) for aid, text, sx in parse_file(os.path.join(R, "clif", "rbo-access.cl"))]


def lst(name, items):
    return f"formulas({name}).\n" + "".join(f"{f} # label({lab.replace('-', '_')}).\n" for lab, f in items) + "end_of_list.\n"


def facts(text):
    out = []
    for i, line in enumerate(l.strip() for l in text.strip().splitlines()):
        if line and not line.startswith("%"):
            out.append((f"fact{i}", line.rstrip(".")))
    return out


# ---------- scenarios ----------
# CR-42 if Dana's approver activation had been allowed: two active roles, at two instants of the review
CR42 = """
isa_material_entity(c_dana, c_t1). isa_material_entity(c_dana, c_t2).
isa_temporal_instant(c_t1, c_t1). isa_temporal_instant(c_t2, c_t2). c_t1 != c_t2.
isa_temporal_interval(c_u, c_u). occupies_temporal_region(c_cr42, c_u).
temporal_part_of(c_t1, c_u). temporal_part_of(c_t2, c_u). precedes(c_t1, c_t2).
isa_rbo_business_process(c_cr42, c_u).
isa_rbo_role_definition(c_dsub, c_u). isa_rbo_role_definition(c_dappr, c_u). c_dsub != c_dappr.
isa_rbo_assigned_role(c_rsub, c_t1). inheres_in(c_rsub, c_dana). concretizes(c_rsub, c_dsub, c_t1).
isa_rbo_assigned_role(c_rappr, c_t2). inheres_in(c_rappr, c_dana). concretizes(c_rappr, c_dappr, c_t2).
isa_rbo_active_role(c_a1, c_t1). inheres_in(c_a1, c_dana). rbo_activated_in(c_a1, c_cr42). concretizes(c_a1, c_dsub, c_t1). specifically_depends_on(c_a1, c_rsub).
isa_rbo_active_role(c_a2, c_t2). inheres_in(c_a2, c_dana). rbo_activated_in(c_a2, c_cr42). concretizes(c_a2, c_dappr, c_t2). specifically_depends_on(c_a2, c_rappr).
rbo_constrains(c_dsd, c_dsub). rbo_constrains(c_dsd, c_dappr). rbo_has_cardinality(c_dsd, 2).
-(exists p rbo_applies_within(c_dsd, p)).
rbo_in_force(c_dsd, c_t1). rbo_in_force(c_dsd, c_t2). rbo_in_force(c_dsub, c_t1). rbo_in_force(c_dappr, c_t2).
"""
WHOLE ="isa_rbo_whole_instance_dsd(c_dsd, c_u).\n"
SAME = "isa_rbo_same_time_dsd(c_dsd, c_u).\n"
# closure: Dana's only active roles are a1 at t1 and a2 at t2, each concretizing only its own definition
CLOSE = """
(all a all t (isa_rbo_active_role(a, t) & inheres_in(a, c_dana) -> (a = c_a1 & t = c_t1) | (a = c_a2 & t = c_t2))).
(all d all t (concretizes(c_a1, d, t) -> d = c_dsub)). (all d all t (concretizes(c_a2, d, t) -> d = c_dappr)).
c_a1 != c_a2.
-(exists t isa_rbo_whole_instance_dsd(c_dsd, t)).
"""
# critique finding 16: Bob holds Visitor and Work Visa Holder active; WVH is senior to Temporary Resident
VISA = """
isa_temporal_instant(c_t, c_t).
isa_rbo_role_definition(c_vis, c_t). isa_rbo_role_definition(c_tr, c_t). isa_rbo_role_definition(c_wvh, c_t).
c_vis != c_tr. c_vis != c_wvh. c_tr != c_wvh.
rbo_in_force(c_s, c_t). rbo_has_senior(c_s, c_wvh). rbo_has_junior(c_s, c_tr).
rbo_in_force(c_vis, c_t). rbo_in_force(c_tr, c_t). rbo_in_force(c_wvh, c_t). rbo_in_force(c_dsd, c_t).
isa_rbo_active_role(c_av, c_t). inheres_in(c_av, c_bob). rbo_activated_in(c_av, c_bobrev). concretizes(c_av, c_vis, c_t).
isa_rbo_active_role(c_aw, c_t). inheres_in(c_aw, c_bob). rbo_activated_in(c_aw, c_bobrev). concretizes(c_aw, c_wvh, c_t).
isa_rbo_same_time_dsd(c_dsd, c_t). rbo_constrains(c_dsd, c_vis). rbo_constrains(c_dsd, c_tr). rbo_has_cardinality(c_dsd, 2).
(all d (rbo_constrains(c_dsd, d) -> d = c_vis | d = c_tr)).
-(exists p rbo_applies_within(c_dsd, p)).
(all a all t (isa_rbo_active_role(a, t) & inheres_in(a, c_bob) -> a = c_av | a = c_aw)).
(all d all t (concretizes(c_av, d, t) -> d = c_vis)). (all d all t (concretizes(c_aw, d, t) -> d = c_wvh)).
-(exists t isa_rbo_whole_instance_dsd(c_dsd, t)).
"""
# Alice as Citizen asks to vote: the permission is assigned to US Person, a junior of Citizen
VOTE = """
isa_rbo_role_definition(c_citizen, c_t). isa_rbo_role_definition(c_usp, c_t). c_citizen != c_usp.
rbo_in_force(c_s, c_t). rbo_has_senior(c_s, c_citizen). rbo_has_junior(c_s, c_usp).
isa_rbo_active_role(c_a, c_t). inheres_in(c_a, c_alice). rbo_activated_in(c_a, c_rev). concretizes(c_a, c_citizen, c_t).
rbo_has_requester(c_q, c_alice). occurrent_part_of(c_q, c_rev). occupies_temporal_region(c_q, c_uq). has_first_instant(c_uq, c_t).
rbo_requests_operation(c_q, c_vote). rbo_has_operation(c_g, c_vote). rbo_assigned_to(c_g, c_usp).
-(exists b rbo_has_access_object(c_g, b)). -(exists e rbo_has_object_description(c_g, e)). -(exists b rbo_requests_access_to(c_q, b)).
(all k -(occurrent_part_of(c_q, k) & (exists u isa_rbo_task_instance(k, u)))).
isa_rbo_access_permission(c_g, c_t).
(all h all t (isa_rbo_access_prohibition(h, t) -> -rbo_covers(h, c_q))).
rbo_in_force(c_citizen, c_t). rbo_in_force(c_usp, c_t). rbo_in_force(c_g, c_t).
(all h all o -rbo_requires_task_binding(h, o)).
(all c all u -isa_rbo_dsd_constraint(c, u)).
"""
# Botha and Eloff 2001. po-2: Tom activates APM alone; the hierarchy reaches Stock Controller through Buyer
BYPASS = """
isa_temporal_instant(c_t, c_t). isa_temporal_interval(c_u, c_u).
isa_rbo_role_definition(c_dsc, c_t). isa_rbo_role_definition(c_dbuy, c_t). isa_rbo_role_definition(c_dapm, c_t).
c_dsc != c_dapm. c_dsc != c_dbuy. c_dbuy != c_dapm.
rbo_in_force(c_s1, c_t). rbo_has_senior(c_s1, c_dapm). rbo_has_junior(c_s1, c_dbuy).
rbo_in_force(c_s2, c_t). rbo_has_senior(c_s2, c_dbuy). rbo_has_junior(c_s2, c_dsc).
rbo_in_force(c_dsc, c_t). rbo_in_force(c_dbuy, c_t). rbo_in_force(c_dapm, c_t). rbo_in_force(c_dsd, c_t).
isa_rbo_active_role(c_a, c_t). inheres_in(c_a, c_tom). rbo_activated_in(c_a, c_po2). concretizes(c_a, c_dapm, c_t).
isa_rbo_whole_instance_dsd(c_dsd, c_u). rbo_constrains(c_dsd, c_dsc). rbo_constrains(c_dsd, c_dapm). rbo_has_cardinality(c_dsd, 2).
(all d (rbo_constrains(c_dsd, d) -> d = c_dsc | d = c_dapm)).
-(exists p rbo_applies_within(c_dsd, p)).
(all a all t (isa_rbo_active_role(a, t) & inheres_in(a, c_tom) -> a = c_a)).
(all d all t (concretizes(c_a, d, t) -> d = c_dapm)).
(all g all t -isa_rbo_dynamic_designation(g, t)).
"""
# po-3: the same two requests granted, each citing one permission of a dynamic permission set. The two differ
# in operation, so in content ([rbo-s17])
PERM_DSD = """
isa_rbo_dsd_constraint(c_pd, c_u). rbo_has_cardinality(c_pd, 2). -(exists p rbo_applies_within(c_pd, p)).
rbo_in_force(c_pd, c_t2).
rbo_constrains_permission(c_pd, c_p1). rbo_constrains_permission(c_pd, c_p2).
rbo_has_operation(c_p1, c_create). rbo_has_operation(c_p2, c_approve). -rbo_has_operation(c_p2, c_create).
occurrent_part_of(c_q1, c_po3). cco_has_agent(c_q1, c_tom). -(exists y rbo_on_behalf_of(c_q1, y)).
rbo_decides_on(c_d1, c_q1). isa_rbo_access_grant(c_d1, c_t1). rbo_cites(c_d1, c_p1).
occurrent_part_of(c_q2, c_po3). cco_has_agent(c_q2, c_tom). -(exists y rbo_on_behalf_of(c_q2, y)).
rbo_decides_on(c_d2, c_q2). isa_rbo_access_grant(c_d2, c_t2). rbo_cites(c_d2, c_p2).
"""
# po-10: Tom completed the form; were Dick to approve it, Dick and Tom count as one in this plan
TASK_DSD = """
isa_rbo_dsd_constraint(c_td, c_u). rbo_has_cardinality(c_td, 2). rbo_applies_within(c_td, c_plan).
rbo_constrains_task(c_td, c_s1). rbo_constrains_task(c_td, c_s2). c_s1 != c_s2. cco_prescribed_by(c_po10, c_plan).
occurrent_part_of(c_k1, c_po10). cco_prescribed_by(c_k1, c_s1). cco_has_agent(c_k1, c_tom). -(exists y rbo_on_behalf_of(c_k1, y)).
occurrent_part_of(c_k2, c_po10). cco_prescribed_by(c_k2, c_s2). cco_has_agent(c_k2, c_dick). -(exists y rbo_on_behalf_of(c_k2, y)).
isa_rbo_dynamic_designation(c_g, c_u). rbo_designates_agent(c_g, c_tom). rbo_designates_agent(c_g, c_dick).
-(exists c2 rbo_applies_to_constraint(c_g, c2)). rbo_applies_within(c_g, c_plan).
rbo_in_force(c_td, c_t). rbo_in_force(c_g, c_t).
"""
# po-11: the approval robot approves on Tom's behalf
HUMAN = """
rbo_requires_human(c_h, c_s). -(exists p rbo_applies_within(c_h, p)).
cco_prescribed_by(c_k, c_s). occurrent_part_of(c_k, c_po11). cco_has_agent(c_k, c_bot). rbo_on_behalf_of(c_k, c_tom).
(all t -isa_cco_person(c_bot, t)).
occupies_temporal_region(c_k, c_uk). has_first_instant(c_uk, c_t0). rbo_in_force(c_h, c_t0).
"""
# lemma: with no designations, a static task set is violated exactly when the role set of the definitions its
# tasks require is, if the tasks require distinct definitions and both constraints are in force. Excluding static designations alone is not enough:
# [rbo-u1] matches kinds at any times, so a dynamic designation applies to a constraint that is an SSD constraint
# at one time and a DSD constraint at another, which rbo.ttl's disjointness (RBO_0000013, RBO_0000014) does not
# exclude once translated per time
TASK_SSD = """
isa_rbo_ssd_constraint(c_ct, c_t). rbo_has_cardinality(c_ct, 2).
isa_rbo_ssd_constraint(c_cr, c_t). rbo_has_cardinality(c_cr, 2).
rbo_constrains_task(c_ct, c_s1). rbo_constrains_task(c_ct, c_s2). (all s (rbo_constrains_task(c_ct, s) -> s = c_s1 | s = c_s2)).
isa_rbo_task_specification(c_s1, c_t). isa_rbo_task_specification(c_s2, c_t).
rbo_requires_role(c_s1, c_d1). rbo_requires_role(c_s2, c_d2). c_d1 != c_d2.
rbo_constrains(c_cr, c_d1). rbo_constrains(c_cr, c_d2). (all d (rbo_constrains(c_cr, d) -> d = c_d1 | d = c_d2)).
(all g all u -isa_rbo_static_designation(g, u)).
(all g all u -isa_rbo_dynamic_designation(g, u)).
rbo_in_force(c_ct, c_t). rbo_in_force(c_cr, c_t).
"""
# po-7b: Tom asks to approve the order in a Figure 6 instance, in no task instance; approval is task-bound there
TBR_UNBOUND = """
rbo_requires_task_binding(c_h, c_o). rbo_applies_within(c_h, c_plan).
rbo_requests_operation(c_q, c_o). occurrent_part_of(c_q, c_po7b). cco_prescribed_by(c_po7b, c_plan).
(all k all u -(occurrent_part_of(c_q, k) & isa_rbo_task_instance(k, u))).
occupies_temporal_region(c_q, c_uq). has_first_instant(c_uq, c_t0). rbo_in_force(c_h, c_t0).
"""
# po-7: Harry asks to approve the order inside his task instance, whose specification requires approval
TBR_BOUND = """
rbo_requires_task_binding(c_h, c_o). (all o (rbo_requires_task_binding(c_h, o) -> o = c_o)).
rbo_requests_operation(c_q, c_o). occurrent_part_of(c_q, c_k). isa_rbo_task_instance(c_k, c_u).
cco_prescribed_by(c_k, c_s). rbo_requires_operation(c_s, c_o).
occupies_temporal_region(c_q, c_uq). has_first_instant(c_uq, c_t0). rbo_in_force(c_h, c_t0).
"""
# near miss for the strong form: the request is inside a task instance, but its specification does not require
# the operation (Tom's order-stock task in po-1, which does not need approval)
TBR_WRONG_TASK = """
rbo_requires_task_binding(c_h, c_o). -(exists p rbo_applies_within(c_h, p)).
rbo_requests_operation(c_q, c_o). occurrent_part_of(c_q, c_k). isa_rbo_task_instance(c_k, c_u).
(all k all u (occurrent_part_of(c_q, k) & isa_rbo_task_instance(k, u) -> k = c_k)).
cco_prescribed_by(c_k, c_s). (all s (cco_prescribed_by(c_k, s) -> s = c_s)). -rbo_requires_operation(c_s, c_o).
occupies_temporal_region(c_q, c_uq). has_first_instant(c_uq, c_t0). rbo_in_force(c_h, c_t0).
"""
DENY = """
isa_rbo_access_permission(c_g, c_t). rbo_covers(c_g, c_q).
isa_rbo_access_prohibition(c_h, c_t). rbo_covers(c_h, c_q).
"""
# probe-1: Tom was granted create requisition, then asks to approve the order as Approver. The Approver
# permission covering the request is not a member of the permission set, but has the content of APM's, which is
PDSD_SAME_CONTENT = """
isa_rbo_dsd_constraint(c_pd, c_u). rbo_has_cardinality(c_pd, 2). -(exists p rbo_applies_within(c_pd, p)).
rbo_constrains_permission(c_pd, c_preq). rbo_constrains_permission(c_pd, c_papm).
rbo_has_operation(c_preq, c_create). -rbo_has_operation(c_papm, c_create).
(all o (rbo_has_operation(c_papm, o) <-> o = c_approve)). (all o (rbo_has_operation(c_pappr, o) <-> o = c_approve)).
(all b -rbo_has_access_object(c_papm, b)). (all b -rbo_has_access_object(c_pappr, b)).
(all e -rbo_has_object_description(c_papm, e)). (all e -rbo_has_object_description(c_pappr, e)).
isa_rbo_business_process(c_po, c_u).
occurrent_part_of(c_q1, c_po). cco_has_agent(c_q1, c_tom). -(exists y rbo_on_behalf_of(c_q1, y)).
rbo_decides_on(c_d1, c_q1). isa_rbo_access_grant(c_d1, c_t1). rbo_cites(c_d1, c_preq). rbo_decided_before(c_q1, c_q2).
rbo_has_requester(c_q2, c_tom). -(exists y rbo_on_behalf_of(c_q2, y)). occurrent_part_of(c_q2, c_po).
occupies_temporal_region(c_q2, c_uq). has_first_instant(c_uq, c_t2). rbo_requests_operation(c_q2, c_approve).
(all b -rbo_requests_access_to(c_q2, b)).
(all k all u -(occurrent_part_of(c_q2, k) & isa_rbo_task_instance(k, u))). rbo_in_force(c_pd, c_t2).
isa_rbo_access_permission(c_pappr, c_t2). rbo_in_force(c_pappr, c_t2). rbo_assigned_to(c_pappr, c_dappr).
isa_rbo_role_definition(c_dappr, c_t2). rbo_in_force(c_dappr, c_t2).
isa_rbo_active_role(c_a, c_t2). inheres_in(c_a, c_tom). rbo_activated_in(c_a, c_po). concretizes(c_a, c_dappr, c_t2).
"""
# probe-2: the set has three members, two of them APM's and Approver's approve-order permissions, of one content.
# A request for that operation, the first decided in its instance, hits both and counts them once
PDSD_ONCE = """
isa_rbo_dsd_constraint(c_pd, c_u). rbo_has_cardinality(c_pd, 2). -(exists p rbo_applies_within(c_pd, p)).
rbo_constrains_permission(c_pd, c_papm). rbo_constrains_permission(c_pd, c_pappr). rbo_constrains_permission(c_pd, c_preq).
(all p (rbo_constrains_permission(c_pd, p) -> p = c_papm | p = c_pappr | p = c_preq)).
(all o (rbo_has_operation(c_papm, o) <-> o = c_approve)). (all o (rbo_has_operation(c_pappr, o) <-> o = c_approve)).
(all o (rbo_has_operation(c_preq, o) <-> o = c_create)). c_create != c_approve.
(all b -rbo_has_access_object(c_papm, b)). (all b -rbo_has_access_object(c_pappr, b)).
(all e -rbo_has_object_description(c_papm, e)). (all e -rbo_has_object_description(c_pappr, e)).
rbo_has_requester(c_q, c_tom). (all o (rbo_requests_operation(c_q, o) <-> o = c_approve)).
(all q -rbo_decided_before(q, c_q)).
"""
# probe-3: Tom, with APM active, asks to approve the order and to create a requisition at one instant. The
# approve-order request sorts first by IRI, so it is decided first and granted
PDSD_SAME_INSTANT = """
isa_rbo_dsd_constraint(c_pd, c_u). rbo_has_cardinality(c_pd, 2). -(exists p rbo_applies_within(c_pd, p)).
rbo_constrains_permission(c_pd, c_preq). rbo_constrains_permission(c_pd, c_papm).
(all p (rbo_constrains_permission(c_pd, p) -> p = c_preq | p = c_papm)).
(all o (rbo_has_operation(c_preq, o) <-> o = c_create)). rbo_has_operation(c_papm, c_approve). c_create != c_approve.
-(exists b rbo_has_access_object(c_preq, b)). -(exists e rbo_has_object_description(c_preq, e)).
isa_rbo_business_process(c_po, c_u). rbo_in_force(c_pd, c_t).
isa_rbo_role_definition(c_dsc, c_t). isa_rbo_role_definition(c_dbuy, c_t). isa_rbo_role_definition(c_dapm, c_t).
rbo_in_force(c_s1, c_t). rbo_has_senior(c_s1, c_dapm). rbo_has_junior(c_s1, c_dbuy).
rbo_in_force(c_s2, c_t). rbo_has_senior(c_s2, c_dbuy). rbo_has_junior(c_s2, c_dsc).
rbo_in_force(c_dsc, c_t). rbo_in_force(c_dbuy, c_t). rbo_in_force(c_dapm, c_t).
isa_rbo_active_role(c_a, c_t). inheres_in(c_a, c_tom). rbo_activated_in(c_a, c_po). concretizes(c_a, c_dapm, c_t).
rbo_has_requester(c_q1, c_tom). -(exists y rbo_on_behalf_of(c_q1, y)). occurrent_part_of(c_q1, c_po).
occupies_temporal_region(c_q1, c_uq1). has_first_instant(c_uq1, c_t). (all o (rbo_requests_operation(c_q1, o) <-> o = c_approve)).
rbo_decides_on(c_d1, c_q1). isa_rbo_access_grant(c_d1, c_t). rbo_cites(c_d1, c_papm).
rbo_has_requester(c_q2, c_tom). -(exists y rbo_on_behalf_of(c_q2, y)). occurrent_part_of(c_q2, c_po).
occupies_temporal_region(c_q2, c_uq2). has_first_instant(c_uq2, c_t). rbo_requests_operation(c_q2, c_create).
-(exists b rbo_requests_access_to(c_q2, b)).
(all k all u -(occurrent_part_of(c_q2, k) & isa_rbo_task_instance(k, u))).
isa_rbo_access_permission(c_preq, c_t). rbo_in_force(c_preq, c_t). rbo_assigned_to(c_preq, c_dsc).
rbo_decided_before(c_q1, c_q2). (all q -rbo_decided_before(q, c_q1)).
"""


def run(tool, name, assumptions, goals=None, opts=""):
    path = os.path.join(W, name + ".in")
    body = opts + "".join(lst("assumptions", a) for a in assumptions)
    if goals:
        body += lst("goals", goals)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    t0 = time.time()
    with open(path, encoding="utf-8") as fin, open(os.path.join(W, name + ".out"), "w", encoding="utf-8") as fout:
        p = subprocess.run([os.path.join(BIN, tool + ".exe")], stdin=fin, stdout=fout, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    out = open(os.path.join(W, name + ".out"), encoding="utf-8", errors="replace").read()
    m = re.search(r"Exiting with (\d+) (proof|model)s?", out)
    ex = re.findall(r"process \d+ exit \(([a-z_]+)\)", out, re.I) or re.findall(r"Exiting with (failure)", out)
    verdict = f"{m.group(1)} {m.group(2)}" if m else (ex[-1] if ex else "no result")
    if not m and tool == "mace4":
        sizes = re.findall(r"DOMAIN SIZE (\d+)", out)
        verdict += f" (reached size {sizes[-1]})" if sizes else ""
    used = sorted(set(re.findall(r"# label\(([a-z0-9_]+)\)", out.split("PROOF")[1]))) if "PROOF" in out else []
    size = re.search(r"interpretation\( (\d+),", out)
    n = sum(len(a) for a in assumptions)
    return {"name": name, "tool": tool, "verdict": verdict, "seconds": round(dt, 1), "axioms": n,
            "used": [u for u in used if not u.startswith("fact")], "size": size.group(1) if size else ""}


FULL = "--full" in sys.argv
M_SECS = 600 if FULL else 300
M_OPTS = f"assign(max_seconds, {M_SECS}).\nassign(max_megs, 6000).\nassign(start_size, 2).\nassign(end_size, 24).\n"
P_OPTS = "assign(max_seconds, 300).\n"
results = []
SCEN = {"cr42-whole": (CR42 + WHOLE, None),
        "vote": (VOTE + "isa_temporal_instant(c_t, c_t).", None),
        "cr42-same-time-not-violated": (CR42 + SAME + CLOSE, "rbo_violates_dsd(c_dana, c_dsd, c_cr42)"),
        "visa-gap-not-violated": (VISA, "(exists i rbo_violates_dsd(c_bob, c_dsd, i))")}
# Mace4, tier 1 (RBO, bridge, scenario) and tier 2 (adding BFO-SIG); with --full, also the whole BFO set.
# Without a goal a model shows the set consistent; with one, a model is a counterexample to the goal.
# Tier 1 keeps only the distinctness each scenario asserts. A full unique-name assumption was tried: it pushes
# the search to 10-12 elements, where Mace4 runs out of memory grounding RBO's six-variable definitions. A model
# of the stated premises is a model whatever else it merges, so a countermodel found here still refutes the goal.
tiers = [("t1", [rbo, bridge])] + ([("t2", [rbo, bridge, bfo_sig]), ("full", [rbo, bridge, bfo])] if FULL else [])
for tier, theory in tiers:
    for key, (text, goal) in SCEN.items():
        results.append(run("mace4", f"m-{tier}-{key}", theory + [facts(text)],
                           [("goal", goal)] if goal else None, M_OPTS))
# entailments. From p2 on, Prover9 gets the access-control axioms: RBO without [rbo-s6], which p1 derives, and
# without the RT axioms, whose completion schema [rbo-t5] shares rbo-in-force with the scenario facts. With them,
# p2 had produced over 70,000 factors of input clauses, and no search, when it was stopped on 2026-10-31.
# Leaving premises out cannot make a proof unsound; Mace4 still gets every axiom.
s6 = [x for x in rbo if x[0] == "rbo-s6"]
RT = {"rbo-t1", "rbo-t2", "rbo-t3", "rbo-t4", "rbo-t5"}
access_axioms = [x for x in rbo if x[0] != "rbo-s6" and x[0] not in RT]
results.append(run("prover9", "p1-s6-from-s5", [[x for x in rbo if x[0] in ("rbo-s5", "rbo-u4")]], s6, P_OPTS))
results.append(run("prover9", "p2-cr42-whole-violates", [access_axioms, facts(CR42 + WHOLE)],
                   [("goal", "rbo_violates_dsd(c_dana, c_dsd, c_cr42)")], P_OPTS))
results.append(run("prover9", "p3-vote-granted", [access_axioms, facts(VOTE)],
                   [("goal", "rbo_warrants_grant(c_q)")], P_OPTS))
results.append(run("prover9", "p4-deny-overrides", [access_axioms, facts(DENY)],
                   [("goal", "-rbo_warrants_grant(c_q)")], P_OPTS))

results.append(run("prover9", "p5-bypass-active-for-sc", [access_axioms, facts(BYPASS)],
                   [("goal", "rbo_active_for(c_tom, c_dsc, c_po2, c_t)")], P_OPTS))
results.append(run("mace4", "m-t1-bypass-dsd-silent", [rbo, bridge, facts(BYPASS)],
                   [("goal", "rbo_violates_dsd(c_tom, c_dsd, c_po2)")], M_OPTS))
results.append(run("prover9", "p6-permission-dsd-violated", [access_axioms, facts(PERM_DSD)],
                   [("goal", "rbo_violates_permission_dsd(c_tom, c_pd, c_po3)")], P_OPTS))
results.append(run("prover9", "p7-task-dsd-designation", [access_axioms, facts(TASK_DSD)],
                   [("goal", "rbo_violates_task_dsd(c_dick, c_td, c_po10)")], P_OPTS))
results.append(run("prover9", "p8-human-requirement", [access_axioms, facts(HUMAN)],
                   [("goal", "rbo_violates_human_requirement(c_h, c_k)")], P_OPTS))
# the lemma needs only the two violation schemas, task authorization, one subject and the exactly-one role;
# as a single biconditional over every RBO axiom Prover9 ran out of time, so each direction is a goal of its own
lemma = [x for x in rbo if x[0] in ("rbo-s1", "rbo-s11", "rbo-s12", "rbo-u1", "rbo-u3", "rbo-k1")]
results.append(run("prover9", "p9a-task-ssd-implies-role-ssd", [lemma, facts(TASK_SSD)],
                   [("goal", "(all x (rbo_violates_task_ssd(x, c_ct, c_t) -> rbo_violates_ssd(x, c_cr, c_t)))")], P_OPTS))
results.append(run("prover9", "p9b-role-ssd-implies-task-ssd", [lemma, facts(TASK_SSD)],
                   [("goal", "(all x (rbo_violates_ssd(x, c_cr, c_t) -> rbo_violates_task_ssd(x, c_ct, c_t)))")], P_OPTS))
results.append(run("prover9", "p10a-task-binding-unbound", [access_axioms, facts(TBR_UNBOUND)],
                   [("goal", "rbo_violates_task_binding(c_h, c_q)")], P_OPTS))
results.append(run("prover9", "p10b-task-binding-bound", [access_axioms, facts(TBR_BOUND)],
                   [("goal", "-rbo_violates_task_binding(c_h, c_q)")], P_OPTS))
results.append(run("prover9", "p10c-task-binding-wrong-task", [access_axioms, facts(TBR_WRONG_TASK)],
                   [("goal", "rbo_violates_task_binding(c_h, c_q)")], P_OPTS))
results.append(run("prover9", "p10d-task-binding-denies", [access_axioms, facts(TBR_UNBOUND)],
                   [("goal", "-rbo_warrants_grant(c_q)")], P_OPTS))
# refusal at access time ([rbo-s15]): members compared by content, requests at one instant in decision order.
# The two negative goals rest on closures, so each scenario's premises are shown consistent: by Mace4 for
# pdsd-once, and for the other two, where it finds no model in 300 s, by the hand-specified models in docs/fol/
# (tools/check_hand_model.py)
for key, text in (("pdsd-same-content", PDSD_SAME_CONTENT), ("pdsd-once", PDSD_ONCE),
                  ("pdsd-same-instant", PDSD_SAME_INSTANT)):
    results.append(run("mace4", f"m-t1-{key}", [rbo, bridge, facts(text)], None, M_OPTS))
results.append(run("prover9", "p11a-refused-through-same-content", [access_axioms, facts(PDSD_SAME_CONTENT)],
                   [("goal", "rbo_refuses_permission_dsd(c_pd, c_q2)")], P_OPTS))
results.append(run("prover9", "p11b-one-content-counts-once", [access_axioms, facts(PDSD_ONCE)],
                   [("goal", "-rbo_refuses_permission_dsd(c_pd, c_q)")], P_OPTS))
results.append(run("prover9", "p11c-second-decided-refused", [access_axioms, facts(PDSD_SAME_INSTANT)],
                   [("goal", "rbo_refuses_permission_dsd(c_pd, c_q2)")], P_OPTS))
results.append(run("prover9", "p11d-first-decided-not-refused", [access_axioms, facts(PDSD_SAME_INSTANT)],
                   [("goal", "-rbo_refuses_permission_dsd(c_pd, c_q1)")], P_OPTS))

lines = ["# First-order results (tools/run_fol.py)", "",
         f"Prover9 and Mace4, LADR 2009-11A, built from github.com/ai4reason/Prover9 (master, commit cdca95a5). Run {time.strftime('%Y-%m-%d')}.", "",
         f"RBO: {len(rbo)} axioms. BRIDGE: {len(bridge)} axioms from the classified OWL. BFO: {len(bfo)} axioms from "
         f"{len(MODULES)} modules ({', '.join(MODULES)}), universals expanded over {len(in_play)} in play: {', '.join(sorted(in_play))}.", "",
         f"BFO axioms left out: {len(skipped)}. "
         + "; ".join(f"{a} ({m}): {why}" for m, a, why in skipped if why != "names a universal not in play")
         + f"; and {sum(1 for s in skipped if s[2] == 'names a universal not in play')} universal-declaration axioms naming a universal not in play.", "",
         f"BFO-SIG, the {len(bfo_sig)} BFO axioms using no relation outside RBO's BFO vocabulary: {', '.join(a for a, _ in bfo_sig)}.", "",
         "| Run | Tool | Axioms | Result | Model size | Seconds | Non-fact axioms the proof uses |", "|---|---|---:|---|---:|---:|---|"]
for r in results:
    lines.append(f"| {r['name']} | {r['tool']} | {r['axioms']} | {r['verdict']} | {r['size']} | {r['seconds']} | {', '.join(r['used'])} |")
print("\n".join(lines))
with open(os.path.join(R, "docs", "fol-results.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
