# Verification report

Everything measured or checked while building RBACO, dated 2026-10-29, re-run on 2026-10-30 for the extension after Botha and Eloff (2001), and re-run again on 2026-10-31 after the corrections of design-record D15 and once more after those of D16. On 2026-11-01, after the optimizations of D17, the query run was re-run and checked, and `run_all.sh` was run end to end on a copy, every result as before apart from run times. After the simplifications of D18 the same day, `run_all.sh` was run again in place: every verdict, report, inference and proof was as before, and only run times and the counts that included the removed terms changed. On 2026-11-03, after design-record D19 tightened [rbaco-a2], it was run in place once more: the query output, derived files and DL inferences came out byte-identical, every proof and model was found again, and the hand-specified models were rechecked on the new theories (section 7). Later that day, after the rename of design-record D20, it was run in place again, with every count, proof and model as before; the reports it rewrites changed only in run times and in the module name on the first line of `docs/dl/inferences.txt`, which the rename had shortened. The hand-specified models were rechecked with the same results. On 2026-11-04, after the Linux port of design-record D21, `run_all.sh` was run on Linux, in a Claude Code cloud container: every count, proof and model came out as before, and the reports, derived files and theories it rewrote differed from the Windows copies only in line endings and in the run times the port moved to the logs. The hand-specified models gave the same results there. A second run on Linux reproduced every file it writes byte for byte, and a rerun on Windows, reported on 2026-11-05, gave every result again and changed no file. Later on 2026-11-05, with the version IRIs of release 0.1.0 (design-record D22), it was run on Linux once more, with every result as before and every file it writes unchanged. Each tool named here is in `tools/`. The Python tools need Python 3 and rdflib, the DL checks Java and ROBOT (section 6), the first-order checks LADR (section 7); none needs network access. `docs/query-results.md` holds the full output of the last run. `MANIFEST.sha256` lists a hash for every file in the deliverable.

To regenerate the results, from the `rbaco-bfo/` directory:

```bash
python tools/run_queries.py . && python tools/rowlbac_checks.py . && python tools/rl_check.py .
```

`run_queries.py` rewrites `docs/query-results.md`, and the other two append to it.

## 1. What was checked

| Check | How | Result |
|---|---|---|
| Turtle and RDF/XML parse | `measure.py` | all parse; `rbaco-bfo.owl` and `rbaco-bfo-domain.owl` are isomorphic to the Turtle |
| Data files in dependency order | `ttl_ordered.py` on `data/*.ttl` | 0 forward references in all six, the probes included (the alphabetical files rdflib wrote before had 250, 110, 91, 75 and 944 for the first five, in the order of section 2); each of the five graphs isomorphic to the one before reordering, while `probes.ttl` was written in order from the start. None of the six has a reference cycle, so the order always exists. The derived files have no references between their own subjects |
| Label comments current | `annotate_ttl.py --check` | `rbaco-bfo.ttl`: 108 headers, 323 trailing comments; `rbaco-bfo-domain.ttl`: 24 and 30; the six data files 3,049 trailing comments (and 14 headers, for RBACO domain classes the data annotates); the five derived files 275; none stale. The commented data parses to the same graphs, and the query results are unchanged apart from row order. Adding them left both graphs isomorphic to their RDF/XML (1,088 and 151 triples), and HermiT reasons over the annotated files |
| No invented IRIs | `measure.py`: every `obo:` and `cco:` IRI used in `rbaco-bfo.ttl` and `rbaco-bfo-domain.ttl` looked up in `imports/` | 38 and 8 borrowed IRIs; none missing (the one hit is the BFO ontology IRI in `owl:imports`) |
| Imports unmodified | SHA-256 against the BFO 2020 and CCO v2.2 files the consult worked from | 8 of 8 byte-identical; hashes in `imports/SHA256SUMS` |
| SPARQL queries execute | `run_queries.py` | 32 of 32 run, no errors, over six datasets. After the simplifications of design-record D18, 63 s on 2026-11-01 within `run_all.sh`, and 63 s again on 2026-11-03 after D19, the run recorded in `docs/query-results.md`; after the optimizations of D17, 62 s the same day with nothing else running, of which 21 s on the purchase data and 14 s of that in `derive-ssd-conflicts.rq`; after the corrections of D16, 1,018 s and 1,035 s on 2026-10-31; after those of D15, 1,097 s; before them, 148 s on 2026-10-30 and 152 s on 2026-10-31. The output is ordered (D16): two runs on the same inputs wrote identical results apart from the elapsed time, and byte-identical derived files |
| The optimizations change no result | every query call of a full run evaluated both ways on the same graph (D17) | 0 differences: 1,675 calls with and without the evaluation hooks, on a run taken before the queries were rewritten; 846 calls of the six queries rewritten for agents counted as one, role DSD reports and constraint labels, against their old texts; 1,681 calls of the final runner against its previous path, the time substituted in the text, parsed at each call and evaluated by rdflib alone, which took 1,096 s of query time against 79 s. For every query, the translation with three evaluation times written into it in turn was identical to a fresh translation of the substituted text. Against the run of D16, `docs/query-results.md` differs only in the count of queries and the elapsed time, and the derived files are byte-identical |
| Scenario answers | `run_queries.py`, compared with ROWLBAC §3.1 and Botha and Eloff | all match (section 3); every activation verdict agrees with the data except the deliberate same-time variant of CR-42; the eight regression probes meet all 15 of their expectations |
| Asserted closures the queries rely on | `check-asserted-closures.rq`, among the checks `run_queries.py` runs | 0 rows in the four datasets it checks, and in the probe and RT data, run separately on 2026-10-31: every occurrent part of a task instance is asserted part of its business process instance, every task instance is part of one, and nothing is located in something located elsewhere without being asserted located there too. Three planted gaps, one of each kind, each gave its row |
| ROWLBAC's own rules | `rowlbac_checks.py` | DSoD rule fires on Bob's first activation; ssod closure gives Citizen ssod Citizen; Figure 5 does not entail ops ⊑ marketing (section 4) |
| Data consistency, partial | `rl_check.py`: a subset of the OWL 2 RL rules, then disjointness, complement and owl:Nothing clashes | 0 clashes in all six datasets; 4 of 4 negative controls detected |
| is about bridge | `rl_check.py` witnesses, and a hand proof (section 5) | holds in both directions |
| Defined-class classification (P15) | `rl_check.py` | printer-p43 is classified as a classroom printer and printer-p44 is not |
| CLIF syntax and signature | `check_clif.py` | 48 axioms, 48 distinct IDs, 82 predicates, all declared and used, one arity each, no free variables |
| `check_clif.py` calibration | run on the 13 BFO 2020 CLIF modules (generated 2025-12-05) | 12 pass; `universal-declaration.cl` fails on its unary `(universal X)` declarations, which the checker misreads as free variables |
| OWL 2 DL consistency and classification | HermiT 1.4.5.456 through ROBOT 1.9.8 (`run_dl.sh`), on `rbaco-bfo.ttl`, `rbaco-bfo-domain.ttl` and each dataset merged with its derived file, imports included | all eight consistent, no unsatisfiable classes (section 6) |
| DL negative controls | `make_dl_controls.py`, `run_dl_controls.sh` | 8 of 8 detected, including cardinality and datatype clashes the partial RL check cannot see |
| Silent merging | `dl_diff.py`: individuals with two values for a functional, exactly-1 or at-most-1 property, which a DL reasoner would identify instead of reporting | none in any dataset |
| CLIF consistency and entailments | Prover9 and Mace4 (LADR 2009-11A) on `rbaco-bfo-access.cl`, the OWL bridge and 9 BFO 2020 CLIF modules, translated by `clif2ladr.py` (`run_fol.py`); hand-specified models where Mace4 finds none (`check_hand_model.py`) | section 7 |

## 2. Measurements

| File | Triples |
|---|---:|
| `rbaco-bfo.ttl` / `rbaco-bfo.owl` | 1,088 |
| `rbaco-bfo-domain.ttl` / `rbaco-bfo-domain.owl` | 151 |
| `imports/bfo-core.ttl` (BFO 2020) | 1,014 |
| `imports/` CCO v2.2: Agent 1,225; Artifact 3,537; Event 2,285; ExtendedRelation 575; Geospatial 464; InformationEntity 1,800; Time 462 | 10,348 |
| `imports/iao-extract.ttl` (5 IAO terms) | 34 |
| ontology closure as loaded | 12,589 |
| `data/us-persons.ttl`, `code-review.ttl`, `abac.ttl`, `rt-policy.ttl`, `purchase.ttl`, `probes.ttl` | 515, 236, 218, 189, 2,061, 646 |
| `data/derived/` us-persons, code-review, abac, purchase, probes | 43, 20, 14, 185, 109 |

Terms (`rbaco-bfo-terms.csv`, 167 rows): 71 new classes (49 in `rbaco-bfo`, 22 in `rbaco-bfo-domain`), 49 new object properties (48 and 1), 5 data properties, 4 annotation properties, and 38 borrowed terms: 22 classes and 14 object properties from CCO v2.2 and BFO 2020 core, plus 1 class and 1 property from IAO. The queries total 1,546 lines.

The IAO extract drops two axioms, which `build_iao_extract.py` prints: IAO_0000104 and IAO_0000007 have `has part` (BFO_0000051) restrictions, and BFO 2020 core does not declare BFO_0000051.

## 3. Scenario results

All of these match what the scenario calls for. The tables are in `docs/query-results.md`.

**ROWLBAC §3.1 (US persons).**
- Alice as Citizen: vote, work and jury are granted, each citing its permission.
- Alice as Permanent Resident: work is granted; vote and jury are denied. A denial cites nothing because no permission applies.
- Alice's Permanent Resident assignment yields one SSD report against {Resident, Citizen}, because Permanent Resident is senior to Resident.
- Bob's Visitor activation is allowed.
- Bob's work request is denied, citing the Visitor prohibition.
- Bob's Temporary Resident activation is refused with a DSD report.
- Bob's Citizen activation is refused as not authorized.
- Every check query returns no rows: no cycles, a limited hierarchy, well-formed constraints, no drift between the two hierarchies, and active roles that are valid.

**CR-42 (code review, whole-instance DSD within the code-review plan).**
- Dana's push and Eve's approval are granted.
- Dana's approver activation at 12:05 is refused with a DSD report, although she dropped submitter at 12:00.
- Dana's approval request is denied.
- In the variant with the constraint retyped to same-time counting, the 12:05 request is allowed. That row reads `consistent = false` because the data still record the refusal: only the verdict changes in the variant.

**ROWLBAC §4.1 (attribute-based).** Marie may use printer p43 (a classroom printer, under the faculty permission) and display d7 (in her office o12, under the member permission). She is denied p44 (in a lab) and d8 (in office o13). `cq-usable-objects.rq` returns exactly p43 and d7.

**ROWLBAC §4.2 (RT, Figure 4).** In the current state, HQ.marketing, HQ.ops and HQ.staff are {Alice} and HR.employee is {Alice, Bob}. `rt-security-properties.rq` gives restriction proven and access, availability and safety not proven. Each "not proven" has a counter-state that respects the growth and shrink restrictions:
- Access: add `HR.manufacturing ← Carol`. Carol joins ops and not marketing.
- Availability: retract `HR.managers ← Alice`. Alice leaves marketing.
- Safety: add `HR.sales ← Carol`. Carol joins marketing.

Restriction holds in all four states.

**Botha and Eloff 2001 (purchase workflow).** `data/purchase.ttl` holds Figure 3's hierarchy with Figure 6's Approver added, the Figure 2 task specifications, Tom, Dick and Harry, a stores application host, an approval robot, and a workflow engine that issues the work items. Each Table 2 interpretation has a plan of its own, so its constraints apply only there. All constraints are issued on 1 January; Tom holds APM and Manager, Dick holds Stock Controller and Manager, Harry holds APM and Manager. Ten process instances run under those plans, and a static assignment tests Table 1:

| Instance | Plan | What it tests | Result |
|---|---|---|---|
| po-1 | conflicting roles | The WSession example (p.674): Tom takes the order-stock work item | APM refused (strict least privilege); Buyer allowed. Create order, view order, send e-mail and create requisition granted, the last two through Buyer's juniors; approve order denied. `check-task-specs.rq` flags send e-mail, create requisition and approve order as outside the task's needs |
| po-2 | conflicting roles | The bypass: Tom activates APM with no work item | Create requisition and approve order both granted; no conflict report. `check-sod-hierarchy.rq` warns that {Stock Controller, APM} holds a senior–junior pair |
| po-3 | conflicting permissions | The same two requests under a permission DSD | Create requisition granted; approve order denied, citing the permission DSD |
| po-4 | conflicting roles | Harry prepares the requisition as Stock Controller | Harry's later APM request refused (DSD); Tom's allowed, and Tom approves |
| po-5 | conflicting users | Dick prepares it; Tom and Dick count as one in this plan | Tom's APM activation allowed, since permission SoD refuses at the request; Tom's approve order denied, citing the permission DSD. The worklist at 09:30 offers the approval to Harry only |
| po-6 | conflicting tasks | Harry prepares it, then asks to approve | Refused (task SoD); Tom allowed |
| po-7 | Figure 6 | Tom prepares it as Stock Controller, then asks for Approver | Refused (DSD on {Stock Controller, Approver}); Harry allowed, approving under Approver's own permission |
| po-7b | Figure 6 | Tom activates APM with no work item | Activation allowed. Create requisition and approve order denied, citing the task-bound operation requirement for the Figure 6 plan; send e-mail, which it does not name, granted |
| po-10 | internal purchase order | The prototype run (pp.678–679): Tom completes the form | Worklist at 09:30: Harry only (Tom by task SoD, Dick through the designation, the robot by the human performer requirement). Dick refused (task SoD through the designation); Harry approves. Worklist at 10:05: the stores host; it issues the items |
| po-11 | internal purchase order | Automation | The approval robot, on Tom's behalf, refused (human performer, citing the requirement); a task DSD report is written as well, since its principal is Tom, who completed the form. The stores host refused issuing before any approval (prior task) |
| — | — | Dick, of Tom's family, assigned Auditor on 20 January | Three SSD reports through the static family designation: on {Auditor, APM}, on the permission set {approve order, approve audit}, and on the task set {approve order, approve audit} |

All 23 activation verdicts agree with the data, and the 24 access decisions are as listed. The warnings are as intended: `check-sod-hierarchy.rq` reports the internal purchase order task DSD as partly task-bound, since the requirement there names approve purchase order but not complete order form; `check-conflict-coverage.rq` reports Table 3 rows 3 and 4 for the stores sets, which no role constraint backs; `check-designation-chains.rq` reports Tom and Harry, joined to Dick by different dynamic designations and to each other by none; `check-limited-hierarchy.rq` reports APM's three immediate juniors (Figure 3 is a general hierarchy, and NIST's limited one allows a single junior). `cq-least-privilege-slack.rq` measures Botha's point about APM: the approve-order task's required role reaches six operations the task does not need, against one or two for every other task. `docs/botha-review.md` § Verification draws its finding on Figure 6 from po-7 and po-7b.

**Regression probes (design-record D15).** `data/probes.ttl` adds eight probes to the purchase data, dated after its last instance, each exercising a behavior the corrections changed. All 15 of their expectations hold, and `run_queries.py` fails if one does not:
1. Approver's approve-order permission has the content of APM's, a member of the conflicting-permissions set, so Tom's request through it after his requisition is denied, citing the constraint.
2. APM reaches approve order through two permissions of that set with one content, which count once: Tom's request is granted.
3. Two access requests at one instant are taken in IRI order: approve order is granted, and the requisition, which would then complete the set, is denied.
4. Harry loses Manager while it is active and never deactivates it: his later request is denied, and `check-active-roles.rq` reports the active role.
5. A designation of Tom and Dick issued after both their activations does not join them in that instance: both are allowed, with no DSD report.
6. Once the conflicting-users designation is retired, Tom and Dick no longer count as one: both their requests are granted.
7. Manager comes to inherit from Auditor, so Tom, and Dick through their family, are authorized for APM and Auditor together: issuing the inheritance statement yields six SSD reports, against the role, permission and task constraints.
8. Harry asks at one instant for APM and, through it, Stock Controller: the APM request sorts first and is fulfilled, so the conflicting-tasks DSD refuses the other.

## 4. ROWLBAC re-run

- **§3.3.5 DSoD rule, run on the triples as printed.** It fires for `act1`, Bob activating Visitor, because he is assigned Temporary Resident. With the symmetric `disjointWith` triple added, it fires for both activations. The activation rule fires for both as well.
- **§3.4.2 closure.** It gives Citizen ssod Citizen, Citizen ssod Resident, Resident ssod Citizen and Resident ssod Resident, with the same pattern for dsod. With Alice holding only Citizen, the SSODConflict rule fires with (Citizen, Citizen).
- **Figure 5.** 64 of 2,048 truth assignments satisfy the 12 class axioms. marketing ⊑ employee and ops ⊑ employee are entailed. ops ⊑ marketing is not: 3 counter-assignments, e.g. {employee, manufacturing, ops}. A brute-force check is a complete decision procedure here, because every Figure 5 axiom is Boolean over class names: with no properties, any model reduces to the types of its individuals.

## 5. The is about bridge, by hand

`cco:ont00001808 owl:equivalentProperty obo:IAO_0000136`.
1. IAO_0000136 has domain IAO_0000030 (IAO ICE), and cco:ont00001808 has domain cco:ont00000958 (CCO ICE).
2. Since the properties are equivalent, each domain applies to both.
3. IAO ICE ⊑ ∃IAO_0000136.entity (IAO), so an IAO ICE has an `is about` filler and is therefore a CCO ICE.
4. CCO ICE ≡ GDC ⊓ ∃cco:ont00001808.entity (CCO), so a CCO ICE has a filler and is therefore an IAO ICE.

So the two classes are equivalent. `rl_check.py` confirms steps 3 and 4 on witnesses. A side effect worth knowing: anything asserted to be about something becomes an ICE of both kinds, so the bridge would make an ontology inconsistent if it used either property on a non-GDC.

HermiT confirms the result: classifying `rbaco-bfo.ttl` with its imports infers `IAO_0000030 owl:equivalentClass cco:ont00000958` (section 6).

## 6. OWL 2 DL reasoning

Tools, fetched 2026-10-29: ROBOT 1.9.8 (`robot.jar`, 81,524,668 bytes, from the GitHub release ontodev/robot v1.9.8, SHA-256 `6f518b02…5f05f8`), which bundles HermiT 1.4.5.456 and OWL API 4.5.29; run on Java 24.0.2. `tools/run_dl.sh` merges each input with its imports through `catalog-v001.xml` and runs `robot reason --reasoner HermiT`, which exits non-zero on an inconsistent ontology or an unsatisfiable class. The run of 2026-10-29 took 41 s; the runs of 2026-10-30, with seven inputs, and of 2026-10-31, with eight, were not timed.

| Input | Triples merged | Result |
|---|---:|---|
| `rbaco-bfo.ttl` | 12,327 | consistent, no unsatisfiable classes |
| `rbaco-bfo-domain.ttl` | 12,469 | consistent, no unsatisfiable classes |
| `data/us-persons.ttl` + derived | 13,168 | consistent; 229 individuals, 1,765 inferred type assertions |
| `data/code-review.ttl` + derived | 12,789 | consistent; 152 individuals, 1,218 inferred type assertions |
| `data/abac.ttl` + derived | 12,760 | consistent; 147 individuals, 1,189 inferred type assertions |
| `data/rt-policy.ttl` | 12,689 | consistent; 119 individuals, 1,028 inferred type assertions |
| `data/purchase.ttl` + derived | 15,280 | consistent; 653 individuals, 4,439 inferred type assertions |
| `data/probes.ttl` + `purchase.ttl` + the probes' derived file | 16,014 | consistent; 820 individuals, 5,439 inferred type assertions |

Figures are from the run of 2026-11-01, after the simplifications of design-record D18. It gave the same results as the last run of 2026-10-31, after the corrections of D16, on 26 fewer triples for `rbaco-bfo.ttl` and 44 fewer for each other input. The earlier runs gave them on fewer ontology triples than that run of 2026-10-31: the run after the corrections of D15 on 4 fewer, the last run of 2026-10-30, for the first seven inputs, on 8 fewer still, and the 2026-10-29 run, for the first six, on 302 fewer than that. In the purchase dataset HermiT places each of the 11 SoD constraints under exactly one kind: 3 role, 4 permission, 4 task (RBACO_0000042–044). In the probes dataset it does the same for 12, the probes' own permission constraint among them. It can only because the dataset declares its role definitions, permissions and task specifications pairwise distinct (`owl:AllDifferent`): without that, OWL's lack of a unique-name assumption leaves no two members countable, and a first run classified none.

**Negative controls.** Each is a few-line ontology importing `rbaco-bfo-domain.owl` (`make_dl_controls.py`). HermiT rejects the original four: an individual that is both an access permission and an access prohibition (inconsistent); an active role `is activated in` two business process instances declared distinct (inconsistent, from the exactly-1 restriction on RBACO_0000003); a temporal instant with two different `has timestamp` values (inconsistent, from the functional data property RBACO_0000205); and a class below both permission and prohibition (1 unsatisfiable class). The second and third are clashes the partial RL check in section 1 cannot detect. Three controls added on 2026-10-30 are rejected as well, each as inconsistent: a task specification requiring two role definitions declared distinct (the qualified cardinality 1 on RBACO_0000040); a constraint naming two distinct roles and two distinct permissions, which falls under both the role and the permission SoD kinds, declared disjoint; and a same-time DSD over two permissions, since same-time DSD is a role SoD constraint. An eighth, added later that day, is also rejected as inconsistent: a task-bound operation requirement applying within two business process plans declared distinct (the at-most-1 on RBACO_0000050).

**What the classification adds** (`dl_diff.py`, from the last run of 2026-10-31; `make_inferences.sh` writes its output, the imports-only comparison and the controls' verdicts to `docs/dl/inferences.txt`):
- On RBACO's own classes: `assigned role` ⊑ BFO `role` (from its equivalent-class definition), the role, permission and task SoD kinds ⊑ SoD constraint (from their definitions), `classroom printer` ⊑ `printer` (a defined class, so this holds only under DL reasoning), and IAO ICE ≡ CCO ICE (the bridge).
- On the imported classes: 22 new subclass links. HermiT was also run on the imports alone (`imports_only.sh`). 13 of the 22 appear there too and come from BFO and CCO themselves, e.g. CCO's Multi-Day Temporal Interval ⊑ BFO temporal interval. The other 9 appear only with RBACO, and every one comes from the bridge: seven CCO ICE subclasses (Descriptive, Prescriptive, Designative, Representational, Religion, Ideology, Media Content Entity) fall under IAO ICE, and IAO's directive information entity falls under CCO ICE. RBACO changes nothing else in BFO, CCO or IAO.
- On the data: printer-p43 is classified as a classroom printer and printer-p44 is not, as in the RL check. The ten RT simple inclusion statements are classified as role inheritance statements, which `rbaco-bfo.ttl` asserts (RBACO_0000036 ⊑ RBACO_0000017): the body role is the senior.

**Silent merging.** OWL has no unique-name assumption. Two values for an exactly-1 or functional property therefore make a reasoner identify the two individuals rather than report a clash, unless they are declared distinct. `dl_diff.py` lists every individual with two or more values for a functional, inverse-functional, exactly-1 or at-most-1 property, across sub-properties. It finds none in any dataset, including for the two request properties declared functional on 2026-10-31 (RBACO_0000111, RBACO_0000137).

## 7. First-order checks of the CLIF module

**Tools.** Prover9 and Mace4 from LADR 2009-11A, built with gcc from w64devkit 2.10.0 (`w64devkit-x64-2.10.0.7z.exe`, 67,127,496 bytes, SHA-256 `18d0a4c7…6325e`). The source was github.com/ai4reason/Prover9, branch master at commit `cdca95a5…72e3` (`prover9.zip`, 2,311,747 bytes, SHA-256 `f360df49…ac7483`), fetched 2026-10-29 and built unmodified. Three POSIX headers needed shims on Windows, and none of them affects the search: `getrusage` (timing only), `fork` and `pipe` (used only by a search mode Prover9 never calls), and `SIGUSR1`. LADR's `clausetester` was built from the same source and relinked with a 512 MB stack, because reading a 20-element interpretation (the explicit model below) overflows the default stack. Since 2026-10-31 `mace4` is relinked the same way: on the corrected theory its search overflowed the linker's default 2 MB at domain size 3 and stopped with no result line (Windows status `0xC00000FD`). The shims and build steps are `tools/ladr/`. Rebuilt with them from a fresh unpack of the same zip on 2026-10-30, all three binaries were byte-identical to the ones the checks ran on; rebuilt again on 2026-10-31, `prover9` and `clausetester` were byte-identical once more, and `mace4` differed only in its stack reserve.

**Translation** (`tools/clif2ladr.py`). Each `cl:comment` axiom becomes one labeled LADR formula. `(instance-of x U t)` with a constant universal becomes `isa_U(x, t)`, so a model cannot identify two universals. A variable used only in universal positions is expanded over the universals in play: a conjunction for `forall`, a disjunction for `exists`. Run over all 13 BFO 2020 CLIF modules and `rbaco-bfo-access.cl`, the translator parses 343 + 48 axioms. Every predicate has one arity across all 14 files, so RBACO's use of BFO's relations agrees with BFO's on argument count and order. Only BFO [qkp-1] does not translate, and it holds by construction (below).

**Theories** (`tools/run_fol.py`, output in `docs/fol-results.md`):
- **RBACO**: the 48 axioms of `rbaco-bfo-access.cl` (23 on 2026-10-29; 20 added for Botha and Eloff on 2026-10-30, and [rbaco-g3] later that day; [rbaco-s15] to [rbaco-s18] on 2026-10-31, with the corrections of design-record D15, when one `rbaco-in-force` predicate replaced the two for statements; on 2026-11-03 [rbaco-a2] took the coverage query's reading of objects, with the undefined predicate `rbaco-meets-description`, D19). The Prover9 entailments after the first use 42 of them (the lemma, six): all but [rbaco-s6], which the first entailment derives, and the RT axioms [rbaco-t1] to [rbaco-t5]. The completion schema [rbaco-t5] now shares `rbaco-in-force` with the scenario facts, and with the RT axioms in, the CR-42 entailment had produced over 70,000 factors of input clauses, and begun no search, when it was stopped. Leaving premises out cannot make a proof unsound. Mace4 gets all 48.
- **BRIDGE**: 50 axioms taken from the HermiT-classified OWL (32 before the extension). They give each RBACO universal its BFO ancestors (e.g. `isa_rbaco_role_definition(x,t) → isa_generically_dependent_continuant(x,t)`), and add the OWL axiom that an active role specifically depends on an assigned role.
- **BFO**: 207 axioms from 9 modules: existence-instantiation, specific-dependency, generic-dependence, participation, occurrent-mereology, temporal-region, order, continuant-mereology and universal-declaration. Universals are expanded over the 31 in play: RBACO's 15 and CCO Person, their BFO ancestors, the temporal regions, and material entity (24 before the extension). Left out are 64 universal-declaration axioms naming a universal outside those 31, and [xtf-1] and [qkp-1]. Those two say that universals are pairwise distinct and are not particulars, which holds by construction when universals are predicate names rather than domain elements. The spatial, spatiotemporal, history and material-entity modules are not used, and the CLIF signature touches none of their relations. The location criteria of object descriptions do use one: located in (BFO_0000171), which `spatial.cl` and `spatiotemporal.cl` axiomatize, appears in `rbaco-bfo-domain.ttl` and in `derive-regulation-coverage.rq`, `cq-usable-objects.rq` and `check-asserted-closures.rq`. Those criteria are checked by the SPARQL runs only.

**Entailments (Prover9).** Each proof uses RBACO axioms only, so adding the BFO set cannot remove it.

| Goal | Premises | Result | Axioms the proof uses |
|---|---|---|---|
| [rbaco-s6] | [rbaco-s5], [rbaco-u4] | proved, 0.2 s | [rbaco-s5], [rbaco-u4] |
| CR-42, granted: Dana violates the whole-instance DSD constraint | RBACO, the scenario's facts | proved, 1.8 s | [rbaco-s2], [rbaco-s3], [rbaco-s5], [rbaco-u4] |
| Alice as Citizen may vote under a permission assigned to US Person | RBACO, the scenario's facts | proved, 0.7 s | [rbaco-a1] to [rbaco-a4], [rbaco-g3], [rbaco-h1], [rbaco-h2], [rbaco-s15] |
| Deny-overrides: a request covered by a permission and a prohibition is not granted | RBACO, two covering facts | proved, 0.8 s | [rbaco-a3] |
| po-2: Tom with APM alone has an active role for Stock Controller (the bypass) | RBACO, the scenario's facts | proved, 1.2 s | [rbaco-a0], [rbaco-h1], [rbaco-h2] |
| po-3: two grants citing the two permissions of a dynamic permission set violate it | RBACO, two grants | proved, 1.1 s | [rbaco-p1], [rbaco-s2], [rbaco-s9], [rbaco-s10], [rbaco-s17], [rbaco-u4] |
| po-10: Dick violates the task DSD through Tom's task instance and the designation | RBACO, the scenario's facts | proved, 1.0 s | [rbaco-p1], [rbaco-s2], [rbaco-s13], [rbaco-s14], [rbaco-u1], [rbaco-u2], [rbaco-u4] |
| po-11: the robot's task instance violates the human performer requirement, though performed on Tom's behalf | RBACO, the scenario's facts | proved, 4.2 s | [rbaco-g1], [rbaco-s2] |
| Lemma, both directions: with no designations, a static task set is violated exactly when the role set of its tasks' (distinct) required roles is | [rbaco-s1], [rbaco-s11], [rbaco-s12], [rbaco-u1], [rbaco-u3], [rbaco-k1], closure facts | proved, 0.1 s each | all six |
| po-7b: a request for a task-bound operation in a Figure 6 instance, part of no task instance, violates the requirement | RBACO, the scenario's facts | proved, 1.4 s | [rbaco-a1], [rbaco-g3], [rbaco-s2] |
| po-7: a request inside a task instance whose specification requires the operation does not violate it | RBACO, the scenario's facts | proved, 1.3 s | [rbaco-g3] |
| Near miss: a request inside a task instance whose specification does not require the operation violates it | RBACO, the scenario's facts, closure of the request's task instances and the task's specifications | proved, 1.5 s | [rbaco-a1], [rbaco-g3], [rbaco-s2] |
| po-7b: the request that violates the requirement is not granted | RBACO, the scenario's facts | proved, 1.5 s | [rbaco-a1], [rbaco-a3], [rbaco-g3], [rbaco-s2] |
| Probe 1: Tom, granted create requisition in an instance, is refused approve order through Approver's permission, which has the content of APM's | RBACO, the scenario's facts | proved, 32.9 s | [rbaco-a1], [rbaco-a2], [rbaco-a4], [rbaco-h2], [rbaco-p1], [rbaco-p2], [rbaco-s2], [rbaco-s15] to [rbaco-s18], [rbaco-u4] |
| Probe 2: a first request hitting two members of one content is not refused, since they count once | RBACO, the scenario's facts | proved, 1.3 s | [rbaco-a2], [rbaco-s15] to [rbaco-s18] |
| Probe 3: of two requests at one instant, the second in decision order is refused | RBACO, the scenario's facts | proved, 25.8 s | [rbaco-a1], [rbaco-a2], [rbaco-a4], [rbaco-h1], [rbaco-h2], [rbaco-p1], [rbaco-p2], [rbaco-s2], [rbaco-s15] to [rbaco-s18], [rbaco-u4] |
| Probe 3: the first is not refused | RBACO, the scenario's facts | proved, 1.9 s | [rbaco-a2], [rbaco-s15] to [rbaco-s18] |

Rows are from the run of 2026-10-31, on the 48-axiom theory, in which every goal of the 44-axiom run of 2026-10-30 was proved again. The run of 2026-11-01, after the simplifications of D18, gave the same result, axiom count, model size and axioms used in every row, at different times. So did the run of 2026-11-03, after D19 tightened [rbaco-a2], which `docs/fol-results.md` holds, except that probes 1 and 3 each have one more fact line, and the two refusals took 45.2 s and 36.3 s. [rbaco-s6] needs [rbaco-u4] as well, since [rbaco-s5] compares witnesses by same dynamic subject. The vote proof uses [rbaco-a4], with a fact that the request is part of no task instance, and [rbaco-g3] and [rbaco-s15], since [rbaco-a3] now withholds a grant from a request that violates a task-bound operation requirement or that a dynamic permission constraint refuses. The po-3 proof compares the two permissions by content ([rbaco-s17]). Since D19, the vote proof and the refusals of probes 1 and 3 derive coverage from facts that the request names no object and the permission names neither an object nor an object description. The two negative probe goals rest on closures of the scenario's facts, so their premises are shown consistent below.

The lemma first failed as a single biconditional over all of RBACO (300 s, no proof), and then, split and restricted to the six axioms, with only static designations excluded (no proof: Prover9 exhausted its search). The reason is [rbaco-u1]: it matches a designation's kind against a constraint's kind at any times, so a dynamic designation applies to a constraint that is an SSD constraint at one time and a DSD constraint at another. `rbaco-bfo.ttl` declares the two disjoint (RBACO_0000013, RBACO_0000014), but translated per time, disjointness does not exclude this, and the bridge carries only BFO ancestors. With dynamic designations excluded too, both directions prove at once. *Interpretation*: a constraint's kind does not change, so the gap is in the translation rather than in RBACO's intent; a rigidity axiom for the constraint kinds would close it.

In the CR-42 rows, "granted" is the counterfactual state the decision query tests: Dana's approver role active at 12:05 after her submitter role ended at 12:00.

**Satisfiability of RBACO with BFO (explicit model, 2026-10-29, 23-axiom theory).** Mace4 cannot search the 262-axiom set at the sizes the scenario needs. Run for 600 s on each of four scenarios, it reached domain size 4 or 5. Restricted to the 118 BFO axioms stated wholly in RBACO's BFO vocabulary, it did no better in 300 s. Instead, a script, `build_model.py`, wrote out the intended CR-42 model, and `clausetester` evaluated every formula in it. The script and its two theories were retired on 2026-11-01, since they test a theory RBACO no longer has (design-record D18); the results stay here and in `docs/fol/model-results.txt` as the record of that check. The model had 20 elements:
- Dana and the review;
- three temporal regions (the review's interval and two instants);
- the two role definitions, two assigned roles and two active roles;
- one instance of each other RBACO universal;
- a medium and a pattern that concretizes the policy texts;
- the review's first boundary.

Its relations were closed under BFO's inverse, dissective and subclass axioms, and RBACO's defined predicates computed from their definitions.

| Model | Formulas true | Meaning |
|---|---|---|
| CR-42 granted, whole-instance DSD | 297 of 297 | RBACO + BRIDGE + BFO + the scenario is satisfiable |
| CR-42 granted, same-time DSD, with Dana's active roles closed | 302 of 302; the violation goal is false | the same-time variant does not entail a violation |
| Negative control: one fact removed (a1 concretizes the submitter definition) | 295 of 297 | the tester reports exactly the removed fact and [rbaco-r2], which requires an active role to concretize a definition |

Building the model exposed 16 BFO commitments a scenario has to meet, and RBACO's data meets all of them once stated. Five matter for how RBACO data is written:
- Every generically dependent continuant is concretized at every time it exists ([ibk-1]). So a permission or constraint needs a carrier (a stored document) at every time it is in force.
- A process has a participant at every time it exists ([trl-1]).
- A process has a process boundary at its first or last instant ([aff-1], [qsp-1], [esh-2]).
- An instant is its own first and last instant ([nfo-1]).
- Anything occupying a region that precedes another region precedes it too ([wff-1]).

The datasets state participants (`has participant`, 21 uses) and first instants (`has first instant`, 54 uses). They give no permission or constraint a carrier: all 16 uses of `concretizes` have a role definition as object. They also give no process a boundary (no instance of BFO_0000035). RBACO's queries do not need either, and the OWL rendering does not require them, so the data is incomplete as a BFO description and not inconsistent with BFO.

**Countermodels (Mace4, RBACO + BRIDGE + scenario).**

| Scenario | Result | Reading |
|---|---|---|
| CR-42 granted, whole-instance | model, 3 elements, 2.7 s | consistent |
| Alice votes | model, 3 elements, 2.5 s | consistent |
| Visa gap: Bob has Visitor and Work Visa Holder active, DSD {Visitor, Temporary Resident}, Work Visa Holder senior to Temporary Resident | model, 3 elements, 24.9 s, with no violation | critique finding 16 holds formally: [rbaco-s3] counts only definitions concretized directly |
| CR-42 granted, same-time | no model in 300 s (size 3) | settled by the explicit model above, for the 23-axiom theory |
| po-2: APM alone, DSD {Stock Controller, APM}, APM senior through Buyer | model, 3 elements, 2.5 s, with no violation | the bypass holds formally: the DSD is silent while [rbaco-a0] reaches the junior |
| Probe 1: Tom's requisition granted, then approve order requested through Approver's permission | no model in 300 s (size 3) | consistent, by a hand-specified model (below) |
| Probe 2: a first request hitting two members of one content | model, 3 elements, 2.4 s | consistent |
| Probe 3: approve order and create requisition requested at one instant | no model in 300 s (size 3) | consistent, by a hand-specified model (below) |

All rows are from the run of 2026-10-31, on the 48-axiom theory; for the first five, the 44-axiom run of 2026-10-30 gave the same results. The runs of 2026-11-01 and 2026-11-03 gave the same result and model size in every row.

These models are small because OWL and CLIF have no unique-name assumption: Mace4 merges any constants the premises do not force apart. In the visa-gap model Bob, his Visitor active role and the Temporary Resident definition share an element. It is still a model of every stated premise, which includes Visitor ≠ Temporary Resident ≠ Work Visa Holder and the closure of Bob's active roles, so it refutes the goal. A full unique-name assumption was tried. It moves the search to 10–12 elements, where Mace4 ran out of memory grounding RBACO's six-variable definitions.

**Hand-specified models (2026-10-31, rechecked 2026-11-03).** For probes 1 and 3, Mace4 finds no model in 300 s at size 3. For probe 1, runs at sizes 4 to 6, with other options and with constants pinned to elements, did no better, and a Prover9 search for a contradiction in its premises found none. Small models exist, so these are search failures. `tools/check_hand_model.py` evaluates a hand-specified interpretation of each scenario instead (`docs/fol/hand-pdsd-same-content.py`, `hand-pdsd-same-instant.py`). The facts' atoms and a few stated ones are closed under the theory's atom-to-atom implications, and RBACO's defined predicates are computed from their definitions. LADR's `clausetester` then evaluates every formula independently (`docs/fol/model-results.txt`). The counts below are for the theories of 2026-11-03, to which D19 added one and two facts; on those of 2026-10-31 they were 136, 147 and 134 of 136.
- Probe 1 needs 3 elements. All 137 formulas are true, and so is the refusal of p11a.
- Probe 3 needs 5: [rbaco-h4] makes seniority acyclic, so the definitions of APM, Buyer and Stock Controller cannot share an element, and neither can the two inheritance statements. All 149 formulas are true, and so are the goals of p11c and p11d.
- A negative control, the probe-1 model with Tom's assigned role not concretizing the Approver definition, makes exactly [rbaco-r2] and the OWL dependence axiom false (135 of 137), in both evaluators.

**Not checked.**
- The 48-axiom theory with the BFO set. The explicit model of 2026-10-29 satisfied the 23-axiom theory only: the extension's definitions add up to nine quantified variables per formula, which `clausetester` would evaluate over 20⁹ assignments, and its script computed only the original defined predicates. So the extension and the corrections are shown satisfiable only without the BFO set, by the tier-1 models above (Mace4's and the two hand-specified ones); with it, they are unchecked.
- Satisfiability with the four BFO modules left out.
- The vote, visa-gap and probe scenarios against the BFO set.
- [rbaco-t1] to [rbaco-t5] against any scenario. The RT results rest on the SPARQL fixpoint (section 3), and since 2026-10-31 the Prover9 entailments leave these axioms out.
