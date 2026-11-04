# Hand-specified model of the probe-1 scenario of design-record D15 (run_fol.py, PDSD_SAME_CONTENT) for
# m-t1-pdsd-same-content.in, where Mace4 finds no model in 300 s. Create and the requisition permission on 1; the
# permission DSD constraint on the numeral 2, its cardinality; everything else on 0. Tom's assigned role, the
# witness [rbaco-r2] and the OWL dependence axiom need for his active Approver role, also on 1.
N = 3
CONST = {"c_approve": 0, "c_papm": 0, "c_pappr": 0, "c_create": 1, "c_preq": 1, "c_pd": 2,
         "c_tom": 0, "c_q1": 0, "c_q2": 0, "c_d1": 0, "c_po": 0, "c_t1": 0, "c_u": 0, "c_rt_role": 0,
         "c_t2": 0, "c_uq": 0, "c_dappr": 0, "c_a": 0}
R_ = 1  # Tom's assigned role
# the approve-order permissions' operations are stated as closures, which are not read for atoms; the assigned
# role's BFO ancestors follow from a defined predicate, whose consequences are not chained
EXTRA = [("rbaco_has_operation", (0, 0)),
         ("isa_role", (R_, 0)), ("concretizes", (R_, 0, 0)), ("inheres_in", (R_, 0)),
         ("specifically_depends_on", (0, R_))]
EXTRA += [(u, (R_, 0)) for u in ("isa_entity", "isa_continuant", "isa_realizable_entity",
                                  "isa_specifically_dependent_continuant")]
# the goal of p11a-refused-through-same-content
GOALS = ["rbaco_refuses_permission_dsd(c_pd, c_q2)"]
