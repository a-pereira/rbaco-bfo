# Design record

The decisions behind RBACO, each settled during clarification. For each one: the question, the options considered, what was chosen, and its consequences. A paragraph marked *Interpretation* is a modeling judgment of mine that no source states. Sources: ROWLBAC (Finin et al., SACMAT 2008), cited by section; the NIST standard (Ferraiolo et al., ACM TISSEC 4(3), 2001), cited by printed page; BFO 2020 (`bfo-core.ttl` and the CLIF modules at github.com/bfo-ontology/bfo-2020, generated 2025-12-05); BFO 2.0 *Specification and User's Guide* (B. Smith, corresponding author, 2015), cited by PDF page; CCO v2.2 (2026-08-13); IAO release 2026-03-30.

## D1. Semantics: NIST's, not ROWLBAC's as written

Options: reproduce ROWLBAC's encodings; or build each pattern to NIST's semantics and list ROWLBAC's departures in the critique. **Chosen: NIST's semantics**, adding only what a pattern cannot work without. Every departure is a finding in `critique.md`.

## D2. Sessions become business process instances

NIST gives each session one user (p.233). The user replaced sessions with business process instances: a hiring, an order, a code change. Options: the session is the whole instance, shared by all participants; or it is one participant's part of it. **Chosen: the whole instance.** An active role belongs to a person within one instance (`activated in`, RBACO_0000106, exactly one). DSD then reads "no one person activates n roles from the set within one instance", the form that serves NIST's purpose ("cannot occur without deliberate collusion", p.238).

CCO has no business-process class: an absence search for business, workflow, procedure, transaction and task matches no label among the terms of CCO v2.2 (12 modules, 1,572 declared terms), IAO (267 in its namespace) or the BFO 2020 OWL (76). So `business process` (RBACO_0000004) ⊑ CCO Planned Act, prescribed by a `business process plan` (RBACO_0000005) ⊑ CCO Plan.

## D3. DSD scope and counting

Scope options: always global, or scoped to a plan with global as the default. **Chosen: scoped, with global optional** (`applies within`, RBACO_0000115, at most one). NIST names each set for "the transaction or business process" it restricts (p.245), and DSD set creation has "identical" semantics (p.246), but Def. 4's formula ignores the name.

Counting options: same-time (two roles active together), whole-instance (two roles active at any times in one instance), or a choice per set. **Chosen: a choice per set**, same-time by default (RBACO_0000015, RBACO_0000016). Whole-instance is the classic separation of duty: CR-42 shows Dana refused the approver role after dropping submitter, and the same-time variant shows the same request allowed.

DSD counts only roles activated explicitly, since NIST says juniors "are not necessarily active" (p.257).

## D4. What an RBAC role is

Options: a BFO role (the person's organizational standing); an information entity in the access-control system (NIST: active roles "might actually be the groups", p.253); or both, linked. **Chosen: both.** A `role definition` (RBACO_0000001) is a CCO Prescriptive ICE; an `assigned role` (RBACO_0000002) is a BFO role that concretizes it.

*Interpretation.* BFO 2020 allows an SDC to concretize a GDC (`generic-dependence.cl` [rog-1]), and a role is an SDC. Saying that a person's assigned role concretizes a definition is my reading of how a prescription becomes a standing; no source applies concretization to roles this way.

*Interpretation.* The act that outputs an assigned role, a `role assignment` (RBACO_0000028), is typed both a CCO Gain of Role, in which the assignee becomes bearer of the role, and a `policy administration act` (RBACO_0000030), an Act of Declarative Communication realizing the officer's Authority Role. One process is thus both the officer's declaration and the assignee's gain. It also stretches CCO's Authority Role, which CCO defines as realized by processes that create, modify, transfer or eliminate Process Regulations or other Authority Roles (ont00000187); an assigned role is neither. No source settles either point. The alternative, kept open, is two processes: the declaration, and the gain it brings about.

## D5. Active roles are separate roles

Options: an active role as a state of the assigned role; or as a role of its own. **Chosen: its own role**, output by a `role activation` (RBACO_0000026) ⊑ CCO Gain of Role and input to a `role deactivation` (RBACO_0000027) ⊑ CCO Loss of Role. It specifically depends on the assigned role (BFO_0000195).

## D6. Operations

**Chosen: IAO plan specifications** (IAO_0000104). IAO files software under plan specification, and NIST's operation is "an executable image of a program" (p.233). The scenario's acts (vote, work, jury) get operation individuals of the same type.

The IAO extract keeps 5 terms. IAO's has-part axioms on plan specification use BFO_0000051, which BFO 2020 core does not declare, so `build_iao_extract.py` drops them and prints what it dropped.

## D7. Prohibitions and the covering axiom

Options: drop prohibitions (NIST, p.233 fn. 2); keep them with ROWLBAC's covering axiom; keep them without it. **Chosen: keep, no covering, deny-overrides.** `access prohibition` (RBACO_0000008) is disjoint from `access permission` (RBACO_0000007). A request with no covering permission is denied, and the denial cites nothing.

*Refinement made while drafting.* Regulations sit under CCO Process Regulation (ont00001324), not under CCO Action Permission or Process Prohibition. Those CCO classes are defined as permitting or prohibiting *some* process, so asserting them of a regulation would entail that a regulated process exists, which is false for a permission nobody has used. ROWLBAC's disjoint-and-covering pattern (P2) moves to decisions: `access decision` ⊑ `grant` ⊔ `denial`.

## D8. Hierarchy and inheritance

**Chosen: juniors' regulations apply without the juniors being activated.** That matches Approach 1's active-role semantics and leaves NIST's open question (p.244) answered one way, stated here.

The hierarchy is kept in two places, with a check between them. Role universals in `rbaco-bfo-domain.ttl` are ordered by `rdfs:subClassOf`, as ROWLBAC's Approach 1 does. Role definitions are ordered by dated `role inheritance statements` (RBACO_0000017), which `derive-hierarchy-snapshot.rq` turns into `is senior to` (RBACO_0000120) at a given time. `check-hierarchy-drift.rq` reports any disagreement. Annotation RBACO_0000301 links each universal to its definition.

## D9. SSD and DSD as sets with a cardinality, recorded rather than enforced

Options: pairs as OWL disjointness, so that a violation makes the ontology inconsistent; or sets with a cardinality, recorded as queryable regulations with conflict reports. **Chosen: sets with a cardinality, recorded.** A violation is a fact about an act. `derive-ssd-conflicts.rq` and `derive-dsd-conflicts.rq` write conflict reports (RBACO_0000019, RBACO_0000020) carrying the subject, the constraint, the act, the role definitions and a justification. CLIF axioms [rbaco-s1] to [rbaco-s5] define the violation predicates and deny nothing. D14 extends this to permission and task sets, whose reports name members with RBACO_0000146 and RBACO_0000147, and adds three refusals the queries make at the request: permission DSD at access, task DSD and strict least privilege at activation. D15 places the three member properties under RBACO_0000149 and reports static breaches at policy issuing acts as well.

## D10. Scenario details

- **DSD set: {Visitor, Temporary Resident}, global**, as §3.3.3 and §3.4.2 encode it; §3.1's {Visitor, Resident} is a critique finding.
- **Both SSD sets from §3.1**: {Resident, Citizen} and {Permanent Resident, Temporary Resident}.
- **One business process instance per narrative**: `alice-review`, `bob-review` (instances of `status eligibility review`, RBACO_0001016), `cr-42`, `marie-day`.

## D11. Attribute-based access and RT

- **ABAC (§4.1): conditional permissions.** A permission names an object description (RBACO_0000009) with criteria as annotation values (RBACO_0000302, RBACO_0000303 and RBACO_0000305) and, for the office rule, a `requester office condition` (RBACO_0000011). Classroom printer (RBACO_0001023) is also a defined class, so a DL reasoner can classify printers by location.
- **RT (§4.2): reified statements.** Each RT statement is an ICE with a head and a body (RBACO_0000034 to RBACO_0000038). Membership is derived to a fixpoint by `derive-rt-membership.rq`. Growth and shrink restrictions are recorded on a `security analysis specification` (RBACO_0000039), and `derive-rt-bounds.rq` derives sound bounds from them.

*Interpretation, not checked.* RT type 3 (`A.r ← B.r1.r2`) might be expressible in ALCI as `A-r ⊒ ∃r2⁻.B-r1` if RT role names are encoded as properties. ROWLBAC says type 3 needs a role chain. RBACO does not rely on this.

## D12. Time

**Chosen: event-bounded tenures.** An assigned role exists from the role assignment that outputs it to the Loss of Role that takes it as input. An active role ends then too, if not deactivated before (D15). Every act occupies a temporal interval whose first instant carries an `xsd:dateTime` timestamp (RBACO_0000205). Queries take an evaluation time, which the runner substitutes for `?evalTime`.

*Convention adopted from BFO 2.0, not from BFO 2020.* A reassignment creates a new role instance and does not reuse the old one. This follows BFO 2.0's statement that an s-dependent continuant "cannot migrate from one independent continuant bearer to another" (PDF p.29). The `role` and `inheres-in` terms used here are BFO 2020's.

## D13. Rules, imports and identifiers

- **Rules: SPARQL 1.1 only.** No SWRL or N3. The 30 query files (plus a shared prefix file) are derivations, checks and competency questions.
- **CCO and IAO are bridged through `is about`**: `cco:ont00001808 owl:equivalentProperty obo:IAO_0000136`. *Interpretation*: the two definitions read alike. With the bridge, an IAO ICE and a CCO ICE are mutually entailed under the two ontologies' axioms: a four-line hand proof in the verification report, which HermiT confirms by inferring the two classes equivalent. The bridge's only effect on the imported classes is to place CCO's ICE subclasses under IAO ICE and IAO's directive information entity under CCO ICE (verification report, section 6).
- **Mixed imports**: BFO 2020 core and five CCO modules by IRI (with their two further CCO dependencies resolved by the catalog), and IAO as a scripted extract.
- **Opaque identifiers** `RBACO_0000001` onward, under the base `https://w3id.org/rbaco/bfo/` (until D20, `RBO_0000001` onward under the placeholder base `https://example.org/rbac-bfo/`), labels in `rdfs:label`. RBACO_00001xx are object properties, 2xx data properties, 3xx annotation properties, and 1xxx domain terms.
- **License**: CC BY 4.0, a placeholder matching BFO 2020. CCO is BSD 3-Clause.

## D14. Tasks and conflicting entities (Botha and Eloff 2001)

Added 2026-10-30 after a review of R. A. Botha and J. H. P. Eloff, "Separation of duties for access control enforcement in workflow environments", *IBM Systems Journal* 40(3), 2001, pp.666–682. `docs/botha-review.md` has the review, the ten proposals and the record of how each was settled; this entry lists what was chosen.

- **Tasks.** A task specification (RBACO_0000040, a CCO Plan) is a continuant part of a business process plan and requires exactly one role definition (RBACO_0000132) and the operations it needs (RBACO_0000133, read by checks only). A task instance (RBACO_0000041, a CCO Planned Act) is an occurrent part of a business process, prescribed by its specification, with at most one agent. A work item (RBACO_0000048, a CCO Prescriptive ICE) is issued when a task is enabled and names its specification and process instance; the task instance, once begun, is prescribed by it too.
- **WSessions and strict least privilege.** An active role may be activated for one task instance (RBACO_0000136). A role activation request may name a work item (RBACO_0000137), and is then refused unless it asks for the task's required role definition itself ([rbaco-k3]). A request that is part of a task instance is covered only through a role activated for it ([rbaco-a4], which [rbaco-a2] now uses). The binding is optional, after Botha and Eloff p.671.
- **Three kinds of SoD set.** Role, permission and task SoD constraints (RBACO_0000042–044) are defined by two or more members of one kind and are pairwise disjoint. Same-time DSD is role-only. Dynamic permission SoD reads "exercised" as granted ([rbaco-s9]) and refuses the access request that would complete the set; dynamic task SoD refuses the task-bound activation ([rbaco-s14]).
- **Conflicting agents.** Static and dynamic designations (RBACO_0000046, 047) name agents, or a CCO Group of Agents whose member parts count, as one subject for SoD ([rbaco-u3], [rbaco-u4]). They do not chain; `check-designation-chains.rq` reports pairs that share an agent.
- **Automation and principals.** Workflow automation is a CCO Agent with assigned roles like anyone else. An act may be performed on behalf of an agent (RBACO_0000143), its principal ([rbaco-p1]), and SoD compares principals. A human performer requirement (RBACO_0000049) refuses a non-person agent for a task, whoever it acts for ([rbaco-g1]); requires prior (RBACO_0000144) refuses a task until a person has finished the prior one ([rbaco-g2]).
- *Interpretation.* Botha and Eloff remedy dynamically conflicting roles related by the hierarchy by re-engineering it (Figure 6, p.676). In RBACO the remedy holds only for task-bound activations: activated without a work item, APM still reaches both conflicting operations under the Figure 6 hierarchy (scenario po-7b). Permission or task SoD closes it, and so does the requirement below.
- **Task-bound operations.** Activation stays optional. Instead, a task-bound operation requirement (RBACO_0000050, a CCO Process Regulation, optionally scoped by applies within) names operations (RBACO_0000148) that may be requested only within a task instance whose specification requires them (RBACO_0000133) ([rbaco-g3]). `decide-access.rq` denies an unmet request after prohibitions and before permission SoD, citing the requirement. Being inside some task instance is not enough, so a task cannot carry an operation it does not need. Two alternatives were declined: requiring every activation in a plan with task specifications to name a work item, which breaks the datasets that have no workflow; and checking only that the request is inside a task instance, which lets a task whose role reaches the operation through the hierarchy carry it. `check-sod-hierarchy.rq` warns when a requirement names some of a dynamic set's operations but not all.

## D15. Corrections after the review of 2026-10-31

A review of the consult output on 2026-10-31 found three high and six medium defects, corrected the same day. Each behavior that changed has a regression probe in `data/probes.ttl`, which `run_queries.py` runs over the purchase data and checks against its expected result (the "Probe expectations" table in `docs/query-results.md`).

- **In force, defined once.** A prescriptive entity is in force at t when the issuing act (RBACO_0000031) that outputs it begins at or before t and no retiring act (RBACO_0000032) taking it as input does, as RBACO_0000032's scope note says. `derive-in-force.rq` writes this for each evaluation time, and every query that reads a constraint, designation, requirement, regulation, inheritance statement or role definition joins on it. Before, each query filtered in its own way or not at all, so a late designation could count in one query and not in another. The CLIF predicate `rbaco-in-force` replaces the one for inheritance statements, and the axioms test it wherever the queries do. A retired role definition authorizes no one ([rbaco-h3]).
- **Permissions compared by content.** NIST assigns one permission to many roles (Def. 1, p.234), while RBACO holds one regulation per role it is assigned to. Separation of duty therefore compares regulations by operation, named object and object description ([rbaco-s17]): a permission covering a request counts as a member of a set when it has that member's content, and members of one content count once. Before, a junior's permission for a constrained operation escaped the set, and listing both permissions counted one request twice. Comparing by overlapping object scope was declined, because an object description's criteria are annotation values that the queries cannot compare with a named object. `check-sod-hierarchy.rq` warns instead when a permission outside a set has a member's operation under another object scope.
- **Deassignment ends active roles.** An active role ends at its deactivation or at the Loss of Role of the assigned role it specifically depends on, whichever comes first. NIST leaves open sessions after DeassignUser to the implementation, which may wait for them to end, terminate them, or inactivate the role (p.252). RBACO inactivates the role, which [rbaco-r2] already implies. `check-active-roles.rq` reports an active role that outlives its assigned role.
- **Requests at one instant, in IRI order.** Requests with the same timestamp are decided one at a time, the smaller IRI first (`rbaco-decided-before`), and each decision is in the graph before the next request is counted. Before, two conflicting requests at one instant were both granted. For role DSD the change is from refusing both activations to allowing the first. Counting same-instant grants as exercised was declined: it refuses both requests, the legitimate one included.
- **Static SoD at policy changes.** NIST enforces static constraints during user assignment and while role hierarchies are created (p.246). Issuing an inheritance statement, a static constraint or a static designation is now checked as an assignment is, and a breach it completes is reported at the issuing act. As with assignments (D9), it is reported, not refused.
- **Decisions in the CLIF.** [rbaco-a3] now withholds a grant when the request violates a task-bound operation requirement ([rbaco-g3]) or a dynamic permission constraint refuses it ([rbaco-s15], with [rbaco-s16] and [rbaco-s18]), the two denial grounds `decide-access.rq` already applied.
- **Conflict reports over any member.** `describes conflicting member` (RBACO_0000149) is the parent of the role definition, permission and task specification member properties (RBACO_0000126, RBACO_0000146, RBACO_0000147) and carries a report's minimum of two members, which before was stated on the role property alone, so that a permission report entailed two unnamed role definitions.
- **The worklist counts as the decisions do.** `cq-worklist.rq` uses the in-force facts, the evaluation time, each constraint's n and permission contents.

## D16. Low-severity corrections after the same review

The review's fourteen low-severity findings were corrected after D15. Most were wording: citations, cross-references, the CLIF's name-mapping header, an absence claim without its search scope (D2), and a modeling choice now marked as an interpretation (D4). These change behavior or commitments:

- **Object scope in the competency questions.** `cq-class-level-permissions.rq` and `cq-usable-objects.rq` now match a prohibition to a permission's objects as `derive-regulation-coverage.rq` matches a regulation to a request: the same named object, an object description whose criteria hold, or neither, which covers only requests that name no object. Before, a prohibition on one object, or one with an object description, overrode a permission for every object. `cq-usable-objects.rq` also applies a prohibition through any of the person's active roles in the instance, and one that names no role definition but carries a subject description (a case D18 removed). No dataset has a prohibition these changes reach, so the published answers are unchanged; five planted cases were checked on a copy of the ABAC data, of which the old queries answered four wrongly.
- **Functional request properties.** `requests activation for` (RBACO_0000137) and `is fulfilled by` (RBACO_0000111) are functional: a request serves one work item and is fulfilled at most once.
- **requires prior** (RBACO_0000144) is a sub-property of CCO's is about, like the other relations between information entities. It stays on the task specification rather than on a plan, which its scope note now says.
- **Asserted closures are checked, not computed.** The queries read parthood, location and types as asserted. `check-asserted-closures.rq` reports a part of a task instance that is not asserted part of its business process instance, a task instance in no business process instance, and an entity located in something located elsewhere without the direct link. Materializing the closures was the other option; a check leaves the data as written and tells its author what is missing. A type that only a reasoner would infer stays invisible to the queries (README).
- **First-order limits stated, not repaired.** [rbaco-h1] fixes seniority exactly only in finite models, and [rbaco-s4] and [rbaco-s5] rely on the disjointness of the two DSD kinds that only `rbaco-bfo.owl` states. The CLIF header now says both. A rigidity axiom for the constraint kinds would change the theory every proof and model was checked against, while the queries, which compute closures, are unaffected.
- **Reproducible output.** `run_queries.py` sorts the terms inside a concatenated cell and the rows of a query without ORDER BY, and breaks ties within an ordered one, so a rerun on the same inputs writes the same tables. `tools/make_inferences.sh`, which `run_all.sh` runs, writes `docs/dl/inferences.txt`.

Left open: [rbaco-a2] lets a regulation that names no object cover a request for any object, while `derive-regulation-coverage.rq` lets it cover only requests that name no object. No dataset pairs such a regulation with such a request. Aligning the axiom with the query would need a fact that the request names no object in each first-order scenario whose proofs use coverage. D19 aligned them on 2026-11-03.

## D17. Query run time

The corrections of D15 made `run_queries.py` about seven times slower: 1,035 s after D16, against 152 s before D15. On 2026-11-01, on the user's word ("go ahead with the optimizations"), each costly step was made to run once:

- **Agents counted as one, derived once per dataset.** `derive-counted-as-one.rq` writes, for each conflicting agent designation, the agents it counts as one, the constraints it applies to and, for a dynamic designation, the instances it applies in, in the query-internal namespace `rbacow:`. Six queries read these instead of repeating the test in ten places. Only whether a designation is in force is still evaluated at each time.
- **Activation refusals read the role DSD reports**, as they already read the task DSD reports, instead of counting again. A report counts for each principal and instance of a request, the old test for the request as a whole; the two differ only for a request with two principals, or one inside two instances that both hold active roles, and no dataset has either.
- **Types closed once per dataset**, by the closure `a/rdfs:subClassOf*` computed and no more, so D16's reading of the data as asserted stands.
- **rdflib's evaluator steered.** Two hooks order a group's joins by how many terms remain unbound, and test each filter conjunct, EXISTS last, where its variables are first bound, within the filter's own scope. Each query is translated once, and each call writes its evaluation time into the translation. All three rely on rdflib's internals, so `run_queries.py` uses them under rdflib 7.6.0 only, the version they were checked under; under any other it lets rdflib parse and evaluate each query itself, more than ten times slower.

A fault turned up on the way. The conflict derivations required a constraint's `rdfs:label`, so an unlabeled constraint got no report, and the refusals that read reports would have let it pass; reading role DSD reports puts one more refusal behind them. A report now names the constraint's IRI when it has no label. The run took 62 s. The checks that no result changed, and the run times, are in the verification report, section 1.

## D18. Simplifications (2026-11-01)

A review for simplification on 2026-11-01 made nine proposals, and on the user's word ("Yes, go ahead") seven were carried out. Of the other two, `rl_check.py` was kept with a corrected description rather than retired, and the speed code of D17 was kept, since each part pays for itself: with one part off at a time the run took 168 s without the single translation, 113 s without join ordering and 509 s without the filter placement, against 62 s. The changes to what RBACO states or checks:

- **Subject descriptions removed.** Subject description (RBACO_0000010), has subject description (RBACO_0000104) and has subject type criterion (RBACO_0000304) let an access regulation assigned to no role definition cover any requester who met the description. No dataset used them, `docs/mapping.md` maps no pattern to them, and the queries' reading of them went beyond [rbaco-a2], which covers a request only through an active role for the definition a regulation is assigned to. An access regulation is now assigned to one role definition, and the queries agree with [rbaco-a2]. Attribute conditions remain on the object side (D11).
- **Three scenario act classes removed.** Act of voting, act of working and act of jury service (RBACO_0001013 to RBACO_0001015) stood for ROWLBAC's Vote, Work and JuryDuty, but the scenario's permissions name operations, which are plan specifications (D6), and nothing referred to the classes.
- **The explicit model retired.** `build_model.py` and its two theories tested the 23-axiom theory of 2026-10-29, which RBACO no longer has; the results stay in the verification report (section 7) and `docs/fol/model-results.txt`. Porting the model to the current theory was the alternative, as new work with an unknown outcome. `parse_check.py`, which nothing called, was deleted as well.

The rest is presentation. The README points to `run_all.sh` instead of repeating each step's command, the purchase results moved from `docs/botha-review.md` to the verification report (section 3), D17 was cut to its decisions, and `rl_check.py` describes itself as the consistency check that needs no Java.

## D19. Coverage as the queries read it (2026-11-03)

[rbaco-a2] let a regulation that names no object cover a request for any object, while `derive-regulation-coverage.rq` lets it cover only requests that name no object (D16, "Left open"). On 2026-11-03, on the user's word ("Yes, tighten it"), the axiom took the query's reading. Its object clause now has the query's three cases: the regulation names the object the request names; it names neither an object nor an object description, and the request names no object; or it has an object description that the requested object meets.

The third case rests on a predicate the logic leaves undefined. An object description's criteria are annotation values (RBACO_0000302, RBACO_0000303), and a requester office condition (RBACO_0000011) reads the requester's office, so whether an object meets a description depends on the request as well as the object. `rbaco-meets-description b e q` states it, and like `rbaco-in-force` and `rbaco-decided-before` it has no defining axiom; `derive-regulation-coverage.rq` tests it. Two readings without a new predicate were declined, since each leaves a case in which the axiom grants a request the query denies: treating the criteria as met does so through a permission whose criteria fail, and letting a regulation with a description cover nothing does so past a prohibition whose criteria hold.

The module keeps its 48 axioms and has 82 predicates. Three first-order scenarios gained the facts coverage now needs: that the covered request names no object (the vote scenario, probes 1 and 3) and that the covering permission has no object description (the vote scenario and probe 3; probe 1 stated it already). Probe 2's goal is negative and uses [rbaco-a2] only from coverage to its conditions, a direction the change strengthens, so its scenario gained nothing. No query or dataset changed, and the rerun of `run_all.sh` wrote the same query results, derived files and inferences, byte for byte. Every proof and model was found again with the same axioms used, and the hand-specified models satisfy the new theories (verification report, section 7).

## D20. The name RBACO (2026-11-03)

Before publication the ontology was renamed from RBO to RBACO, on the user's word ("Yes, RBACO"). The prefix `rbo` is taken: Bioregistry lists it for OBO Foundry's Radiation Biology Ontology, also built on BFO, with IRIs `http://purl.obolibrary.org/obo/RBO_`. Candidate names were checked against the listings of Bioregistry and 18 registries it mirrors, against w3id.org and against GitHub repository names. ACO was declined because an access control ontology already goes by it (arXiv 2101.03209), ROBAC because an access control model does (Zhang, Zhang and Sandhu 2006), and the free names with a BFO suffix (RBAC-BFO, ACBFO) because an edition on UFO may follow. RBACO, for Role-Based Access Control Ontology, is free in all of them. It reads like RBAC0, the base model of RBAC96 (Sandhu et al. 1996), so the README gives the expansion and says that RBACO also covers hierarchies and constraints.

The family is RBACO and this edition RBACO-BFO. Editions would share the name but not identifiers: a UFO edition would mint its own, and a mapping with verdicts would relate the two.

What changed, in every file except the 21 byte copies in `imports/`:

- Identifiers `RBO_0000001` onward became `RBACO_0000001` onward, with the same numbers, under `https://w3id.org/rbaco/bfo/` (before, the placeholder base `https://example.org/rbac-bfo/`). The w3id.org redirect is not registered yet, and the ontology's comment now says so instead of asking for the placeholder to be replaced. The example data moved to `https://example.org/rbaco/data/` and the queries' internal namespace to `https://example.org/rbaco/work#`.
- The prefixes `rbo:` and `rbow:` became `rbaco:` and `rbacow:`; the CLIF names `rbo-…` and axiom IDs `[rbo-…]` became `rbaco-…` and `[rbaco-…]`, and their LADR forms `rbo_…` became `rbaco_…`; the definition IDs `NNN-RBO` became `NNN-RBACO`. The files `rbo.*`, `rbo-domain.*`, `rbo-terms.csv` and `clif/rbo-access.cl` became `rbaco-bfo.*`, `rbaco-bfo-domain.*`, `rbaco-bfo-terms.csv` and `clif/rbaco-bfo-access.cl`, and the module names in the terms document and the run output follow the files. The ontology's title is "Role-Based Access Control Ontology, BFO edition (RBACO-BFO)".
- The records of earlier work were renamed too: this record, the verification report and `docs/fol/` name terms, axioms and files as they are named now, although the runs they report used the old names.

Nothing was modeled differently. The rename was made by a script of literal and regular-expression rules, and no old name is left outside this entry and the history note in D13. The byte copies kept their bytes, as both `SHA256SUMS` files confirm; the IAO extract, which `tools/build_iao_extract.py` writes, took the new base in its ontology IRI and the new name in its comment. Rerun on the renamed files, the generators rewrote the Turtle with only the label comments realigned, the RDF/XML as isomorphic graphs, and the terms document and the IAO extract byte for byte. `tools/run_all.sh` then gave every count in `docs/expected-results.md`: 32 of 32 queries and 15 of 15 probe expectations, 0 RL clashes, 8 of 8 DL inputs consistent and 8 of 8 negative controls rejected, 18 proofs from the same axioms under their new LADR names, 5 Mace4 models, and the same 3 searches ending at their time limit at size 3. The reports it rewrote matched the renamed copies apart from run times and one line: the first line of `docs/dl/inferences.txt`, where the script had shortened the module name to `rbaco` and the run wrote `rbaco-bfo`. The two theories in `docs/fol/` are byte-identical to the ones `tools/run_fol.py` writes now, and the hand-specified models gave 137 of 137 and 149 of 149 formulas true on them, as before.
