# Hand-specified model of the probe-3 scenario of design-record D15 (run_fol.py, PDSD_SAME_INSTANT) for
# m-t1-pdsd-same-instant.in, where Mace4 finds no model in 300 s. As for probe 1: create, the requisition
# permission and the second request on 1; the constraint on the numeral 2; approve, APM's permission, the first
# request, the instant and APM's definition on 0. [rbo-h4] makes seniority acyclic, so Buyer's and Stock
# Controller's definitions take 3 and 4, and the two hierarchy statements differ (s1 on 0, s2 on 3). Tom's
# assigned role, the witness [rbo-r2] and the OWL dependence axiom need for his active APM role, on 1.
N = 5
CONST = {c: 0 for c in ("c_approve", "c_papm", "c_q1", "c_d1", "c_uq1", "c_uq2", "c_t", "c_tom", "c_po", "c_u",
                        "c_a", "c_dapm", "c_s1", "c_rt_role")}
CONST.update({"c_create": 1, "c_preq": 1, "c_q2": 1, "c_pd": 2, "c_dbuy": 3, "c_s2": 3, "c_dsc": 4})
R_ = 1  # Tom's assigned role
# the requisition permission's operations and the first request's are stated as closures, which are not read for
# atoms; the assigned role's BFO ancestors follow from a defined predicate, whose consequences are not chained
EXTRA = [("rbo_has_operation", (1, 1)), ("rbo_requests_operation", (0, 0)),
         ("isa_role", (R_, 0)), ("concretizes", (R_, 0, 0)), ("inheres_in", (R_, 0)),
         ("specifically_depends_on", (0, R_))]
EXTRA += [(u, (R_, 0)) for u in ("isa_entity", "isa_continuant", "isa_realizable_entity",
                                  "isa_specifically_dependent_continuant")]
# the goals of p11c-second-decided-refused and p11d-first-decided-not-refused
GOALS = ["rbo_refuses_permission_dsd(c_pd, c_q2)", "-rbo_refuses_permission_dsd(c_pd, c_q1)"]
