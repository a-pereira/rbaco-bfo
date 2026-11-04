(cl:comment '
RBAC on BFO (RBO) access module, draft of 2026-11-03
Companion to rbo.owl. It states, in first-order logic, the parts of the RBO account that OWL 2 DL cannot:
time-indexed seniority, the counting in separation-of-duty constraints over roles, permissions and tasks,
agents counted as one, task-bound activation and operations, deny-overrides, and RT role linking.
Written in the style of the BFO 2020 CLIF modules (ternary instance-of, time-indexed continuant relations,
one axiom per cl:comment with an axiom ID). License: CC BY 4.0 (placeholder).

Name mapping. BFO 2020 names are used as in the BFO CLIF. Other names map to OWL terms as follows:
  rbo-role-definition            RBO_0000001   rbo-assigned-role         RBO_0000002
  rbo-active-role                RBO_0000003   rbo-business-process      RBO_0000004
  rbo-access-permission          RBO_0000007   rbo-access-prohibition    RBO_0000008
  rbo-ssd-constraint             RBO_0000013   rbo-same-time-dsd         RBO_0000015
  rbo-whole-instance-dsd         RBO_0000016   rbo-role-assignment       RBO_0000028
  rbo-activated-in               RBO_0000106   rbo-assigned-to           RBO_0000105
  rbo-has-operation              RBO_0000101   rbo-has-access-object     RBO_0000102
  rbo-has-object-description     RBO_0000103   rbo-has-requester         RBO_0000107
  rbo-requests-operation         RBO_0000108   rbo-requests-access-to    RBO_0000109
  rbo-constrains                 RBO_0000114   rbo-applies-within        RBO_0000115
  rbo-senior-to                  RBO_0000120 (here time-indexed)
  rbo-member-of                  RBO_0000131   rbo-has-cardinality       RBO_0000201
  rbo-dsd-constraint             RBO_0000014   rbo-access-grant          RBO_0000022
  rbo-task-specification         RBO_0000040   rbo-task-instance         RBO_0000041
  rbo-static-designation         RBO_0000046   rbo-dynamic-designation   RBO_0000047
  rbo-human-requirement          RBO_0000049   rbo-decides-on            RBO_0000112
  rbo-cites                      RBO_0000113   rbo-requires-role         RBO_0000132
  rbo-constrains-permission      RBO_0000134   rbo-constrains-task       RBO_0000135
  rbo-activated-for              RBO_0000136   rbo-designates-agent      RBO_0000138
  rbo-designates-group           RBO_0000139   rbo-applies-to-constraint RBO_0000140
  rbo-on-behalf-of               RBO_0000143   rbo-requires-prior        RBO_0000144
  rbo-requires-human             RBO_0000145   rbo-requires-operation    RBO_0000133
  rbo-task-binding-requirement   RBO_0000050   rbo-requires-task-binding RBO_0000148
  cco-prescribed-by              cco:ont00001920   cco-has-output        cco:ont00001986
  cco-has-agent                  cco:ont00001833   cco-person            cco:ont00001262
  rbo-has-head                   RBO_0000116   rbo-has-body              RBO_0000117
  rbo-has-senior                 RBO_0000118   rbo-has-junior            RBO_0000119
  rbo-names-member               RBO_0000122   rbo-has-linking-base      RBO_0000123
  rbo-linked-role                RBO_0000203
  rbo-role-of-name               no single OWL counterpart: rbo-role-of-name y n e holds when e has role
                                 issuer (RBO_0000121) y and has RT role name (RBO_0000202) n
  rbo-in-force                   no OWL counterpart: an information content entity is in force at t when its
                                 issuing act (RBO_0000031) starts at or before t and no retiring act
                                 (RBO_0000032) with it as input does (the scope note of RBO_0000032);
                                 derive-in-force.rq computes it
  rbo-decided-before             no OWL counterpart: request q1 is decided before q2 when q1 is earlier, or
                                 at the same time with a smaller IRI; the queries compute it
  rbo-meets-description          no OWL counterpart: rbo-meets-description b e q holds when, at the time of
                                 q, object b is an instance of every object type criterion (RBO_0000302) of
                                 description e, is located in an instance of every object location type
                                 criterion (RBO_0000303), and, if e is a requester office condition
                                 (RBO_0000011), is located in an office (RBO_0001101, rbo-domain.ttl) of the
                                 requester of q; derive-regulation-coverage.rq tests it
  rbo-senior-or-same, rbo-authorized-for, rbo-scope-fits, rbo-explicitly-active, rbo-request-time,
  rbo-active-for, rbo-active-for-request, rbo-covers, rbo-warrants-grant, rbo-principal, rbo-designates,
  rbo-designation-applies, rbo-same-static-subject, rbo-same-dynamic-subject, rbo-authorized-for-permission,
  rbo-exercised, rbo-authorized-for-task, rbo-performed, rbo-same-content, rbo-hits, rbo-exercised-before,
  rbo-refuses-permission-dsd, rbo-violates-*
                                 defined here; the SPARQL queries compute them

None of these axioms forbids a violation. Constraints and regulations are prescriptive information content
entities, and a conflict report describes an act that went against one, so the violation predicates are
defined (iff), never denied. The SPARQL queries are the operational reading of the definitions. The
commitments are structural: what an active role is ([rbo-r1]-[rbo-r4], [rbo-k2], [rbo-k3]), that seniority is
acyclic ([rbo-h4]), and that a task specification requires exactly one role definition ([rbo-k1]).

Two limits of the first-order reading, neither of which the queries share. [rbo-h1] is an equivalence, not an
inductive definition. With [rbo-h4], every finite model gives rbo-senior-to exactly the transitive closure of
the links [rbo-h1] admits, but an infinite one can add more (a densely ordered chain of further definitions
satisfies it), so no axiom here entails that one definition is not senior to another; the queries compute the
closure. [rbo-s4] and [rbo-s5] both define rbo-violates-dsd, each for its own kind of constraint. They cannot
disagree because rbo.owl makes the kinds disjoint (RBO_0000015, RBO_0000016), which this module does not
restate; its kind tests, like those of [rbo-u1], hold at any time, so a constraint of both kinds, even at
different times, would make the two definitions conflict.

The task, permission, conflicting-agent and principal axioms follow Botha and Eloff, "Separation of duties
for access control enforcement in workflow environments", IBM Systems Journal 40(3), 2001, pp.666-682.')

 (cl:ttl "https://example.org/rbac-bfo/clif/rbo-access.cl"
  (cl:text
  (cl:outdiscourse instance-of exists-at concretizes inheres-in participates-in occurrent-part-of
   occupies-temporal-region has-first-instant temporal-part-of
   rbo-activated-in rbo-assigned-to rbo-has-operation rbo-has-access-object rbo-has-requester
   rbo-requests-operation rbo-requests-access-to rbo-constrains rbo-applies-within rbo-senior-to
   rbo-senior-or-same rbo-in-force rbo-has-junior rbo-has-senior rbo-authorized-for
   rbo-has-cardinality rbo-active-for rbo-covers rbo-warrants-grant rbo-request-time cco-prescribed-by
   rbo-violates-ssd rbo-violates-dsd rbo-scope-fits rbo-explicitly-active rbo-member-of rbo-has-head rbo-names-member
   rbo-has-body rbo-has-linking-base rbo-linked-role rbo-role-of-name
   member-part-of precedes cco-has-agent rbo-principal rbo-on-behalf-of rbo-designates rbo-designates-agent
   rbo-designates-group rbo-designation-applies rbo-applies-to-constraint rbo-same-static-subject
   rbo-same-dynamic-subject rbo-requires-role rbo-activated-for rbo-active-for-request
   rbo-constrains-permission rbo-constrains-task rbo-authorized-for-permission rbo-exercised rbo-decides-on
   rbo-cites rbo-authorized-for-task rbo-performed rbo-violates-permission-ssd rbo-violates-permission-dsd
   rbo-violates-task-ssd rbo-violates-task-dsd rbo-requires-human rbo-violates-human-requirement
   rbo-requires-prior rbo-violates-prior-guard rbo-requires-operation rbo-requires-task-binding
   rbo-violates-task-binding rbo-has-object-description rbo-same-content rbo-hits rbo-exercised-before
   rbo-decided-before rbo-refuses-permission-dsd rbo-meets-description)

  (cl:comment '--- Roles ---')

  (cl:comment 'An assigned role is a role that concretizes a role definition and is not an active role [rbo-r1]'
    (forall (r t)
     (iff (instance-of r rbo-assigned-role t)
      (and (instance-of r role t)
       (exists (d) (and (instance-of d rbo-role-definition t) (concretizes r d t)))
       (not (instance-of r rbo-active-role t))))))

  (cl:comment 'An active role is a role concretizing a role definition that its bearer is authorized for at that time [rbo-r2]'
    (forall (a t)
     (if (instance-of a rbo-active-role t)
      (and (instance-of a role t)
       (exists (d x)
        (and (instance-of d rbo-role-definition t) (concretizes a d t) (inheres-in a x)
         (rbo-authorized-for x d t)))))))

  (cl:comment 'An active role is activated in exactly one business process instance [rbo-r3]'
    (forall (a t)
     (if (instance-of a rbo-active-role t)
      (exists (i)
       (and (rbo-activated-in a i) (instance-of i rbo-business-process t)
        (forall (j) (if (rbo-activated-in a j) (= j i))))))))

  (cl:comment 'While an active role exists, its bearer participates in the instance it is activated in [rbo-r4]'
    (forall (a i x t)
     (if (and (rbo-activated-in a i) (inheres-in a x) (exists-at a t)
          (exists (u) (and (occupies-temporal-region i u) (temporal-part-of t u))))
      (participates-in x i t))))

  (cl:comment '--- Hierarchy (NIST Def. 2a) ---')

  (cl:comment 'd1 is senior to d2 at t when an inheritance statement in force at t links them and both are in force at t, or by transitivity [rbo-h1]'
    (forall (d1 d2 t)
     (iff (rbo-senior-to d1 d2 t)
      (or (exists (s) (and (rbo-in-force s t) (rbo-has-senior s d1) (rbo-has-junior s d2)
                       (rbo-in-force d1 t) (rbo-in-force d2 t)))
       (exists (d3) (and (rbo-senior-to d1 d3 t) (rbo-senior-to d3 d2 t)))))))

  (cl:comment 'rbo-senior-or-same is the reflexive closure of rbo-senior-to over role definitions [rbo-h2]'
    (forall (d1 d2 t)
     (iff (rbo-senior-or-same d1 d2 t)
      (or (and (= d1 d2) (instance-of d1 rbo-role-definition t)) (rbo-senior-to d1 d2 t)))))

  (cl:comment 'x is authorized for d at t when an assigned role of x at t concretizes d or a senior definition, in force at t (NIST authorized users). A retired definition authorizes no one, so by [rbo-r2] no active role outlives it, as none outlives its assigned role [rbo-h3]'
    (forall (x d t)
     (iff (rbo-authorized-for x d t)
      (exists (r e)
       (and (instance-of r rbo-assigned-role t) (inheres-in r x) (concretizes r e t) (rbo-in-force e t)
        (rbo-senior-or-same e d t))))))

  (cl:comment 'Seniority is acyclic: the check-hierarchy-cycles query looks for violations of this axiom, so it is a commitment, not a definition [rbo-h4]'
    (forall (d t) (not (rbo-senior-to d d t))))

  (cl:comment '--- Separation of duty ---')

  (cl:comment 'SSD with cardinality 2. x violates SSD constraint c at t when c is in force at t and x, or agents a static designation counts as one with x ([rbo-u3]), are authorized for two distinct definitions c constrains. For cardinality k the schema repeats with k distinct witnesses; first-order logic without arithmetic has no single axiom for every k [rbo-s1]'
    (forall (x c t)
     (if (and (instance-of c rbo-ssd-constraint t) (rbo-has-cardinality c 2))
      (iff (rbo-violates-ssd x c t)
       (exists (d1 d2 y1 y2)
        (and (rbo-in-force c t) (not (= d1 d2)) (rbo-constrains c d1) (rbo-constrains c d2)
         (rbo-authorized-for y1 d1 t) (rbo-authorized-for y2 d2 t)
         (rbo-same-static-subject x y1 c t) (rbo-same-static-subject x y2 c t)))))))

  (cl:comment 'A dynamic constraint, dynamic designation or requirement c fits instance i when it applies within no plan, or i is prescribed by a plan it applies within. Used by the DSD axioms, [rbo-u4], [rbo-g1] and [rbo-g3] [rbo-s2]'
    (forall (c i)
     (iff (rbo-scope-fits c i)
      (or (not (exists (p) (rbo-applies-within c p)))
       (exists (p) (and (rbo-applies-within c p) (cco-prescribed-by i p)))))))

  (cl:comment 'x has d explicitly active in i at t: an active role of x, activated in i and existing at t, concretizes d itself. DSD counts only these. Seniors are not counted, because activating a role does not activate its juniors (NIST p.257) [rbo-s3]'
    (forall (x d i t)
     (iff (rbo-explicitly-active x d i t)
      (exists (a)
       (and (instance-of a rbo-active-role t) (inheres-in a x) (rbo-activated-in a i) (concretizes a d t))))))

  (cl:comment 'Same-time DSD, cardinality 2: two constrained definitions active in one fitting instance at one time at which the constraint is in force, for x or for agents a dynamic designation counts as one with x there ([rbo-u4]) [rbo-s4]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbo-same-time-dsd t)) (rbo-has-cardinality c 2))
      (iff (rbo-violates-dsd x c i)
       (exists (d1 d2 t y1 y2)
        (and (rbo-in-force c t) (not (= d1 d2)) (rbo-constrains c d1) (rbo-constrains c d2) (rbo-scope-fits c i)
         (rbo-explicitly-active y1 d1 i t) (rbo-explicitly-active y2 d2 i t)
         (rbo-same-dynamic-subject x y1 c i t) (rbo-same-dynamic-subject x y2 c i t)))))))

  (cl:comment 'Whole-instance DSD, cardinality 2: the two times may differ, so a role dropped earlier in the instance still counts. The constraint, and any designation counting the two agents as one, are in force at the later time [rbo-s5]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbo-whole-instance-dsd t)) (rbo-has-cardinality c 2))
      (iff (rbo-violates-dsd x c i)
       (exists (d1 d2 t1 t2 y1 y2)
        (and (not (= d1 d2)) (rbo-constrains c d1) (rbo-constrains c d2) (rbo-scope-fits c i)
         (or (= t1 t2) (precedes t1 t2)) (rbo-in-force c t2)
         (rbo-explicitly-active y1 d1 i t1) (rbo-explicitly-active y2 d2 i t2)
         (rbo-same-dynamic-subject x y1 c i t2) (rbo-same-dynamic-subject x y2 c i t2)))))))

  (cl:comment 'Corollary of [rbo-s4] and [rbo-s5], stated for checking: on the same constraint data a same-time violation is a whole-instance violation [rbo-s6]'
    (forall (x c i d1 d2 t)
     (if (and (not (= d1 d2)) (rbo-constrains c d1) (rbo-constrains c d2) (rbo-scope-fits c i)
          (rbo-explicitly-active x d1 i t) (rbo-explicitly-active x d2 i t) (rbo-in-force c t)
          (exists (u) (instance-of c rbo-whole-instance-dsd u)) (rbo-has-cardinality c 2))
      (rbo-violates-dsd x c i))))

  (cl:comment '--- Access decisions ---')

  (cl:comment 'The time of a request is the first instant of the temporal region it occupies [rbo-a1]'
    (forall (q t)
     (iff (rbo-request-time q t)
      (exists (u) (and (occupies-temporal-region q u) (has-first-instant u t))))))

  (cl:comment 'x has an active role for d in i at t: an active role of x, activated in i and existing at t, concretizes d or a definition senior to d, in force at t. The regulations of juniors apply this way without the juniors being active (NIST Def. 2a, p.235) [rbo-a0]'
    (forall (x d i t)
     (iff (rbo-active-for x d i t)
      (exists (a e)
       (and (instance-of a rbo-active-role t) (inheres-in a x) (rbo-activated-in a i)
        (concretizes a e t) (rbo-in-force e t) (rbo-senior-or-same e d t))))))

  (cl:comment 'x has an active role for d serving request q in i at t: as [rbo-a0], and if q is part of a task instance, the active role is activated for it. The WSession grants only the permissions of the role the task requires (Botha and Eloff 2001, p.674) [rbo-a4]'
    (forall (x d q i t)
     (iff (rbo-active-for-request x d q i t)
      (exists (a e)
       (and (instance-of a rbo-active-role t) (inheres-in a x) (rbo-activated-in a i)
        (concretizes a e t) (rbo-in-force e t) (rbo-senior-or-same e d t)
        (forall (k)
         (if (and (occurrent-part-of q k) (exists (u) (instance-of k rbo-task-instance u)))
          (rbo-activated-for a k))))))))

  (cl:comment 'Regulation g covers request q: g is in force at the time of q and has the operation q requests, the requester has an active role serving q ([rbo-a4]) in the instance q is part of for the definition g is assigned to, and the object matches: g names the object q requests, or g names neither an object nor an object description and q requests none, or g has an object description that the requested object meets. Only the queries decide rbo-meets-description: its criteria are annotation values, outside this logic [rbo-a2]'
    (forall (g q)
     (iff (rbo-covers g q)
      (exists (x i d o t)
       (and (rbo-has-requester q x) (occurrent-part-of q i) (rbo-request-time q t) (rbo-in-force g t)
        (rbo-has-operation g o) (rbo-requests-operation q o)
        (rbo-assigned-to g d) (rbo-active-for-request x d q i t)
        (or (exists (b) (and (rbo-has-access-object g b) (rbo-requests-access-to q b)))
         (and (not (exists (b) (rbo-has-access-object g b))) (not (exists (e) (rbo-has-object-description g e)))
          (not (exists (b) (rbo-requests-access-to q b))))
         (exists (e b) (and (rbo-has-object-description g e) (rbo-requests-access-to q b)
          (rbo-meets-description b e q)))))))))

  (cl:comment 'Deny-overrides: a grant is warranted iff some permission covers q, no prohibition covers q, no task-binding requirement is violated by q ([rbo-g3]), and no dynamic permission constraint refuses q ([rbo-s15]). Otherwise the request is denied (no covering axiom, NIST p.233 fn. 2) [rbo-a3]'
    (forall (q)
     (iff (rbo-warrants-grant q)
      (and (exists (g) (and (exists (t) (instance-of g rbo-access-permission t)) (rbo-covers g q)))
       (not (exists (h) (and (exists (t) (instance-of h rbo-access-prohibition t)) (rbo-covers h q))))
       (not (exists (h) (rbo-violates-task-binding h q)))
       (not (exists (c) (rbo-refuses-permission-dsd c q)))))))

  (cl:comment '--- Agents counted as one (Botha and Eloff 2001, conflicting users, pp.671-676) ---')

  (cl:comment 'The principal of an act is the agent it was performed on behalf of, else its agent. Separation of duty compares principals, so automation acting for x counts as x [rbo-p1]'
    (forall (e x)
     (iff (rbo-principal e x)
      (or (rbo-on-behalf-of e x)
       (and (cco-has-agent e x) (not (exists (y) (rbo-on-behalf-of e y))))))))

  (cl:comment 'The requester of a request is an agent of it, as has requester is a sub-property of has agent in rbo.owl [rbo-p2]'
    (forall (q x) (if (rbo-has-requester q x) (cco-has-agent q x))))

  (cl:comment 'Designation g applies to constraint c when their kinds match (static with static, dynamic with dynamic) and g names c or names no constraint [rbo-u1]'
    (forall (g c)
     (iff (rbo-designation-applies g c)
      (and (or (and (exists (t) (instance-of g rbo-static-designation t)) (exists (t) (instance-of c rbo-ssd-constraint t)))
            (and (exists (t) (instance-of g rbo-dynamic-designation t)) (exists (t) (instance-of c rbo-dsd-constraint t))))
       (or (not (exists (c2) (rbo-applies-to-constraint g c2))) (rbo-applies-to-constraint g c))))))

  (cl:comment 'Designation g designates x at t when it names x, or names a group of agents x is a member part of at t [rbo-u2]'
    (forall (g x t)
     (iff (rbo-designates g x t)
      (or (rbo-designates-agent g x)
       (exists (m) (and (rbo-designates-group g m) (member-part-of x m t)))))))

  (cl:comment 'x and y are one subject for static constraint c at t when they are identical or one applicable designation in force at t designates both. Not transitive: two designations sharing an agent do not join the others [rbo-u3]'
    (forall (x y c t)
     (iff (rbo-same-static-subject x y c t)
      (or (= x y)
       (exists (g) (and (rbo-designation-applies g c) (rbo-in-force g t)
                    (rbo-designates g x t) (rbo-designates g y t)))))))

  (cl:comment 'x and y are one subject for dynamic constraint c in instance i at t: identical, or designated by one applicable designation in force at t whose plan scope fits i ([rbo-s2]) [rbo-u4]'
    (forall (x y c i t)
     (iff (rbo-same-dynamic-subject x y c i t)
      (or (= x y)
       (exists (g) (and (rbo-designation-applies g c) (rbo-scope-fits g i) (rbo-in-force g t)
                    (rbo-designates g x t) (rbo-designates g y t)))))))

  (cl:comment '--- Tasks and WSessions (Botha and Eloff 2001, pp.667-674) ---')

  (cl:comment 'A task specification requires exactly one role definition [rbo-k1]'
    (forall (s t)
     (if (instance-of s rbo-task-specification t)
      (and (exists (d) (rbo-requires-role s d))
       (forall (d1 d2) (if (and (rbo-requires-role s d1) (rbo-requires-role s d2)) (= d1 d2)))))))

  (cl:comment 'An active role activated for a task instance is activated in the business process instance the task instance is part of [rbo-k2]'
    (forall (a k i)
     (if (and (rbo-activated-for a k) (rbo-activated-in a i))
      (occurrent-part-of k i))))

  (cl:comment 'Strict least privilege: an active role activated for a task instance concretizes the role definition the task requires, not a senior one, and inheres in the task instance agent. The WSession is a mapping of one user to the most junior role required for a specific task (p.674) [rbo-k3]'
    (forall (a k s d t)
     (if (and (rbo-activated-for a k) (cco-prescribed-by k s) (rbo-requires-role s d) (exists-at a t))
      (and (concretizes a d t)
       (forall (x) (if (inheres-in a x) (cco-has-agent k x)))))))

  (cl:comment '--- Permission and task separation of duty (Tables 1 and 2, pp.673, 676) ---')

  (cl:comment 'Permissions p1 and p2 have the same content when they have the same operations, named objects and object descriptions. Separation of duty compares permissions by content, not as individuals: NIST permission-to-role assignment is many-to-many (Def. 1, p.234), so regulations with one content assigned to two role definitions are one permission [rbo-s17]'
    (forall (p1 p2)
     (iff (rbo-same-content p1 p2)
      (and (forall (o) (iff (rbo-has-operation p1 o) (rbo-has-operation p2 o)))
       (forall (b) (iff (rbo-has-access-object p1 b) (rbo-has-access-object p2 b)))
       (forall (e) (iff (rbo-has-object-description p1 e) (rbo-has-object-description p2 e)))))))

  (cl:comment 'x is authorized for permission p at t when authorized for a role definition that a permission in force at t, with the content of p, is assigned to [rbo-s7]'
    (forall (x p t)
     (iff (rbo-authorized-for-permission x p t)
      (exists (g d)
       (and (instance-of g rbo-access-permission t) (rbo-in-force g t) (rbo-same-content g p)
        (rbo-assigned-to g d) (rbo-authorized-for x d t))))))

  (cl:comment 'Static permission SoD, cardinality 2: the constraint is in force at t and two constrained permissions of different content are authorized for one subject [rbo-s8]'
    (forall (x c t)
     (if (and (instance-of c rbo-ssd-constraint t) (rbo-has-cardinality c 2))
      (iff (rbo-violates-permission-ssd x c t)
       (exists (p1 p2 y1 y2)
        (and (rbo-in-force c t) (not (rbo-same-content p1 p2))
         (rbo-constrains-permission c p1) (rbo-constrains-permission c p2)
         (rbo-authorized-for-permission y1 p1 t) (rbo-authorized-for-permission y2 p2 t)
         (rbo-same-static-subject x y1 c t) (rbo-same-static-subject x y2 c t)))))))

  (cl:comment 'x has exercised p in i when a request that is part of i, with x as principal, is decided by a grant citing a permission with the content of p. A grant stands in for the exercise, since requests and decisions are recorded and performed acts are not [rbo-s9]'
    (forall (x p i)
     (iff (rbo-exercised x p i)
      (exists (q d g)
       (and (occurrent-part-of q i) (rbo-principal q x) (rbo-decides-on d q)
        (exists (t) (instance-of d rbo-access-grant t)) (rbo-cites d g) (rbo-same-content g p))))))

  (cl:comment 'Dynamic permission SoD, cardinality 2, whole instance: constrained permissions of two different contents exercised in one fitting instance by one subject, the constraint in force at t [rbo-s10]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbo-dsd-constraint t)) (rbo-has-cardinality c 2))
      (iff (rbo-violates-permission-dsd x c i)
       (exists (p1 p2 y1 y2 t)
        (and (rbo-in-force c t) (not (rbo-same-content p1 p2))
         (rbo-constrains-permission c p1) (rbo-constrains-permission c p2) (rbo-scope-fits c i)
         (rbo-exercised y1 p1 i) (rbo-exercised y2 p2 i)
         (rbo-same-dynamic-subject x y1 c i t) (rbo-same-dynamic-subject x y2 c i t)))))))

  (cl:comment 'Member p hits request q when a permission covering q has the content of p [rbo-s18]'
    (forall (p q)
     (iff (rbo-hits p q)
      (exists (g t) (and (instance-of g rbo-access-permission t) (rbo-covers g q) (rbo-same-content g p))))))

  (cl:comment 'y exercised p in i before q: a request that is part of i, with y as principal and decided before q (rbo-decided-before), is decided by a grant citing a permission with the content of p [rbo-s16]'
    (forall (y p q i)
     (iff (rbo-exercised-before y p q i)
      (exists (q2 d g)
       (and (occurrent-part-of q2 i) (rbo-principal q2 y) (rbo-decided-before q2 q) (rbo-decides-on d q2)
        (exists (t) (instance-of d rbo-access-grant t)) (rbo-cites d g) (rbo-same-content g p))))))

  (cl:comment 'Refusal at access time, cardinality 2 (derive-permission-dsd-conflicts.rq): dynamic constraint c, in force at the time of request q and fitting the business process instance q is part of, refuses q when q hits a member p1 ([rbo-s18]) and a member p2 of another content is hit by q too, or was exercised in the instance before q by an agent one subject with the principal of q ([rbo-s16], [rbo-u4]). Only a dynamic constraint refuses [rbo-s15]'
    (forall (c q)
     (and (if (rbo-refuses-permission-dsd c q) (exists (t) (instance-of c rbo-dsd-constraint t)))
      (if (and (exists (t) (instance-of c rbo-dsd-constraint t)) (rbo-has-cardinality c 2))
       (iff (rbo-refuses-permission-dsd c q)
        (exists (x i t p1 p2)
         (and (rbo-principal q x) (occurrent-part-of q i) (exists (u) (instance-of i rbo-business-process u))
          (rbo-request-time q t) (rbo-in-force c t) (rbo-scope-fits c i)
          (rbo-constrains-permission c p1) (rbo-constrains-permission c p2) (not (rbo-same-content p1 p2))
          (rbo-hits p1 q)
          (or (rbo-hits p2 q)
           (exists (y) (and (rbo-exercised-before y p2 q i) (rbo-same-dynamic-subject x y c i t)))))))))))

  (cl:comment 'x can do task specification s at t when authorized for the role definition s requires [rbo-s11]'
    (forall (x s t)
     (iff (rbo-authorized-for-task x s t)
      (exists (d) (and (rbo-requires-role s d) (rbo-authorized-for x d t))))))

  (cl:comment 'Static task SoD, cardinality 2: the constraint is in force at t and two distinct constrained task specifications are ones one subject can do (Table 1 row 4) [rbo-s12]'
    (forall (x c t)
     (if (and (instance-of c rbo-ssd-constraint t) (rbo-has-cardinality c 2))
      (iff (rbo-violates-task-ssd x c t)
       (exists (s1 s2 y1 y2)
        (and (rbo-in-force c t) (not (= s1 s2)) (rbo-constrains-task c s1) (rbo-constrains-task c s2)
         (rbo-authorized-for-task y1 s1 t) (rbo-authorized-for-task y2 s2 t)
         (rbo-same-static-subject x y1 c t) (rbo-same-static-subject x y2 c t)))))))

  (cl:comment 'x has performed s in i when a task instance that is part of i and prescribed by s has x as principal [rbo-s13]'
    (forall (x s i)
     (iff (rbo-performed x s i)
      (exists (k) (and (occurrent-part-of k i) (cco-prescribed-by k s) (rbo-principal k x))))))

  (cl:comment 'Dynamic task SoD, cardinality 2, whole instance: instances of two distinct constrained task specifications with one subject as principal in one fitting instance, the constraint in force at t (Table 2 row 4) [rbo-s14]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbo-dsd-constraint t)) (rbo-has-cardinality c 2))
      (iff (rbo-violates-task-dsd x c i)
       (exists (s1 s2 y1 y2 t)
        (and (rbo-in-force c t) (not (= s1 s2)) (rbo-constrains-task c s1) (rbo-constrains-task c s2)
         (rbo-scope-fits c i) (rbo-performed y1 s1 i) (rbo-performed y2 s2 i)
         (rbo-same-dynamic-subject x y1 c i t) (rbo-same-dynamic-subject x y2 c i t)))))))

  (cl:comment '--- Human in the loop and task-bound operations (not in Botha and Eloff) ---')

  (cl:comment 'Requirement h is violated by task instance k when h is in force when k begins, k is prescribed by the task specification h names, lies in an instance h fits, and has an agent that is never a person [rbo-g1]'
    (forall (h k)
     (iff (rbo-violates-human-requirement h k)
      (exists (s i x u t0)
       (and (rbo-requires-human h s) (cco-prescribed-by k s) (occurrent-part-of k i) (rbo-scope-fits h i)
        (occupies-temporal-region k u) (has-first-instant u t0) (rbo-in-force h t0)
        (cco-has-agent k x) (not (exists (t) (instance-of x cco-person t))))))))

  (cl:comment 'Completion guard: task instance k, prescribed by s2 which requires prior s1, violates the guard when its business process instance holds no instance of s1 that precedes k and has a person as agent. The guard has no plan scope: it belongs to s2, unlike [rbo-g1] and [rbo-g3] (rbo.owl, RBO_0000144) [rbo-g2]'
    (forall (k)
     (iff (rbo-violates-prior-guard k)
      (exists (s1 s2 i)
       (and (exists (u) (instance-of k rbo-task-instance u)) (cco-prescribed-by k s2) (rbo-requires-prior s2 s1)
        (occurrent-part-of k i)
        (not (exists (k1 x)
              (and (cco-prescribed-by k1 s1) (occurrent-part-of k1 i) (precedes k1 k) (cco-has-agent k1 x)
               (exists (t) (instance-of x cco-person t))))))))))

  (cl:comment 'Requirement h is violated by access request q when h is in force at the time of q, q requests an operation h names, h applies within no plan or q is part of an instance h fits, and q is part of no task instance whose specification requires that operation [rbo-g3]'
    (forall (h q)
     (iff (rbo-violates-task-binding h q)
      (exists (o t0)
       (and (rbo-requires-task-binding h o) (rbo-requests-operation q o) (rbo-request-time q t0) (rbo-in-force h t0)
        (or (not (exists (p) (rbo-applies-within h p)))
         (exists (i) (and (occurrent-part-of q i) (rbo-scope-fits h i))))
        (not (exists (k s u)
              (and (occurrent-part-of q k) (instance-of k rbo-task-instance u) (cco-prescribed-by k s)
               (rbo-requires-operation s o)))))))))

  (cl:comment '--- RT role statements (ROWLBAC section 4.2) ---')

  (cl:comment 'Type 1, A.r <- D: D is a member of A.r while the statement is in force [rbo-t1]'
    (forall (s a d t)
     (if (and (rbo-in-force s t) (rbo-has-head s a) (rbo-names-member s d))
      (rbo-member-of d a t))))

  (cl:comment 'Type 2, A.r <- B.r1: every member of B.r1 is a member of A.r. The head is the junior and the body the senior, as in rbo.owl, where has junior role definition is a sub-property of has head role [rbo-t2]'
    (forall (s a b x t)
     (if (and (rbo-in-force s t) (rbo-has-head s a) (rbo-has-senior s b) (rbo-member-of x b t))
      (rbo-member-of x a t))))

  (cl:comment 'Type 3, A.r <- B.r1.r2: a member of y.r2, for any y in B.r1, is a member of A.r. rbo-role-of-name y n e says e is the RT role of issuer y named n [rbo-t3]'
    (forall (s a b n x y e t)
     (if (and (rbo-in-force s t) (rbo-has-head s a) (rbo-has-linking-base s b)
          (rbo-linked-role s n) (rbo-member-of y b t) (rbo-role-of-name y n e) (rbo-member-of x e t))
      (rbo-member-of x a t))))

  (cl:comment 'Type 4, A.r <- B1.r1 and B2.r2: members of both bodies are members of A.r [rbo-t4]'
    (forall (s a b1 b2 x t)
     (if (and (rbo-in-force s t) (rbo-has-head s a) (rbo-has-body s b1) (rbo-has-body s b2)
          (not (= b1 b2)) (rbo-member-of x b1 t) (rbo-member-of x b2 t))
      (rbo-member-of x a t))))

  (cl:comment 'Completion for one RT role (Clark completion, ROWLBAC section 4.2): only the rules above put x in A.r. Asserted per role, it is what the paper calls growth-restricted, and it makes membership the least fixpoint derive-rt-membership.rq computes. Not asserted for every role, so it is a schema, shown here for a role constant rt-role [rbo-t5]'
    (forall (x t)
     (if (rbo-member-of x rt-role t)
      (exists (s)
       (and (rbo-in-force s t) (rbo-has-head s rt-role)
        (or (rbo-names-member s x)
         (exists (b) (and (rbo-has-senior s b) (rbo-member-of x b t)))
         (exists (b n y e) (and (rbo-has-linking-base s b) (rbo-linked-role s n) (rbo-member-of y b t)
                            (rbo-role-of-name y n e) (rbo-member-of x e t)))
         (exists (b1 b2) (and (rbo-has-body s b1) (rbo-has-body s b2) (not (= b1 b2))
                          (rbo-member-of x b1 t) (rbo-member-of x b2 t)))))))))
))
