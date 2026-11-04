# Critique of ROWLBAC

This critique covers ROWLBAC (T. Finin, A. Joshi, L. Kagal, J. Niu, R. Sandhu, W. Winsborough, B. Thuraisingham, "ROWLBAC: Representing Role Based Access Control in OWL", SACMAT '08, Estes Park, Colorado, June 11–13, 2008, pp.73–82), read against the NIST standard (D. F. Ferraiolo, R. Sandhu, S. Gavrila, D. R. Kuhn, R. Chandramouli, "Proposed NIST Standard for Role-Based Access Control", ACM TISSEC 4(3), August 2001, pp.224–274). ROWLBAC is cited by section and NIST by printed page. Each finding says how it was checked. "Re-run" means the paper's own rule or axioms were executed as printed, by `tools/rowlbac_checks.py`. The output is in `docs/query-results.md`.

Findings 1 to 8 are errors in ROWLBAC's encodings or claims. Findings 9 to 13 are places where it departs from NIST. Findings 14 to 17 concern the text and the scenario.

## Errors in the encodings

**1. The DSoD rule tests assigned roles, not active ones (§3.3.5).** The rule's body has `?S a ?RCURRENT`, which every role the subject is assigned satisfies. Bob is assigned Visitor and Temporary Resident, and `ActiveVisitor owl:disjointWith ActiveTemporaryResident` is asserted. Re-run on §3.3's assertions, the rule classifies Bob's first activation (Visitor) as a ProhibitedRoleActivation even though no role is active yet. In effect it enforces SSD. NIST's DSD check for `AddActiveRole` (p.270) counts the session's active roles plus the new one. *Checked: re-run, check 1.*

**2. Run on the triples as printed, the same rule never fires for the activation that is the actual violation.** The rule matches `?ARNEW owl:disjointWith ?ARCURRENT` as a triple, and the paper asserts only one direction. When Bob activates Temporary Resident second, the needed triple, `ActiveTemporaryResident owl:disjointWith ActiveVisitor`, is absent. The rule fires for it only if the engine first adds the symmetric triple. Whether cwm or the authors' engine did that is not stated. *Checked: re-run in both forms, check 1.*

**3. The same activation is both permitted and prohibited (§3.3.5).** The activation rule's body does not test for a DSD conflict, so `act1` is classified PermittedRoleActivation as well, and Bob gets ActiveVisitor. §3.2.1 declares PermittedAction and ProhibitedAction disjoint. The paper never says whether ActivateRole falls under Action, so whether this makes the knowledge base inconsistent cannot be decided from the text. *Checked: re-run, check 1.*

**4. Declaring `ssod` and `dsod` symmetric and transitive makes every constrained role conflict with itself (§3.4.2).** From `Resident ssod Citizen`, symmetry gives `Citizen ssod Resident`, and transitivity then gives `Citizen ssod Citizen` and `Resident ssod Resident`. The §3.4.4 SSODConflict rule binds `?ROLE1` and `?ROLE2` independently, so it fires for Alice when she holds Citizen alone. Transitivity is also wrong for sets: {A, B} and {B, C} as separate pairs would yield A ssod C. NIST's (role set, n) form (Defs. 3a–4, pp.240–241) has neither problem. *Checked: SPARQL path `(ssod|^ssod)+` and the rule re-run, check 2.*

**5. The covering axiom turns "not granted" into "forbidden" (§3.2.1).** `Action ≡ PermittedAction ⊔ ProhibitedAction` means every action is one or the other. NIST leaves negative permissions out (p.233, fn. 2): `CheckAccess` returns false and nothing more. RBO keeps prohibitions, as agreed, and puts the covering on access decisions (grant ⊔ denial) instead of acts. A denial then records that no permission applied, and does not state that the act was forbidden.

**6. Figure 4 states `HR.manager←Alice`.** Every other statement in Figures 4 and 5 uses `HR.managers`, and Figure 5 asserts `Alice a HR-managers`. Read literally, Figure 4 defines a role nothing else uses, and Alice is in no role. RBO's dataset uses `HR.managers` (`rt-stmt-14`).

**7. Figure 5 renames the delegated role.** Figure 4's `HQ.marketingDelg ← HR.managers.access` becomes `HQ-marketingDelg owl:equivalentClass HR-manufacturers-access` in Figure 5, so the OWL ties marketingDelg to a manufacturers role while the RT statement names managers. With Figure 5's encoding, a type 3 statement reduces to equivalence with a fresh named class. Nothing in Figure 5 defines `HR-manufacturers-access` beyond that equivalence, so the delegation's content is lost either way.

**8. The Access property is false, not true (§4.2).** The paper marks "HQ.marketing ⊇ HQ.ops" TRUE and says Pellet proves it. It does not follow, from the RT policy or from Figure 5's OWL.
- *RT policy.* HR.manufacturing is neither growth- nor shrink-restricted, so HR may add `HR.manufacturing ← Carol`. Then Carol is in HQ.ops (through `HQ.ops ← HR.manufacturing`) and not in HQ.marketing, because none of marketing's four defining statements reaches HR.manufacturing alone. In the current state the property does hold (only Alice is in either role), so the paper may be reporting the current state, but the property is posed over reachable states.
- *Figure 5.* All twelve class axioms are Boolean combinations of class names, so an inclusion holds exactly when no truth assignment satisfying the axioms makes the left side true and the right side false. Of 2,048 assignments, 64 satisfy the axioms, and 3 of those have ops true and marketing false, e.g. {employee, manufacturing, ops}. So `HQ-ops ⊑ HQ-marketing` is not entailed, and no sound reasoner proves it. Restriction (marketing ⊑ employee, ops ⊑ employee) is entailed, as the paper says.
*Checked: RBO's bound derivation leaves access "not proven" and the counter-state shows Carol in ops and not marketing; brute force, check 3.*

Availability and Safety come out FALSE, as the paper says. Counter-states: HR retracts `HR.managers ← Alice` (Alice leaves HQ.marketing); HR adds `HR.sales ← Carol` (Carol joins HQ.marketing). Both respect the growth and shrink assumptions.

## Departures from NIST

**9. No sessions.** "Active" belongs to the person, not to a session, so a user with two sessions cannot be represented (§3.3, §3.4). Def. 4 (p.241) quantifies over sessions; its prose (pp.231, 240, "within or across a user's sessions") allows a wider reading. RBO replaces sessions with business process instances, as agreed.

**10. No operations or objects in the main scenario.** Voting, working and jury duty are real-world acts. NIST's operations are "an executable image of a program" acting on objects (p.233). Only the §4.1 devices are NIST objects. RBO models operations as IAO plan specifications and leaves the scenario's object slot empty.

**11. Approaches 1 and 2 implement different NIST options, and Table 1 presents them as interchangeable.** NIST leaves open whether activating a role activates its juniors (p.244; p.257: juniors "are not necessarily active"). Approach 1 never subclasses ActiveCitizen under ActiveUSPerson, so juniors must be activated separately. Approach 2's `activeRole` inheritance rule (§3.4.4) activates them automatically. RBO applies juniors' regulations without activating them.

**12. SSD and DSD only for pairs.** NIST allows any role set with n ≥ 2 ("no one user may be assigned to three of the four roles that represent the purchasing function", p.239). RBO uses a set and a cardinality.

**13. ROWLBAC's subjects are not NIST's users.** NIST users are human beings (p.233), and ROWLBAC's Subject is open (§3.2.2). RBO follows ROWLBAC, with CCO Agent as the range.

## Text and scenario

**14. §3.1 names two SSD constraints, and the encodings carry one.** §3.1 says SSD "exists between Resident and Citizen, and Permanent Resident and Temporary Resident". §3.3.2 and §3.4.2 encode only the first. RBO's dataset has both (`ssd-resident-citizen`, `ssd-pr-tr`).

**15. §3.1 and the encodings name different DSD pairs.** §3.1 puts DSD "between Visitor and Resident". §3.3.3 and §3.4.2 encode Visitor and Temporary Resident. Under Approach 1 activating Temporary Resident does not activate Resident, so the two are different constraints. Under Approach 2 the `activeRole` inheritance rule does activate Resident, and §3.1's pair would then also block Visitor with Permanent Resident or Permanent Residency Applicant, which the encoded pair allows. RBO uses {Visitor, Temporary Resident}, as agreed.

**16. The visa-holder roles sit outside the DSD set.** In Figure 1, Work, Business and Student Visa Holder are below Temporary Resident. Neither encoding includes them, so Bob could activate Visitor together with Work Visa Holder. RBO has the same gap: following NIST p.257, its DSD counts only roles activated explicitly (CLIF [rbo-s3], derive-dsd-conflicts.rq), so a Work Visa Holder role does not count as Temporary Resident. Mace4 finds a model of RBO's axioms in which Bob has Visitor and Work Visa Holder active and violates nothing (verification report, section 7). Closing it means adding the visa roles to the set, which neither paper does.

**17. Citations.** The four levels in §3 (flat, hierarchical, constrained, symmetric) are attributed to reference [10]. That article has no "flat" (zero occurrences) and "symmetric" occurs only inside "antisymmetric" (p.229). Its components are Core, Hierarchical, Static and Dynamic Separation of Duty. References [9] and [10] are the same article (TISSEC 4(3):224–274, 2001), listed twice with different author initials.

## What ROWLBAC gets right, checked

- Subclassing runs in NIST's direction: A ⊑ B exactly when A's members are B's members, matching Def. 2a's senior-to-junior inheritance (p.235). RBO's drift check finds no disagreement between the two hierarchies (check-hierarchy-drift.rq, no rows).
- Disjointness over role classes counts inherited roles, which Def. 3b requires (p.240). RBO's SSD query reproduces it: Alice's Permanent Resident assignment conflicts with Citizen because Permanent Resident is senior to Resident.
- Figure 1 is a limited hierarchy (Def. 2b, p.237): no role has two immediate juniors (check-limited-hierarchy.rq, no rows).
- The scenario's access answers follow from Figure 1 under NIST semantics, and RBO's queries reproduce every one (verification report, section 3).
