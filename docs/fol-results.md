# First-order results (tools/run_fol.py)

Prover9 and Mace4, LADR 2009-11A, built from github.com/ai4reason/Prover9 (master, commit cdca95a5). Run 2026-11-03.

RBACO: 48 axioms. BRIDGE: 50 axioms from the classified OWL. BFO: 207 axioms from 9 modules (existence-instantiation, specific-dependency, generic-dependence, participation, occurrent-mereology, temporal-region, order, continuant-mereology, universal-declaration), universals expanded over 31 in play: cco-person, continuant, entity, generically-dependent-continuant, independent-continuant, material-entity, occurrent, one-dimensional-temporal-region, process, rbaco-access-grant, rbaco-access-permission, rbaco-access-prohibition, rbaco-active-role, rbaco-assigned-role, rbaco-business-process, rbaco-dsd-constraint, rbaco-dynamic-designation, rbaco-role-definition, rbaco-same-time-dsd, rbaco-ssd-constraint, rbaco-static-designation, rbaco-task-instance, rbaco-task-specification, rbaco-whole-instance-dsd, realizable-entity, role, specifically-dependent-continuant, temporal-instant, temporal-interval, temporal-region, zero-dimensional-temporal-region.

BFO axioms left out: 66. qkp-1 (universal-declaration): universals are not particulars: they are not domain elements at all; xtf-1 (universal-declaration): universals are pairwise distinct: they are predicate names, not domain elements; and 64 universal-declaration axioms naming a universal not in play.

BFO-SIG, the 118 BFO axioms using no relation outside RBACO's BFO vocabulary: nmq-1, mbf-1, qaf-1, oap-1, lqn-1, nis-1, zuw-1, bee-1, dzz-1, yct-1, bks-2, myu-1, iyu-1, dbp-1, tht-1, akq-1, kkl-1, cgn-1, zba-1, nyz-1, ibk-1, rog-1, fmm-1, xjr-1, trl-1, yjm-1, kxe-1, ild-2, cgn-1, fmm-1, yvi-1, hbj-1, xlu-1, kad-1, ybr-1, gjl-2, zmr-1, csk-1, aff-1, cmy-2, hdk-1, myl-1, ccz-1, ptm-1, esh-2, hpc-1, boo-1, bal-1, dbj-2, njq-1, bvr-1, zdq-1, fwf-1, pir-2, qaf-1, bfq-1, mjn-2, fwk-2, mvd-1, ruj-1, jhe-2, mei-2, bnt-2, qnf-1, hgs-1, tvx-3, eeg-2, qga-1, owb-1, ixz-1, wsg-2, hew-1, ctz-1, sen-1, wix-1, aou-1, qnf-1, qga-1, owb-1, duz-1, ewm-1, bsm-1, lkt-1, axs-1, hru-1, toj-1, bjs-1, gpp-1, kuz-1, ufw-1, qar-1, qiz-1, bau-1, wda-1, lso-1, tcp-1, njq-1, wrf-2, ejl-1, wyq-1, faf-1, zyw-1, dhv-1, fpd-1, pvu-1, bjp-1, fye-1, qix-1, hxo-1, zkj-2, ghs-1, opd-1, ayr-2, gsg-1, otk-1, iup-1, hke-1, cig-1.

| Run | Tool | Axioms | Result | Model size | Seconds | Non-fact axioms the proof uses |
|---|---|---:|---|---:|---:|---|
| m-t1-cr42-whole | mace4 | 112 | 1 model | 3 | 3.6 |  |
| m-t1-vote | mace4 | 111 | 1 model | 3 | 3.3 |  |
| m-t1-cr42-same-time-not-violated | mace4 | 116 | max_sec_no (reached size 3) |  | 300.2 |  |
| m-t1-visa-gap-not-violated | mace4 | 111 | 1 model | 3 | 29.6 |  |
| p1-s6-from-s5 | prover9 | 2 | 1 proof |  | 0.2 | goal, non_clause, rbaco_s5, rbaco_s6, rbaco_u4 |
| p2-cr42-whole-violates | prover9 | 56 | 1 proof |  | 2.5 | goal, non_clause, rbaco_s2, rbaco_s3, rbaco_s5, rbaco_u4 |
| p3-vote-granted | prover9 | 54 | 1 proof |  | 0.8 | goal, non_clause, rbaco_a1, rbaco_a2, rbaco_a3, rbaco_a4, rbaco_g3, rbaco_h1, rbaco_h2, rbaco_s15 |
| p4-deny-overrides | prover9 | 44 | 1 proof |  | 1.1 | goal, non_clause, rbaco_a3 |
| p5-bypass-active-for-sc | prover9 | 55 | 1 proof |  | 1.7 | goal, non_clause, rbaco_a0, rbaco_h1, rbaco_h2 |
| m-t1-bypass-dsd-silent | mace4 | 111 | 1 model | 3 | 3.5 |  |
| p6-permission-dsd-violated | prover9 | 50 | 1 proof |  | 1.6 | goal, non_clause, rbaco_p1, rbaco_s10, rbaco_s17, rbaco_s2, rbaco_s9, rbaco_u4 |
| p7-task-dsd-designation | prover9 | 49 | 1 proof |  | 1.5 | goal, non_clause, rbaco_p1, rbaco_s13, rbaco_s14, rbaco_s2, rbaco_u1, rbaco_u2, rbaco_u4 |
| p8-human-requirement | prover9 | 46 | 1 proof |  | 5.7 | goal, non_clause, rbaco_g1, rbaco_s2 |
| p9a-task-ssd-implies-role-ssd | prover9 | 15 | 1 proof |  | 0.1 | goal, non_clause, rbaco_k1, rbaco_s1, rbaco_s11, rbaco_s12, rbaco_u1, rbaco_u3 |
| p9b-role-ssd-implies-task-ssd | prover9 | 15 | 1 proof |  | 0.1 | goal, non_clause, rbaco_k1, rbaco_s1, rbaco_s11, rbaco_s12, rbaco_u1, rbaco_u3 |
| p10a-task-binding-unbound | prover9 | 46 | 1 proof |  | 1.7 | goal, non_clause, rbaco_a1, rbaco_g3, rbaco_s2 |
| p10b-task-binding-bound | prover9 | 46 | 1 proof |  | 1.6 | goal, non_clause, rbaco_g3 |
| p10c-task-binding-wrong-task | prover9 | 47 | 1 proof |  | 1.8 | goal, non_clause, rbaco_a1, rbaco_g3, rbaco_s2 |
| p10d-task-binding-denies | prover9 | 46 | 1 proof |  | 1.7 | goal, non_clause, rbaco_a1, rbaco_a3, rbaco_g3, rbaco_s2 |
| m-t1-pdsd-same-content | mace4 | 114 | max_sec_no (reached size 3) |  | 300.2 |  |
| m-t1-pdsd-once | mace4 | 107 | 1 model | 3 | 3.3 |  |
| m-t1-pdsd-same-instant | mace4 | 118 | max_sec_no (reached size 3) |  | 300.2 |  |
| p11a-refused-through-same-content | prover9 | 58 | 1 proof |  | 41.8 | goal, non_clause, rbaco_a1, rbaco_a2, rbaco_a4, rbaco_h2, rbaco_p1, rbaco_p2, rbaco_s15, rbaco_s16, rbaco_s17, rbaco_s18, rbaco_s2, rbaco_u4 |
| p11b-one-content-counts-once | prover9 | 51 | 1 proof |  | 1.6 | goal, non_clause, rbaco_a2, rbaco_s15, rbaco_s16, rbaco_s17, rbaco_s18 |
| p11c-second-decided-refused | prover9 | 62 | 1 proof |  | 42.8 | goal, non_clause, rbaco_a1, rbaco_a2, rbaco_a4, rbaco_h1, rbaco_h2, rbaco_p1, rbaco_p2, rbaco_s15, rbaco_s16, rbaco_s17, rbaco_s18, rbaco_s2, rbaco_u4 |
| p11d-first-decided-not-refused | prover9 | 62 | 1 proof |  | 2.1 | goal, non_clause, rbaco_a2, rbaco_s15, rbaco_s16, rbaco_s17, rbaco_s18 |
