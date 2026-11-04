(cl:comment '
RBACO-BFO access module, draft of 2026-11-03
Companion to rbaco-bfo.owl. It states, in first-order logic, the parts of the RBACO account that OWL 2 DL cannot:
time-indexed seniority, the counting in separation-of-duty constraints over roles, permissions and tasks,
agents counted as one, task-bound activation and operations, deny-overrides, and RT role linking.
Written in the style of the BFO 2020 CLIF modules (ternary instance-of, time-indexed continuant relations,
one axiom per cl:comment with an axiom ID). License: CC BY 4.0.

Name mapping. BFO 2020 names are used as in the BFO CLIF. Other names map to OWL terms as follows:
  rbaco-role-definition            RBACO_0000001   rbaco-assigned-role         RBACO_0000002
  rbaco-active-role                RBACO_0000003   rbaco-business-process      RBACO_0000004
  rbaco-access-permission          RBACO_0000007   rbaco-access-prohibition    RBACO_0000008
  rbaco-ssd-constraint             RBACO_0000013   rbaco-same-time-dsd         RBACO_0000015
  rbaco-whole-instance-dsd         RBACO_0000016   rbaco-role-assignment       RBACO_0000028
  rbaco-activated-in               RBACO_0000106   rbaco-assigned-to           RBACO_0000105
  rbaco-has-operation              RBACO_0000101   rbaco-has-access-object     RBACO_0000102
  rbaco-has-object-description     RBACO_0000103   rbaco-has-requester         RBACO_0000107
  rbaco-requests-operation         RBACO_0000108   rbaco-requests-access-to    RBACO_0000109
  rbaco-constrains                 RBACO_0000114   rbaco-applies-within        RBACO_0000115
  rbaco-senior-to                  RBACO_0000120 (here time-indexed)
  rbaco-member-of                  RBACO_0000131   rbaco-has-cardinality       RBACO_0000201
  rbaco-dsd-constraint             RBACO_0000014   rbaco-access-grant          RBACO_0000022
  rbaco-task-specification         RBACO_0000040   rbaco-task-instance         RBACO_0000041
  rbaco-static-designation         RBACO_0000046   rbaco-dynamic-designation   RBACO_0000047
  rbaco-human-requirement          RBACO_0000049   rbaco-decides-on            RBACO_0000112
  rbaco-cites                      RBACO_0000113   rbaco-requires-role         RBACO_0000132
  rbaco-constrains-permission      RBACO_0000134   rbaco-constrains-task       RBACO_0000135
  rbaco-activated-for              RBACO_0000136   rbaco-designates-agent      RBACO_0000138
  rbaco-designates-group           RBACO_0000139   rbaco-applies-to-constraint RBACO_0000140
  rbaco-on-behalf-of               RBACO_0000143   rbaco-requires-prior        RBACO_0000144
  rbaco-requires-human             RBACO_0000145   rbaco-requires-operation    RBACO_0000133
  rbaco-task-binding-requirement   RBACO_0000050   rbaco-requires-task-binding RBACO_0000148
  cco-prescribed-by              cco:ont00001920   cco-has-output        cco:ont00001986
  cco-has-agent                  cco:ont00001833   cco-person            cco:ont00001262
  rbaco-has-head                   RBACO_0000116   rbaco-has-body              RBACO_0000117
  rbaco-has-senior                 RBACO_0000118   rbaco-has-junior            RBACO_0000119
  rbaco-names-member               RBACO_0000122   rbaco-has-linking-base      RBACO_0000123
  rbaco-linked-role                RBACO_0000203
  rbaco-role-of-name               no single OWL counterpart: rbaco-role-of-name y n e holds when e has role
                                 issuer (RBACO_0000121) y and has RT role name (RBACO_0000202) n
  rbaco-in-force                   no OWL counterpart: an information content entity is in force at t when its
                                 issuing act (RBACO_0000031) starts at or before t and no retiring act
                                 (RBACO_0000032) with it as input does (the scope note of RBACO_0000032);
                                 derive-in-force.rq computes it
  rbaco-decided-before             no OWL counterpart: request q1 is decided before q2 when q1 is earlier, or
                                 at the same time with a smaller IRI; the queries compute it
  rbaco-meets-description          no OWL counterpart: rbaco-meets-description b e q holds when, at the time of
                                 q, object b is an instance of every object type criterion (RBACO_0000302) of
                                 description e, is located in an instance of every object location type
                                 criterion (RBACO_0000303), and, if e is a requester office condition
                                 (RBACO_0000011), is located in an office (RBACO_0001101, rbaco-bfo-domain.ttl) of the
                                 requester of q; derive-regulation-coverage.rq tests it
  rbaco-senior-or-same, rbaco-authorized-for, rbaco-scope-fits, rbaco-explicitly-active, rbaco-request-time,
  rbaco-active-for, rbaco-active-for-request, rbaco-covers, rbaco-warrants-grant, rbaco-principal, rbaco-designates,
  rbaco-designation-applies, rbaco-same-static-subject, rbaco-same-dynamic-subject, rbaco-authorized-for-permission,
  rbaco-exercised, rbaco-authorized-for-task, rbaco-performed, rbaco-same-content, rbaco-hits, rbaco-exercised-before,
  rbaco-refuses-permission-dsd, rbaco-violates-*
                                 defined here; the SPARQL queries compute them

None of these axioms forbids a violation. Constraints and regulations are prescriptive information content
entities, and a conflict report describes an act that went against one, so the violation predicates are
defined (iff), never denied. The SPARQL queries are the operational reading of the definitions. The
commitments are structural: what an active role is ([rbaco-r1]-[rbaco-r4], [rbaco-k2], [rbaco-k3]), that seniority is
acyclic ([rbaco-h4]), and that a task specification requires exactly one role definition ([rbaco-k1]).

Two limits of the first-order reading, neither of which the queries share. [rbaco-h1] is an equivalence, not an
inductive definition. With [rbaco-h4], every finite model gives rbaco-senior-to exactly the transitive closure of
the links [rbaco-h1] admits, but an infinite one can add more (a densely ordered chain of further definitions
satisfies it), so no axiom here entails that one definition is not senior to another; the queries compute the
closure. [rbaco-s4] and [rbaco-s5] both define rbaco-violates-dsd, each for its own kind of constraint. They cannot
disagree because rbaco-bfo.owl makes the kinds disjoint (RBACO_0000015, RBACO_0000016), which this module does not
restate; its kind tests, like those of [rbaco-u1], hold at any time, so a constraint of both kinds, even at
different times, would make the two definitions conflict.

The task, permission, conflicting-agent and principal axioms follow Botha and Eloff, "Separation of duties
for access control enforcement in workflow environments", IBM Systems Journal 40(3), 2001, pp.666-682.')

 (cl:ttl "https://w3id.org/rbaco/bfo/clif/rbaco-bfo-access.cl"
  (cl:text
  (cl:outdiscourse instance-of exists-at concretizes inheres-in participates-in occurrent-part-of
   occupies-temporal-region has-first-instant temporal-part-of
   rbaco-activated-in rbaco-assigned-to rbaco-has-operation rbaco-has-access-object rbaco-has-requester
   rbaco-requests-operation rbaco-requests-access-to rbaco-constrains rbaco-applies-within rbaco-senior-to
   rbaco-senior-or-same rbaco-in-force rbaco-has-junior rbaco-has-senior rbaco-authorized-for
   rbaco-has-cardinality rbaco-active-for rbaco-covers rbaco-warrants-grant rbaco-request-time cco-prescribed-by
   rbaco-violates-ssd rbaco-violates-dsd rbaco-scope-fits rbaco-explicitly-active rbaco-member-of rbaco-has-head rbaco-names-member
   rbaco-has-body rbaco-has-linking-base rbaco-linked-role rbaco-role-of-name
   member-part-of precedes cco-has-agent rbaco-principal rbaco-on-behalf-of rbaco-designates rbaco-designates-agent
   rbaco-designates-group rbaco-designation-applies rbaco-applies-to-constraint rbaco-same-static-subject
   rbaco-same-dynamic-subject rbaco-requires-role rbaco-activated-for rbaco-active-for-request
   rbaco-constrains-permission rbaco-constrains-task rbaco-authorized-for-permission rbaco-exercised rbaco-decides-on
   rbaco-cites rbaco-authorized-for-task rbaco-performed rbaco-violates-permission-ssd rbaco-violates-permission-dsd
   rbaco-violates-task-ssd rbaco-violates-task-dsd rbaco-requires-human rbaco-violates-human-requirement
   rbaco-requires-prior rbaco-violates-prior-guard rbaco-requires-operation rbaco-requires-task-binding
   rbaco-violates-task-binding rbaco-has-object-description rbaco-same-content rbaco-hits rbaco-exercised-before
   rbaco-decided-before rbaco-refuses-permission-dsd rbaco-meets-description)

  (cl:comment '--- Roles ---')

  (cl:comment 'An assigned role is a role that concretizes a role definition and is not an active role [rbaco-r1]'
    (forall (r t)
     (iff (instance-of r rbaco-assigned-role t)
      (and (instance-of r role t)
       (exists (d) (and (instance-of d rbaco-role-definition t) (concretizes r d t)))
       (not (instance-of r rbaco-active-role t))))))

  (cl:comment 'An active role is a role concretizing a role definition that its bearer is authorized for at that time [rbaco-r2]'
    (forall (a t)
     (if (instance-of a rbaco-active-role t)
      (and (instance-of a role t)
       (exists (d x)
        (and (instance-of d rbaco-role-definition t) (concretizes a d t) (inheres-in a x)
         (rbaco-authorized-for x d t)))))))

  (cl:comment 'An active role is activated in exactly one business process instance [rbaco-r3]'
    (forall (a t)
     (if (instance-of a rbaco-active-role t)
      (exists (i)
       (and (rbaco-activated-in a i) (instance-of i rbaco-business-process t)
        (forall (j) (if (rbaco-activated-in a j) (= j i))))))))

  (cl:comment 'While an active role exists, its bearer participates in the instance it is activated in [rbaco-r4]'
    (forall (a i x t)
     (if (and (rbaco-activated-in a i) (inheres-in a x) (exists-at a t)
          (exists (u) (and (occupies-temporal-region i u) (temporal-part-of t u))))
      (participates-in x i t))))

  (cl:comment '--- Hierarchy (NIST Def. 2a) ---')

  (cl:comment 'd1 is senior to d2 at t when an inheritance statement in force at t links them and both are in force at t, or by transitivity [rbaco-h1]'
    (forall (d1 d2 t)
     (iff (rbaco-senior-to d1 d2 t)
      (or (exists (s) (and (rbaco-in-force s t) (rbaco-has-senior s d1) (rbaco-has-junior s d2)
                       (rbaco-in-force d1 t) (rbaco-in-force d2 t)))
       (exists (d3) (and (rbaco-senior-to d1 d3 t) (rbaco-senior-to d3 d2 t)))))))

  (cl:comment 'rbaco-senior-or-same is the reflexive closure of rbaco-senior-to over role definitions [rbaco-h2]'
    (forall (d1 d2 t)
     (iff (rbaco-senior-or-same d1 d2 t)
      (or (and (= d1 d2) (instance-of d1 rbaco-role-definition t)) (rbaco-senior-to d1 d2 t)))))

  (cl:comment 'x is authorized for d at t when an assigned role of x at t concretizes d or a senior definition, in force at t (NIST authorized users). A retired definition authorizes no one, so by [rbaco-r2] no active role outlives it, as none outlives its assigned role [rbaco-h3]'
    (forall (x d t)
     (iff (rbaco-authorized-for x d t)
      (exists (r e)
       (and (instance-of r rbaco-assigned-role t) (inheres-in r x) (concretizes r e t) (rbaco-in-force e t)
        (rbaco-senior-or-same e d t))))))

  (cl:comment 'Seniority is acyclic: the check-hierarchy-cycles query looks for violations of this axiom, so it is a commitment, not a definition [rbaco-h4]'
    (forall (d t) (not (rbaco-senior-to d d t))))

  (cl:comment '--- Separation of duty ---')

  (cl:comment 'SSD with cardinality 2. x violates SSD constraint c at t when c is in force at t and x, or agents a static designation counts as one with x ([rbaco-u3]), are authorized for two distinct definitions c constrains. For cardinality k the schema repeats with k distinct witnesses; first-order logic without arithmetic has no single axiom for every k [rbaco-s1]'
    (forall (x c t)
     (if (and (instance-of c rbaco-ssd-constraint t) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-ssd x c t)
       (exists (d1 d2 y1 y2)
        (and (rbaco-in-force c t) (not (= d1 d2)) (rbaco-constrains c d1) (rbaco-constrains c d2)
         (rbaco-authorized-for y1 d1 t) (rbaco-authorized-for y2 d2 t)
         (rbaco-same-static-subject x y1 c t) (rbaco-same-static-subject x y2 c t)))))))

  (cl:comment 'A dynamic constraint, dynamic designation or requirement c fits instance i when it applies within no plan, or i is prescribed by a plan it applies within. Used by the DSD axioms, [rbaco-u4], [rbaco-g1] and [rbaco-g3] [rbaco-s2]'
    (forall (c i)
     (iff (rbaco-scope-fits c i)
      (or (not (exists (p) (rbaco-applies-within c p)))
       (exists (p) (and (rbaco-applies-within c p) (cco-prescribed-by i p)))))))

  (cl:comment 'x has d explicitly active in i at t: an active role of x, activated in i and existing at t, concretizes d itself. DSD counts only these. Seniors are not counted, because activating a role does not activate its juniors (NIST p.257) [rbaco-s3]'
    (forall (x d i t)
     (iff (rbaco-explicitly-active x d i t)
      (exists (a)
       (and (instance-of a rbaco-active-role t) (inheres-in a x) (rbaco-activated-in a i) (concretizes a d t))))))

  (cl:comment 'Same-time DSD, cardinality 2: two constrained definitions active in one fitting instance at one time at which the constraint is in force, for x or for agents a dynamic designation counts as one with x there ([rbaco-u4]) [rbaco-s4]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbaco-same-time-dsd t)) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-dsd x c i)
       (exists (d1 d2 t y1 y2)
        (and (rbaco-in-force c t) (not (= d1 d2)) (rbaco-constrains c d1) (rbaco-constrains c d2) (rbaco-scope-fits c i)
         (rbaco-explicitly-active y1 d1 i t) (rbaco-explicitly-active y2 d2 i t)
         (rbaco-same-dynamic-subject x y1 c i t) (rbaco-same-dynamic-subject x y2 c i t)))))))

  (cl:comment 'Whole-instance DSD, cardinality 2: the two times may differ, so a role dropped earlier in the instance still counts. The constraint, and any designation counting the two agents as one, are in force at the later time [rbaco-s5]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbaco-whole-instance-dsd t)) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-dsd x c i)
       (exists (d1 d2 t1 t2 y1 y2)
        (and (not (= d1 d2)) (rbaco-constrains c d1) (rbaco-constrains c d2) (rbaco-scope-fits c i)
         (or (= t1 t2) (precedes t1 t2)) (rbaco-in-force c t2)
         (rbaco-explicitly-active y1 d1 i t1) (rbaco-explicitly-active y2 d2 i t2)
         (rbaco-same-dynamic-subject x y1 c i t2) (rbaco-same-dynamic-subject x y2 c i t2)))))))

  (cl:comment 'Corollary of [rbaco-s4] and [rbaco-s5], stated for checking: on the same constraint data a same-time violation is a whole-instance violation [rbaco-s6]'
    (forall (x c i d1 d2 t)
     (if (and (not (= d1 d2)) (rbaco-constrains c d1) (rbaco-constrains c d2) (rbaco-scope-fits c i)
          (rbaco-explicitly-active x d1 i t) (rbaco-explicitly-active x d2 i t) (rbaco-in-force c t)
          (exists (u) (instance-of c rbaco-whole-instance-dsd u)) (rbaco-has-cardinality c 2))
      (rbaco-violates-dsd x c i))))

  (cl:comment '--- Access decisions ---')

  (cl:comment 'The time of a request is the first instant of the temporal region it occupies [rbaco-a1]'
    (forall (q t)
     (iff (rbaco-request-time q t)
      (exists (u) (and (occupies-temporal-region q u) (has-first-instant u t))))))

  (cl:comment 'x has an active role for d in i at t: an active role of x, activated in i and existing at t, concretizes d or a definition senior to d, in force at t. The regulations of juniors apply this way without the juniors being active (NIST Def. 2a, p.235) [rbaco-a0]'
    (forall (x d i t)
     (iff (rbaco-active-for x d i t)
      (exists (a e)
       (and (instance-of a rbaco-active-role t) (inheres-in a x) (rbaco-activated-in a i)
        (concretizes a e t) (rbaco-in-force e t) (rbaco-senior-or-same e d t))))))

  (cl:comment 'x has an active role for d serving request q in i at t: as [rbaco-a0], and if q is part of a task instance, the active role is activated for it. The WSession grants only the permissions of the role the task requires (Botha and Eloff 2001, p.674) [rbaco-a4]'
    (forall (x d q i t)
     (iff (rbaco-active-for-request x d q i t)
      (exists (a e)
       (and (instance-of a rbaco-active-role t) (inheres-in a x) (rbaco-activated-in a i)
        (concretizes a e t) (rbaco-in-force e t) (rbaco-senior-or-same e d t)
        (forall (k)
         (if (and (occurrent-part-of q k) (exists (u) (instance-of k rbaco-task-instance u)))
          (rbaco-activated-for a k))))))))

  (cl:comment 'Regulation g covers request q: g is in force at the time of q and has the operation q requests, the requester has an active role serving q ([rbaco-a4]) in the instance q is part of for the definition g is assigned to, and the object matches: g names the object q requests, or g names neither an object nor an object description and q requests none, or g has an object description that the requested object meets. Only the queries decide rbaco-meets-description: its criteria are annotation values, outside this logic [rbaco-a2]'
    (forall (g q)
     (iff (rbaco-covers g q)
      (exists (x i d o t)
       (and (rbaco-has-requester q x) (occurrent-part-of q i) (rbaco-request-time q t) (rbaco-in-force g t)
        (rbaco-has-operation g o) (rbaco-requests-operation q o)
        (rbaco-assigned-to g d) (rbaco-active-for-request x d q i t)
        (or (exists (b) (and (rbaco-has-access-object g b) (rbaco-requests-access-to q b)))
         (and (not (exists (b) (rbaco-has-access-object g b))) (not (exists (e) (rbaco-has-object-description g e)))
          (not (exists (b) (rbaco-requests-access-to q b))))
         (exists (e b) (and (rbaco-has-object-description g e) (rbaco-requests-access-to q b)
          (rbaco-meets-description b e q)))))))))

  (cl:comment 'Deny-overrides: a grant is warranted iff some permission covers q, no prohibition covers q, no task-binding requirement is violated by q ([rbaco-g3]), and no dynamic permission constraint refuses q ([rbaco-s15]). Otherwise the request is denied (no covering axiom, NIST p.233 fn. 2) [rbaco-a3]'
    (forall (q)
     (iff (rbaco-warrants-grant q)
      (and (exists (g) (and (exists (t) (instance-of g rbaco-access-permission t)) (rbaco-covers g q)))
       (not (exists (h) (and (exists (t) (instance-of h rbaco-access-prohibition t)) (rbaco-covers h q))))
       (not (exists (h) (rbaco-violates-task-binding h q)))
       (not (exists (c) (rbaco-refuses-permission-dsd c q)))))))

  (cl:comment '--- Agents counted as one (Botha and Eloff 2001, conflicting users, pp.671-676) ---')

  (cl:comment 'The principal of an act is the agent it was performed on behalf of, else its agent. Separation of duty compares principals, so automation acting for x counts as x [rbaco-p1]'
    (forall (e x)
     (iff (rbaco-principal e x)
      (or (rbaco-on-behalf-of e x)
       (and (cco-has-agent e x) (not (exists (y) (rbaco-on-behalf-of e y))))))))

  (cl:comment 'The requester of a request is an agent of it, as has requester is a sub-property of has agent in rbaco-bfo.owl [rbaco-p2]'
    (forall (q x) (if (rbaco-has-requester q x) (cco-has-agent q x))))

  (cl:comment 'Designation g applies to constraint c when their kinds match (static with static, dynamic with dynamic) and g names c or names no constraint [rbaco-u1]'
    (forall (g c)
     (iff (rbaco-designation-applies g c)
      (and (or (and (exists (t) (instance-of g rbaco-static-designation t)) (exists (t) (instance-of c rbaco-ssd-constraint t)))
            (and (exists (t) (instance-of g rbaco-dynamic-designation t)) (exists (t) (instance-of c rbaco-dsd-constraint t))))
       (or (not (exists (c2) (rbaco-applies-to-constraint g c2))) (rbaco-applies-to-constraint g c))))))

  (cl:comment 'Designation g designates x at t when it names x, or names a group of agents x is a member part of at t [rbaco-u2]'
    (forall (g x t)
     (iff (rbaco-designates g x t)
      (or (rbaco-designates-agent g x)
       (exists (m) (and (rbaco-designates-group g m) (member-part-of x m t)))))))

  (cl:comment 'x and y are one subject for static constraint c at t when they are identical or one applicable designation in force at t designates both. Not transitive: two designations sharing an agent do not join the others [rbaco-u3]'
    (forall (x y c t)
     (iff (rbaco-same-static-subject x y c t)
      (or (= x y)
       (exists (g) (and (rbaco-designation-applies g c) (rbaco-in-force g t)
                    (rbaco-designates g x t) (rbaco-designates g y t)))))))

  (cl:comment 'x and y are one subject for dynamic constraint c in instance i at t: identical, or designated by one applicable designation in force at t whose plan scope fits i ([rbaco-s2]) [rbaco-u4]'
    (forall (x y c i t)
     (iff (rbaco-same-dynamic-subject x y c i t)
      (or (= x y)
       (exists (g) (and (rbaco-designation-applies g c) (rbaco-scope-fits g i) (rbaco-in-force g t)
                    (rbaco-designates g x t) (rbaco-designates g y t)))))))

  (cl:comment '--- Tasks and WSessions (Botha and Eloff 2001, pp.667-674) ---')

  (cl:comment 'A task specification requires exactly one role definition [rbaco-k1]'
    (forall (s t)
     (if (instance-of s rbaco-task-specification t)
      (and (exists (d) (rbaco-requires-role s d))
       (forall (d1 d2) (if (and (rbaco-requires-role s d1) (rbaco-requires-role s d2)) (= d1 d2)))))))

  (cl:comment 'An active role activated for a task instance is activated in the business process instance the task instance is part of [rbaco-k2]'
    (forall (a k i)
     (if (and (rbaco-activated-for a k) (rbaco-activated-in a i))
      (occurrent-part-of k i))))

  (cl:comment 'Strict least privilege: an active role activated for a task instance concretizes the role definition the task requires, not a senior one, and inheres in the task instance agent. The WSession is a mapping of one user to the most junior role required for a specific task (p.674) [rbaco-k3]'
    (forall (a k s d t)
     (if (and (rbaco-activated-for a k) (cco-prescribed-by k s) (rbaco-requires-role s d) (exists-at a t))
      (and (concretizes a d t)
       (forall (x) (if (inheres-in a x) (cco-has-agent k x)))))))

  (cl:comment '--- Permission and task separation of duty (Tables 1 and 2, pp.673, 676) ---')

  (cl:comment 'Permissions p1 and p2 have the same content when they have the same operations, named objects and object descriptions. Separation of duty compares permissions by content, not as individuals: NIST permission-to-role assignment is many-to-many (Def. 1, p.234), so regulations with one content assigned to two role definitions are one permission [rbaco-s17]'
    (forall (p1 p2)
     (iff (rbaco-same-content p1 p2)
      (and (forall (o) (iff (rbaco-has-operation p1 o) (rbaco-has-operation p2 o)))
       (forall (b) (iff (rbaco-has-access-object p1 b) (rbaco-has-access-object p2 b)))
       (forall (e) (iff (rbaco-has-object-description p1 e) (rbaco-has-object-description p2 e)))))))

  (cl:comment 'x is authorized for permission p at t when authorized for a role definition that a permission in force at t, with the content of p, is assigned to [rbaco-s7]'
    (forall (x p t)
     (iff (rbaco-authorized-for-permission x p t)
      (exists (g d)
       (and (instance-of g rbaco-access-permission t) (rbaco-in-force g t) (rbaco-same-content g p)
        (rbaco-assigned-to g d) (rbaco-authorized-for x d t))))))

  (cl:comment 'Static permission SoD, cardinality 2: the constraint is in force at t and two constrained permissions of different content are authorized for one subject [rbaco-s8]'
    (forall (x c t)
     (if (and (instance-of c rbaco-ssd-constraint t) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-permission-ssd x c t)
       (exists (p1 p2 y1 y2)
        (and (rbaco-in-force c t) (not (rbaco-same-content p1 p2))
         (rbaco-constrains-permission c p1) (rbaco-constrains-permission c p2)
         (rbaco-authorized-for-permission y1 p1 t) (rbaco-authorized-for-permission y2 p2 t)
         (rbaco-same-static-subject x y1 c t) (rbaco-same-static-subject x y2 c t)))))))

  (cl:comment 'x has exercised p in i when a request that is part of i, with x as principal, is decided by a grant citing a permission with the content of p. A grant stands in for the exercise, since requests and decisions are recorded and performed acts are not [rbaco-s9]'
    (forall (x p i)
     (iff (rbaco-exercised x p i)
      (exists (q d g)
       (and (occurrent-part-of q i) (rbaco-principal q x) (rbaco-decides-on d q)
        (exists (t) (instance-of d rbaco-access-grant t)) (rbaco-cites d g) (rbaco-same-content g p))))))

  (cl:comment 'Dynamic permission SoD, cardinality 2, whole instance: constrained permissions of two different contents exercised in one fitting instance by one subject, the constraint in force at t [rbaco-s10]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbaco-dsd-constraint t)) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-permission-dsd x c i)
       (exists (p1 p2 y1 y2 t)
        (and (rbaco-in-force c t) (not (rbaco-same-content p1 p2))
         (rbaco-constrains-permission c p1) (rbaco-constrains-permission c p2) (rbaco-scope-fits c i)
         (rbaco-exercised y1 p1 i) (rbaco-exercised y2 p2 i)
         (rbaco-same-dynamic-subject x y1 c i t) (rbaco-same-dynamic-subject x y2 c i t)))))))

  (cl:comment 'Member p hits request q when a permission covering q has the content of p [rbaco-s18]'
    (forall (p q)
     (iff (rbaco-hits p q)
      (exists (g t) (and (instance-of g rbaco-access-permission t) (rbaco-covers g q) (rbaco-same-content g p))))))

  (cl:comment 'y exercised p in i before q: a request that is part of i, with y as principal and decided before q (rbaco-decided-before), is decided by a grant citing a permission with the content of p [rbaco-s16]'
    (forall (y p q i)
     (iff (rbaco-exercised-before y p q i)
      (exists (q2 d g)
       (and (occurrent-part-of q2 i) (rbaco-principal q2 y) (rbaco-decided-before q2 q) (rbaco-decides-on d q2)
        (exists (t) (instance-of d rbaco-access-grant t)) (rbaco-cites d g) (rbaco-same-content g p))))))

  (cl:comment 'Refusal at access time, cardinality 2 (derive-permission-dsd-conflicts.rq): dynamic constraint c, in force at the time of request q and fitting the business process instance q is part of, refuses q when q hits a member p1 ([rbaco-s18]) and a member p2 of another content is hit by q too, or was exercised in the instance before q by an agent one subject with the principal of q ([rbaco-s16], [rbaco-u4]). Only a dynamic constraint refuses [rbaco-s15]'
    (forall (c q)
     (and (if (rbaco-refuses-permission-dsd c q) (exists (t) (instance-of c rbaco-dsd-constraint t)))
      (if (and (exists (t) (instance-of c rbaco-dsd-constraint t)) (rbaco-has-cardinality c 2))
       (iff (rbaco-refuses-permission-dsd c q)
        (exists (x i t p1 p2)
         (and (rbaco-principal q x) (occurrent-part-of q i) (exists (u) (instance-of i rbaco-business-process u))
          (rbaco-request-time q t) (rbaco-in-force c t) (rbaco-scope-fits c i)
          (rbaco-constrains-permission c p1) (rbaco-constrains-permission c p2) (not (rbaco-same-content p1 p2))
          (rbaco-hits p1 q)
          (or (rbaco-hits p2 q)
           (exists (y) (and (rbaco-exercised-before y p2 q i) (rbaco-same-dynamic-subject x y c i t)))))))))))

  (cl:comment 'x can do task specification s at t when authorized for the role definition s requires [rbaco-s11]'
    (forall (x s t)
     (iff (rbaco-authorized-for-task x s t)
      (exists (d) (and (rbaco-requires-role s d) (rbaco-authorized-for x d t))))))

  (cl:comment 'Static task SoD, cardinality 2: the constraint is in force at t and two distinct constrained task specifications are ones one subject can do (Table 1 row 4) [rbaco-s12]'
    (forall (x c t)
     (if (and (instance-of c rbaco-ssd-constraint t) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-task-ssd x c t)
       (exists (s1 s2 y1 y2)
        (and (rbaco-in-force c t) (not (= s1 s2)) (rbaco-constrains-task c s1) (rbaco-constrains-task c s2)
         (rbaco-authorized-for-task y1 s1 t) (rbaco-authorized-for-task y2 s2 t)
         (rbaco-same-static-subject x y1 c t) (rbaco-same-static-subject x y2 c t)))))))

  (cl:comment 'x has performed s in i when a task instance that is part of i and prescribed by s has x as principal [rbaco-s13]'
    (forall (x s i)
     (iff (rbaco-performed x s i)
      (exists (k) (and (occurrent-part-of k i) (cco-prescribed-by k s) (rbaco-principal k x))))))

  (cl:comment 'Dynamic task SoD, cardinality 2, whole instance: instances of two distinct constrained task specifications with one subject as principal in one fitting instance, the constraint in force at t (Table 2 row 4) [rbaco-s14]'
    (forall (x c i)
     (if (and (exists (t) (instance-of c rbaco-dsd-constraint t)) (rbaco-has-cardinality c 2))
      (iff (rbaco-violates-task-dsd x c i)
       (exists (s1 s2 y1 y2 t)
        (and (rbaco-in-force c t) (not (= s1 s2)) (rbaco-constrains-task c s1) (rbaco-constrains-task c s2)
         (rbaco-scope-fits c i) (rbaco-performed y1 s1 i) (rbaco-performed y2 s2 i)
         (rbaco-same-dynamic-subject x y1 c i t) (rbaco-same-dynamic-subject x y2 c i t)))))))

  (cl:comment '--- Human in the loop and task-bound operations (not in Botha and Eloff) ---')

  (cl:comment 'Requirement h is violated by task instance k when h is in force when k begins, k is prescribed by the task specification h names, lies in an instance h fits, and has an agent that is never a person [rbaco-g1]'
    (forall (h k)
     (iff (rbaco-violates-human-requirement h k)
      (exists (s i x u t0)
       (and (rbaco-requires-human h s) (cco-prescribed-by k s) (occurrent-part-of k i) (rbaco-scope-fits h i)
        (occupies-temporal-region k u) (has-first-instant u t0) (rbaco-in-force h t0)
        (cco-has-agent k x) (not (exists (t) (instance-of x cco-person t))))))))

  (cl:comment 'Completion guard: task instance k, prescribed by s2 which requires prior s1, violates the guard when its business process instance holds no instance of s1 that precedes k and has a person as agent. The guard has no plan scope: it belongs to s2, unlike [rbaco-g1] and [rbaco-g3] (rbaco-bfo.owl, RBACO_0000144) [rbaco-g2]'
    (forall (k)
     (iff (rbaco-violates-prior-guard k)
      (exists (s1 s2 i)
       (and (exists (u) (instance-of k rbaco-task-instance u)) (cco-prescribed-by k s2) (rbaco-requires-prior s2 s1)
        (occurrent-part-of k i)
        (not (exists (k1 x)
              (and (cco-prescribed-by k1 s1) (occurrent-part-of k1 i) (precedes k1 k) (cco-has-agent k1 x)
               (exists (t) (instance-of x cco-person t))))))))))

  (cl:comment 'Requirement h is violated by access request q when h is in force at the time of q, q requests an operation h names, h applies within no plan or q is part of an instance h fits, and q is part of no task instance whose specification requires that operation [rbaco-g3]'
    (forall (h q)
     (iff (rbaco-violates-task-binding h q)
      (exists (o t0)
       (and (rbaco-requires-task-binding h o) (rbaco-requests-operation q o) (rbaco-request-time q t0) (rbaco-in-force h t0)
        (or (not (exists (p) (rbaco-applies-within h p)))
         (exists (i) (and (occurrent-part-of q i) (rbaco-scope-fits h i))))
        (not (exists (k s u)
              (and (occurrent-part-of q k) (instance-of k rbaco-task-instance u) (cco-prescribed-by k s)
               (rbaco-requires-operation s o)))))))))

  (cl:comment '--- RT role statements (ROWLBAC section 4.2) ---')

  (cl:comment 'Type 1, A.r <- D: D is a member of A.r while the statement is in force [rbaco-t1]'
    (forall (s a d t)
     (if (and (rbaco-in-force s t) (rbaco-has-head s a) (rbaco-names-member s d))
      (rbaco-member-of d a t))))

  (cl:comment 'Type 2, A.r <- B.r1: every member of B.r1 is a member of A.r. The head is the junior and the body the senior, as in rbaco-bfo.owl, where has junior role definition is a sub-property of has head role [rbaco-t2]'
    (forall (s a b x t)
     (if (and (rbaco-in-force s t) (rbaco-has-head s a) (rbaco-has-senior s b) (rbaco-member-of x b t))
      (rbaco-member-of x a t))))

  (cl:comment 'Type 3, A.r <- B.r1.r2: a member of y.r2, for any y in B.r1, is a member of A.r. rbaco-role-of-name y n e says e is the RT role of issuer y named n [rbaco-t3]'
    (forall (s a b n x y e t)
     (if (and (rbaco-in-force s t) (rbaco-has-head s a) (rbaco-has-linking-base s b)
          (rbaco-linked-role s n) (rbaco-member-of y b t) (rbaco-role-of-name y n e) (rbaco-member-of x e t))
      (rbaco-member-of x a t))))

  (cl:comment 'Type 4, A.r <- B1.r1 and B2.r2: members of both bodies are members of A.r [rbaco-t4]'
    (forall (s a b1 b2 x t)
     (if (and (rbaco-in-force s t) (rbaco-has-head s a) (rbaco-has-body s b1) (rbaco-has-body s b2)
          (not (= b1 b2)) (rbaco-member-of x b1 t) (rbaco-member-of x b2 t))
      (rbaco-member-of x a t))))

  (cl:comment 'Completion for one RT role (Clark completion, ROWLBAC section 4.2): only the rules above put x in A.r. Asserted per role, it is what the paper calls growth-restricted, and it makes membership the least fixpoint derive-rt-membership.rq computes. Not asserted for every role, so it is a schema, shown here for a role constant rt-role [rbaco-t5]'
    (forall (x t)
     (if (rbaco-member-of x rt-role t)
      (exists (s)
       (and (rbaco-in-force s t) (rbaco-has-head s rt-role)
        (or (rbaco-names-member s x)
         (exists (b) (and (rbaco-has-senior s b) (rbaco-member-of x b t)))
         (exists (b n y e) (and (rbaco-has-linking-base s b) (rbaco-linked-role s n) (rbaco-member-of y b t)
                            (rbaco-role-of-name y n e) (rbaco-member-of x e t)))
         (exists (b1 b2) (and (rbaco-has-body s b1) (rbaco-has-body s b2) (not (= b1 b2))
                          (rbaco-member-of x b1 t) (rbaco-member-of x b2 t)))))))))
))
