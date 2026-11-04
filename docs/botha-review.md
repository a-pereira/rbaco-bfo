# Review: Botha and Eloff (2001) against RBACO

Source: R. A. Botha and J. H. P. Eloff, "Separation of duties for access control enforcement in workflow environments", *IBM Systems Journal* 40(3), 2001, printed pp.666–682 (17 PDF pages). Page numbers below are the printed ones. The paper presents CoAP, the "conflicting entities" administration paradigm, which states separation of duty (SoD) over four kinds of conflicting entity (users, roles, permissions, tasks), each either static (checked when associations are administered) or dynamic (checked by the workflow engine at run time).

The review was made against the draft of 2026-10-29. The alignment table and the finding below describe that draft. The ten proposals were then settled with the user and implemented in the draft of 2026-10-30, which is the one in this directory. Axiom labels such as [rbaco-s3] are those of `clif/rbaco-bfo-access.cl`.

Status: implemented and verified. The section "Implementation" says what changed during implementation, and "Verification" says where the results are and gives the finding they produced.

## How the paper was read

The text was extracted with pypdf 5 from the PDF supplied on 2026-10-30, now `sources/botha-eloff-2001.pdf`. Figures 3 and 6 (role hierarchies) and Table 3 were read from the PDF's drawing operators and glyph positions, not from a rendering, because no rasterizer was available. The script is `scripts/fig_lines.py` in the session scratchpad. Readings that depend on positions alone are marked as interpretation.

## The paper's model

A process definition is a set of tasks in a directed graph with predicates on the arcs; a process instance consists of task instances, and a human task instance is the responsibility of one user (pp.667–668). The worked example is a purchase process (Figure 2, p.669):

| Task | Document | Role in Figure 2 |
|---|---|---|
| 1 Prepare requisition | requisition form | Stock Controller |
| 2 Order stock | purchase order | Buyer |
| 3 Check funds | purchase order | Accountant |
| 4 Approve order (value ≥ 10 000) | purchase order | Accounts Payable Manager |
| 5 Send order to supplier | purchase order | Buyer |

Figure 3 (p.670), read from the arrow geometry, with arrowheads on the junior: Accounts Payable Manager (APM) → Buyer, APM → Accountant, Buyer → Stock Controller, Accountant → Clerk, Stock Controller → Employee, Clerk → Employee. The text says "Permissions are inherited upwards in the hierarchy" (p.669), with stock controller permissions inherited by the buyer (p.670). The permissions named are create order, create requisition, create rejection letter, approve order, confirm funds for order, view order, send e-mail (Figures 4 and 5, pp.672, 675).

A WSession is "a run-time mapping of one user to the most junior role required for a specific task" (p.674). It allows the activation of a single role, the one associated with the task, which the user must hold or hold a senior of; it lasts from when the user starts work on a task instance to when they stop or suspend it, so one task instance may need several WSessions; the user who selects a worklist item accepts responsibility for the task instance and is recorded on it (p.674). Tom, an APM, acting on "order stock", receives only create order, create requisition, view order and send e-mail, "directly or through inheritance" from the buyer role (p.674).

## Alignment

| Botha pattern | Locator | RBACO counterpart | Verdict |
|---|---|---|---|
| Process definition, process instance | pp.667–668 | business process plan (RBACO_0000005), business process (RBACO_0000004) | exact |
| Task definition as part of a process definition; task instance as part of a process instance | pp.667–668, Fig. 2 | none | no-counterpart |
| Task requires a role | Fig. 2; p.674 | none; regulations attach to role definitions only | no-counterpart |
| User accepts responsibility for a task instance | p.674 | none | no-counterpart |
| Role hierarchy, permissions inherited upward | pp.669–670 | role inheritance statement, [rbaco-h1]–[rbaco-h3], [rbaco-a0] | exact |
| WSession: one user, one role, one task instance, transient | p.674 | active role (RBACO_0000003) activated in a business process instance: one role, one bearer, transient | narrower on RBACO's side of the scope: RBACO activates in the process instance, Botha in a task instance |
| Strict least privilege: the most junior role the task requires | p.674 | none; [rbaco-r2] allows any role the user is authorized for | no-counterpart |
| Authorization rechecked when a task is started | p.674 | decide-activation.rq, decide-access.rq evaluate at request time | exact |
| Static conflicting roles (Table 1 row 1) | p.673 | static SoD constraint (RBACO_0000013), [rbaco-s1] | exact |
| Static conflicting permissions (Table 1 row 2) | p.673 | none; SoD constrains role definitions only (RBACO_0000114) | no-counterpart |
| Conflicting users, "considered as the same user" (Tables 1 and 2 row 3) | pp.673, 676 | none | no-counterpart |
| Static conflicting tasks (Table 1 row 4) | p.673 | none | no-counterpart |
| Dynamic conflicting roles, per process instance, across WSessions (Table 2 row 1) | pp.674, 676 | whole-instance DSD (RBACO_0000016), [rbaco-s5] | exact |
| Dynamic conflicting permissions, history-based ("has exercised") | p.675; Table 2 row 2 | none, though grants citing regulations (RBACO_0000113) on requests in an instance carry the history | no-counterpart |
| Dynamic conflicting tasks, "different people for each process instance" | p.676; Table 2 row 4 | none | no-counterpart |
| Conflicts scoped to a process definition | Fig. 8, p.678 | applies within (RBACO_0000115), [rbaco-s2] | exact |
| Cross-entity rules for administration (Table 3) | p.679 | none | no-counterpart |
| Worklist: accepted tasks, plus tasks needing a role the user is senior-or-same to, minus conflicting ones | p.680 | none | no-counterpart |

## Finding: the hierarchy bypass

Botha's remedy for dynamically conflicting roles related by the hierarchy (p.675) is to re-engineer it: "approve order" moves to a new Approver role that is not senior to Stock Controller (Figure 6, p.676). The paper's stated reason is least privilege: APM inherits the stock controller's permissions.

RBACO meets the same hierarchy differently, and the consequence is a gap. DSD counts only explicitly activated roles ([rbaco-s3]), so a whole-instance DSD on {Stock Controller, APM} does not fire when Tom activates APM alone. Access, however, reaches juniors' regulations ([rbaco-a0]). With Figure 3's hierarchy and APM active in one instance, Tom can be granted both create requisition and approve order, and no RBACO constraint reports it.

> [!interpretation] Reviewer's reading, not asserted by either source
> Counting inherited roles in DSD would not close the gap. With {Stock Controller, APM} constrained and APM senior, every APM activation would violate the constraint by itself, so the constraint would forbid the role it constrains. This is the self-defeat the paper's re-engineering avoids. The gap is closed by constraining what Tom does (permissions or tasks), not which roles he holds.

## Table 3

Table 3 (p.679) says which associations the administration tool allows (3) or disallows (8). Its glyphs survive extraction but not their columns. Read from their x positions against the column headers:

| Row | Users | Roles | Permissions | Tasks |
|---|---|---|---|---|
| Conflicting users | | conflicting ✗, non-conflicting ✓ | | |
| Conflicting roles | conflicting ✗, non-conflicting ✓ | | conflicting ✓, non-conflicting ✓ | conflicting ✓, non-conflicting ✗ |
| Conflicting permissions | | conflicting ✓, non-conflicting ✗ | | |
| Conflicting tasks | | conflicting ✓, non-conflicting ✗ | | |

> [!interpretation] Reviewer's reading, not asserted by the paper
> The first, third and fourth rows are two glyphs each at x ≈ 258, inside the Roles column (x ≈ 250–350). The second row's eight glyphs start at x ≈ 160 and are assumed to fill Users, Permissions and Tasks in order; that assignment is not certain. The fourth row agrees with the text: "if conflicting tasks are associated with nonconflicting roles, the tool will suggest that the roles are made conflicting" (p.679).

## Inconsistencies in the paper

The prose pairs "create requisition" with "approve order" as dynamically conflicting permissions (p.675); Table 2 pairs "create order" with "approve order" (p.676). The prototype names its conflicting tasks "complete order form" and "approve order" (p.678), and the conflicting-task prose names "create requisition form" (p.676). The dataset proposed below uses the prose pairing for permissions and states the other.

## Proposals

As first put to the user. The discussion record below is what was adopted.

1. **Tasks.** Add task specification (a part of a business process plan, requiring one role definition) and task instance (an occurrent part of a business process, prescribed by a task specification, with the agent who accepted it).
2. **WSession and strict least privilege.** Let an active role optionally be activated for a task instance within its process instance, and add a check that such an active role concretizes the task's required role definition itself, not a senior.
3. **Generalize SoD constraints beyond roles.** Split the role-set restriction off the SoD constraint so that a constraint can name a set of access permissions or task specifications instead.
4. **Permission-based SoD.** Static: no agent authorized for every permission in the set. Dynamic: no agent granted requests citing n permissions from the set within one fitting instance (history-based).
5. **Task-based SoD.** Static: no agent authorized for the required roles of conflicting tasks. Dynamic: conflicting task instances in one process instance accepted by different agents.
6. **Conflicting users.** A designation naming a group of agents to be counted as one agent by the constraints it is attached to.
7. **Hierarchy check.** A query reporting role SoD constraints whose role set holds a senior–junior pair, with the paper's remedy and the bypass above as its explanation.
8. **Table 3 coverage checks and the worklist.** Queries for the cross-entity rules read above (marked as interpretation where Table 3 is), and a worklist competency question following p.680.
9. **Workflow automation as an agent.** The system that runs the workflow engine is a CCO Agent ("A Material Entity that bears an Agent Capability", ont00001017), not the software, which IAO files under plan specification (IAO_0000010 ⊑ IAO_0000104). Automated tasks then require a role like human ones, automation's permissions are assigned and least-privileged, and its acts enter the same history as people's. Botha has no automated performers: automated activities appear only as something administrators "manually intervene in" (p.668) and as what a module of the prototype "executes" (p.679).
10. **Human in the loop.** SoD counts distinct agents, so Tom creating an order and the automation agent approving it satisfies a task constraint on {create, approve}. Two additions close this. A human-performer requirement on a task specification within a plan: the accepting agent of its instances is a CCO Person (ont00001262), checked at acceptance and, through a prohibition on the completing task in an instance without such an acceptance, at completion. And a new relation, acts on behalf of, so that automation acting for Tom counts as Tom in SoD (proposal 6's collapse, applied to delegation).

## Discussion record

Settled with the user on 2026-10-30:

- Proposals 9 and 10 are added.
- Proposal 1: acceptance is CCO has agent (ont00001833) on the task instance. No separate acceptance act: Botha has the accepting user complete the task instance (p.674), and a commissive act by the automation agent would read oddly.

- Proposal 1: each task specification requires exactly one role definition (OWL qualified cardinality 1), automated tasks included, since proposal 9 gives the automation agent roles. Under OWL's open world, a task specification with no stated role is not inconsistent, only incomplete, so HermiT cannot catch it. A SPARQL check catches a missing role; a DL negative control catches two required roles declared distinct, which violates the upper bound.

- Proposal 1: a requires operation property from task specification to the operations it needs (IAO plan specifications, as for has operation), used by checks only: coverage, least-privilege slack, conflicting tasks implying conflicting permissions (p.671), and requests outside the task's needs. Access is still granted only through the required role. Proposal 1 is settled.

- Proposal 2, all three parts. (a) A new property is activated for, from an active role to at most one task instance, which must be an occurrent part of the business process instance the role is activated in; the process instance stays the activation context, so whole-instance DSD is unchanged, and the binding is optional because "not all access control decisions in an organization will be made in the context of a workflow" (p.671). (b) Strict least privilege as a CLIF commitment checked by query, in the pattern of [rbaco-h4]: a task-bound active role concretizes the task's required role definition itself and is borne by the task instance's agent; decide-activation.rq refuses any other task-bound activation. (c) A request that is an occurrent part of a task instance is covered only through an active role activated for that task instance; other requests are decided as before. Part (c) changes [rbaco-a2].

- Proposal 3 as designed. Three defined, pairwise disjoint subclasses of the SoD constraint: role SoD constraint (≥2 has constrained role definition), permission SoD constraint (≥2 of a new has constrained permission, range access permission), task SoD constraint (≥2 of a new has constrained task specification). The minimum of two moves from RBACO_0000012 into these; the cardinality ≥2 stays on RBACO_0000012; the static/dynamic axis is unchanged. Same-time DSD (RBACO_0000015) becomes a subclass of role SoD constraint; whole-instance DSD applies to all three. Sets are homogeneous: a constraint naming two of each of two kinds is inconsistent (new DL negative control), one naming one of each is caught by SPARQL. Conflict reports gain describes conflicting permission and describes conflicting task specification.

- Proposal 4, enforced at requests only. Static: an agent is authorized for a permission when authorized ([rbaco-h3]) for a role definition it is assigned to, and violates by being authorized for two in the set (the [rbaco-s1] schema); subject-description permissions are out of scope, as in [rbaco-a2]. Dynamic, whole-instance: "exercised p in i" is read as granted a request that is an occurrent part of i by a grant citing p, since RBACO records requests and decisions, not performed acts; decide-access.rq refuses the request that would complete the set. Activations are not refused, which departs from the paper: there a user who has exercised one conflicting permission "will not be able to assume" a role granting the other (p.675), and a conflicting user may not "activate a role that would provide him with" it (p.676). Refusing the activation would block the role's harmless permissions, and the worklist of proposal 8 already withholds the task. Cites regulation (RBACO_0000113) widens its range to access regulation ⊔ SoD constraint, so that a denial can cite the constraint that refused it.

- Proposal 5 as designed. Static: "can do" a task is being authorized ([rbaco-h3]) for its required role, and a violation is being so for two task specifications in the set; stated directly, with its equivalence to SSD over the required roles as a Prover9 lemma. A check reports constraints no holder of a role can satisfy: two tasks sharing a required role, or one required role senior to the other (Botha's hierarchy problem in static form: an APM is senior to Stock Controller in Figs. 3 and 6). Dynamic, whole-instance: one agent (has agent, after proposal 6) of task instances of two distinct specifications in the set within one fitting process instance; repeated instances of one specification do not count twice. Enforced at the task-bound activation: role activation request gains requests activation for, and decide-activation.rq refuses it when the requester is already agent of a conflicting task instance in the process instance. (Settled with a task instance as its range; changed during implementation to a work item, proposal 8, because a refused request leaves no task instance to name.)

- Proposal 6, with designations not chained. A conflicting-agent designation (CCO Prescriptive ICE) names two or more agents directly, or a CCO Group of Agents (ont00000300) whose member parts (BFO_0000129) at t count as one, so a CCO Family (ont00000837) gains members without edits. Static and dynamic subclasses mirror SSD and DSD; dynamic ones may be scoped by applies within (RBACO_0000115, domain widened); a designation naming no constraint applies to every constraint of its kind. A relation same SoD subject (x, y, c, t) holds when x = y or both fall under one designation applying to c, and every SoD axiom compares witnesses with it instead of identity; proposal 10's acts on behalf of joins it as a further disjunct. Static designations act at role assignment ("may therefore not be assigned", Table 1). Not transitive: two designations sharing an agent do not make the other two one subject, which in the prototype would block Harry (p.679); a check reports such chains. Transitive closure is not first-order definable, so chaining would also have split the CLIF from the SPARQL.

- Proposal 7, as a warning. check-sod-hierarchy.rq reports role SoD constraints whose set holds a senior–junior pair at the evaluation time. Static: the senior cannot be assigned without violation. Dynamic: activating the senior alone never fires the constraint ([rbaco-s3]) while [rbaco-a0] gives it the junior's regulations (the bypass). Remedies offered: re-engineer the hierarchy (Fig. 6, p.676), or constrain permissions or tasks (proposals 4, 5). Proposal 5's seniority test shares the query. A warning, not a failure, because no axiom is broken, unlike [rbaco-h4].

- Proposal 8 with work items. Table 3 checks, static and as warnings: row 3 (permissions in a static permission SoD held by roles no static role SoD covers; more strongly, one role holding two of them) and row 4 (conflicting tasks whose required roles are not conflicting, with the paper's remedy, p.679). Row 1 is subsumed by proposal 6; row 2 is not implemented, because its glyphs cannot be placed. A new class, work item: a CCO Prescriptive ICE prescribing a task instance of a task specification within a business process instance, issued when the task is enabled; on acceptance the task instance begins and is prescribed by it as well as by its task specification. An unaccepted task is not yet a task instance, since it has no agent and has not begun. cq-worklist.rq follows p.680: unfinished task instances x is agent of, plus unfulfilled work items whose required role x is authorized for, minus those whose acceptance would break a dynamic task SoD, a permission SoD (through requires operation) or a human-performer requirement, after proposal 6's collapse.

- Proposal 10, on behalf of attaches to acts. A new relation is performed on behalf of runs from a planned act (task instance, access request) to an agent. An act's principal is that agent if any, else its own agent, and SoD compares principals after proposal 6's collapse. Agent-to-agent would have made every act of a shared workflow host count as every user's. PROV-O's counterpart is the qualified form (prov:Delegation with its activity), recorded by annotation, not imported. The human-performer requirement reads the agent, not the principal, so automation acting for Tom fails it as well as SoD.

- Proposal 10, unconditional completion guard. A new property requires prior runs from a task specification to one that must precede it (Task 5 to Task 4). decide-activation.rq refuses a task-bound activation for the later task unless the process instance holds a finished instance of the earlier one whose agent is a Person. (Settled with a further condition, that the earlier instance's principal differ from the creator's. Implementation dropped it from the guard, since a task SoD on {create, approve} already enforces it, at the approving task's own activation; the guard keeps one job.) The guard is scoped by the plans the task specification is part of. Fig. 2's arc predicates (approval only at value ≥ 10 000, p.669) are routing logic RBACO does not model; a branching route must make the branch visible in its plans. The verification dataset uses an order above the threshold.

All ten proposals are settled.

- Later on 2026-10-30, after the Figure 6 finding below: task-bound operations, strong form. The question was whether a plan with task specifications should require every activation in it to name a work item. That would break the datasets that have no workflow, so binding stays optional for activations and is required instead for named operations. A task-bound operation requirement (RBACO_0000050, a CCO Process Regulation, optionally scoped by applies within) names operations (RBACO_0000148). A request for one is denied unless it is part of a task instance whose specification requires that operation (RBACO_0000133), [rbaco-g3]. The weak form, any task instance at all, was declined because a task whose role reaches the operation through the hierarchy would carry it. decide-access.rq checks the requirement after prohibitions and before permission SoD, and cites it. check-sod-hierarchy.rq warns when a requirement names some of a dynamic set's operations but not all, since an unbound activation still reaches the rest.

## Open questions

- Conditional completion guards: a guard that holds only when an arc predicate does (Fig. 2, `VALUE >= 10000`) would need the predicate's value at evaluation time, and RBACO keeps document criteria outside its logic, as it does for object descriptions.
- Table 3 row 2: its glyphs cannot be placed in their columns from the PDF's text layer; a rendering of p.679 would settle it.
- Task-bound operations count only direct permissions when check-sod-hierarchy.rq judges a role set: an operation a role definition reaches through a junior (Stock Controller reaches send e-mail through Employee) does not make the set partly bound. Whether it should depends on which operations a role set is meant to separate, which Botha and Eloff do not say.
- [rbaco-u1] matches designation and constraint kinds at any times. A rigidity axiom for the constraint kinds, or a time argument on [rbaco-u1], would let the static-task lemma (`docs/verification.md` section 7) hold with only static designations excluded.

Measurements behind proposal 10: an absence search of CCO v2.2 (12 modules, 1,572 declared terms) for behalf, delegat, artificial agent, software agent and automat matched only Semi-automatic Pistol. RO (755 declared terms) has no match for behalf or delegat. PROV-O (W3C Recommendation 2013-04-30) has prov:actedOnBehalfOf and prov:Delegation, but is not built on BFO, so RBACO would mint its own relation and record PROV-O's as a counterpart, without importing it.

## Implementation

The draft of 2026-10-30 adds 11 classes (RBACO_0000040–050) and 17 object properties (RBACO_0000132–148), widens the range of cites regulation (RBACO_0000113) and the domain of applies within (RBACO_0000115), and moves the two-role minimum off RBACO_0000012. `clif/rbaco-bfo-access.cl` grows from 23 to 44 axioms, and `queries/` from 19 to 28 files. RBACO_0000050, RBACO_0000148 and [rbaco-g3] came after the ten proposals, from the discussion recorded above. Two settled points changed while being implemented, and the discussion record above says so where each was settled: requests activation for names a work item, not a task instance, and the completion guard no longer compares principals.

| Botha pattern | Locator | RBACO counterpart now |
|---|---|---|
| Task definition, task instance | pp.667–668 | task specification (040), task instance (041) |
| Task requires a role | Fig. 2; p.674 | requires role definition (132), exactly one ([rbaco-k1]) |
| User accepts responsibility | p.674 | CCO has agent on the task instance |
| WSession | p.674 | is activated for (136), [rbaco-k2], [rbaco-a4] |
| Strict least privilege | p.674 | [rbaco-k3]; decide-activation.rq refuses a task-bound request for any other definition |
| Static conflicting permissions, tasks | p.673 | permission and task SoD constraints (043, 044), [rbaco-s7], [rbaco-s8], [rbaco-s11], [rbaco-s12] |
| Conflicting users | pp.673, 676 | conflicting agent designations (045–047), [rbaco-u1]–[rbaco-u4] |
| Dynamic conflicting permissions | p.675 | [rbaco-s9], [rbaco-s10], `derive-permission-dsd-conflicts.rq` |
| Activation refused after a conflicting permission was exercised | pp.675–676 | Not adopted: `decide-access.rq` refuses the access request instead ([rbaco-s15]), so the role's other permissions stay usable (proposal 4) |
| Dynamic conflicting tasks | p.676 | [rbaco-s13], [rbaco-s14], `derive-task-dsd-conflicts.rq` |
| Table 3 rows 1, 3, 4 | p.679 | `derive-ssd-conflicts.rq` (row 1, through static designations); `check-conflict-coverage.rq` (rows 3, 4) |
| Worklist | p.680 | work item (048), `cq-worklist.rq` |
| Not in Botha: automation, principals, human in the loop, prior task | | is performed on behalf of (143), [rbaco-p1]; human performer requirement (049), [rbaco-g1]; requires prior (144), [rbaco-g2] |
| Not in Botha: operations bound to their tasks | | task-bound operation requirement (050), requires task binding for (148), [rbaco-g3] |

## Verification

The purchase dataset (`data/purchase.ttl`) runs the paper's workflow through every check, and its results are in `docs/verification.md`: the instance-by-instance table in section 3, the DL results and the four negative controls added for the extension in section 6, and the Prover9 proofs and Mace4 models in section 7. One finding came out of them.

**Finding: the Figure 6 remedy depends on task binding.** po-7 and po-7b differ only in whether Tom's activation names a work item. Bound, strict least privilege gives him Approver and the DSD refuses it. Unbound, APM is still senior to Stock Controller through Buyer, so before the task-bound operation requirement both conflicting operations were granted with no report, as in po-2. Re-engineering the hierarchy closes the bypass only where the conflicting operations cannot be reached outside their tasks. With the requirement in the Figure 6 plan, po-7b's activation is still allowed, but both operations are denied and the operation it does not name is granted.

> [!interpretation] Reviewer's reading
> Botha and Eloff can rely on the hierarchy alone because their engine activates roles only through WSessions (p.674). RBACO keeps unbound activation, since not every access decision is made inside a workflow (p.671), and binds operations instead of activations. Permission or task SoD (po-3, po-6) also closes the gap, without naming operations.
