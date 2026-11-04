"""Generate the example datasets in data/ from the compact specifications below.

Usage: build_data.py <rbo-dir>

Writes data/us-persons.ttl (ROWLBAC section 3.1), data/code-review.ttl (CR-42),
data/abac.ttl (ROWLBAC section 4.1), data/rt-policy.ttl (ROWLBAC Figure 4), data/purchase.ttl
(Botha and Eloff 2001, the purchase workflow and its separation of duty interpretations) and
data/probes.ttl (regression probes, read together with purchase.ttl).
Every act occupies a temporal interval whose first instant carries a timestamp. Files are written in
dependency order by ttl_ordered.py: a block comes after every block it refers to.
"""
import os, sys
from rdflib import Graph, Namespace, URIRef, Literal, BNode, RDF, RDFS, OWL, XSD
from rdflib.collection import Collection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import annotate_ttl
import ttl_ordered

RBO = Namespace("https://example.org/rbac-bfo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
CCO = Namespace("https://www.commoncoreontologies.org/")
EX = Namespace("https://example.org/rbac-bfo/data/")

# RBO and borrowed terms used below, by readable name
C = dict(
    role_def=RBO.RBO_0000001, active_role=RBO.RBO_0000003, bp=RBO.RBO_0000004, bp_plan=RBO.RBO_0000005,
    permission=RBO.RBO_0000007, prohibition=RBO.RBO_0000008, obj_desc=RBO.RBO_0000009,
    office_cond=RBO.RBO_0000011, ssd=RBO.RBO_0000013, dsd_same=RBO.RBO_0000015, dsd_whole=RBO.RBO_0000016,
    inherit=RBO.RBO_0000017, access_req=RBO.RBO_0000024, act_req=RBO.RBO_0000025,
    activation=RBO.RBO_0000026, deactivation=RBO.RBO_0000027, assignment=RBO.RBO_0000028,
    deassignment=RBO.RBO_0000029, issuing=RBO.RBO_0000031, retiring=RBO.RBO_0000032, rt_role=RBO.RBO_0000033, rt1=RBO.RBO_0000035, rt2=RBO.RBO_0000036,
    rt3=RBO.RBO_0000037, rt4=RBO.RBO_0000038, analysis=RBO.RBO_0000039,
    status_review=RBO.RBO_0001016, office=RBO.RBO_0001018, classroom=RBO.RBO_0001019, lab=RBO.RBO_0001020,
    device=RBO.RBO_0001021, printer=RBO.RBO_0001022, classroom_printer=RBO.RBO_0001023,
    person=CCO.ont00001262, agent=CCO.ont00001017, organization=CCO.ont00001180,
    authority_role=CCO.ont00000187, ibe=CCO.ont00000253, database=CCO.ont00002006, ice=CCO.ont00000958,
    plan_spec=OBO.IAO_0000104, software=OBO.IAO_0000010,
    task_spec=RBO.RBO_0000040, task_instance=RBO.RBO_0000041, work_item=RBO.RBO_0000048,
    static_des=RBO.RBO_0000046, dynamic_des=RBO.RBO_0000047, human_req=RBO.RBO_0000049, task_bound_req=RBO.RBO_0000050,
    family=CCO.ont00000837, planned_act=CCO.ont00000228,
    interval=OBO.BFO_0000202, instant=OBO.BFO_0000203,
)
P = dict(
    has_operation=RBO.RBO_0000101, has_object=RBO.RBO_0000102, has_obj_desc=RBO.RBO_0000103,
    assigned_to=RBO.RBO_0000105, activated_in=RBO.RBO_0000106, requester=RBO.RBO_0000107,
    req_op=RBO.RBO_0000108, req_obj=RBO.RBO_0000109, req_act=RBO.RBO_0000110, fulfilled_by=RBO.RBO_0000111,
    constrained=RBO.RBO_0000114, applies_within=RBO.RBO_0000115, head=RBO.RBO_0000116, body=RBO.RBO_0000117,
    senior=RBO.RBO_0000118, junior=RBO.RBO_0000119, issuer=RBO.RBO_0000121, names_member=RBO.RBO_0000122,
    link_base=RBO.RBO_0000123, growth=RBO.RBO_0000129, shrink=RBO.RBO_0000130,
    cardinality=RBO.RBO_0000201, rt_name=RBO.RBO_0000202, linked_name=RBO.RBO_0000203,
    timestamp=RBO.RBO_0000205, mirrors=RBO.RBO_0000301, obj_type=RBO.RBO_0000302,
    loc_type=RBO.RBO_0000303, criteria_class=RBO.RBO_0000305, has_office=RBO.RBO_0001101,
    has_agent=CCO.ont00001833, has_output=CCO.ont00001986, has_input=CCO.ont00001921,
    prescribed_by=CCO.ont00001920, has_participant=OBO.BFO_0000057, realizes=OBO.BFO_0000055,
    concretizes=OBO.BFO_0000059, inheres_in=OBO.BFO_0000197, sdep=OBO.BFO_0000195,
    occurrent_part_of=OBO.BFO_0000132, occupies=OBO.BFO_0000199, first_instant=OBO.BFO_0000222,
    last_instant=OBO.BFO_0000224, located_in=OBO.BFO_0000171, carrier_of=OBO.BFO_0000101,
    requires_role=RBO.RBO_0000132, requires_op=RBO.RBO_0000133, constrained_perm=RBO.RBO_0000134,
    constrained_task=RBO.RBO_0000135, activated_for=RBO.RBO_0000136, req_act_for=RBO.RBO_0000137,
    designates_agent=RBO.RBO_0000138, designates_group=RBO.RBO_0000139, applies_to=RBO.RBO_0000140,
    wi_for=RBO.RBO_0000141, wi_in=RBO.RBO_0000142, on_behalf=RBO.RBO_0000143,
    requires_prior=RBO.RBO_0000144, requires_human=RBO.RBO_0000145, requires_binding=RBO.RBO_0000148,
    member_part_of=OBO.BFO_0000129, continuant_part_of=OBO.BFO_0000176,
)


class Data:
    def __init__(self, title, comment):
        self.g = ttl_ordered.OrderedGraph()
        for p, ns in (("rbo", RBO), ("obo", OBO), ("cco", CCO), ("ex", EX)):
            self.g.bind(p, ns)
        onto = URIRef(str(EX) + title)
        self.g.add((onto, RDF.type, OWL.Ontology))
        self.g.add((onto, OWL.imports, URIRef("https://example.org/rbac-bfo/rbo-domain.owl")))
        self.g.add((onto, RDFS.comment, Literal(comment, lang="en")))

    def ind(self, name, cls, label, **props):
        s = EX[name]
        for c in (cls if isinstance(cls, (list, tuple)) else [cls]):
            self.g.add((s, RDF.type, c))
        self.g.add((s, RDFS.label, Literal(label, lang="en")))
        for k, vs in props.items():
            for v in (vs if isinstance(vs, (list, tuple)) else [vs]):
                self.g.add((s, P[k], v if isinstance(v, (URIRef, Literal)) else EX[v]))
        return s

    def when(self, name, start, end=None):
        """The act or process `name` occupies an interval starting at `start` (and ending at `end`)."""
        iv, i0 = EX[f"{name}-interval"], EX[f"{name}-start"]
        self.g.add((EX[name], P["occupies"], iv))
        self.g.add((iv, RDF.type, C["interval"]))
        self.g.add((iv, P["first_instant"], i0))
        self.g.add((i0, RDF.type, C["instant"]))
        self.g.add((i0, P["timestamp"], Literal(start, datatype=XSD.dateTime)))
        if end:
            i1 = EX[f"{name}-end"]
            self.g.add((iv, P["last_instant"], i1))
            self.g.add((i1, RDF.type, C["instant"]))
            self.g.add((i1, P["timestamp"], Literal(end, datatype=XSD.dateTime)))

    def save(self, path):
        ttl_ordered.write(self.g, path)
        _, _, comments = annotate_ttl.annotate_file(path, LABELS)
        print(os.path.basename(path), len(self.g), "triples,", comments, "label comments")


def t(day, hhmm):
    return f"2026-0{day[0]}-{day[1:]}T{hhmm}:00Z"


def admin(d, who="officer", label="the security officer"):
    d.ind(who, C["person"], label)
    d.ind(f"{who}-authority", C["authority_role"], f"authority role of {label}", inheres_in=who)


def issue(d, name, when, outputs, agent="officer"):
    d.ind(name, C["issuing"], f"policy issuing act {name}", has_agent=agent, has_output=outputs,
          realizes=f"{agent}-authority")
    d.when(name, when)


def role_definitions(d, defs):
    """defs: {short: label}. Each definition is carried by its own database record."""
    for k, lab in defs.items():
        d.ind(f"def-{k}", C["role_def"], f"{lab} role definition")
        d.ind(f"rec-def-{k}", C["ibe"], f"database record of the {lab} role definition", carrier_of=f"def-{k}")


def inheritance(d, senior, junior):
    return d.ind(f"inh-{senior}-{junior}", C["inherit"], f"{senior} inherits from {junior}",
                 senior=f"def-{senior}", junior=f"def-{junior}")


def assign(d, person, k, cls, when, n=1):
    role = f"{person}-{k}-assigned-{n}"
    d.ind(role, cls, f"{person}'s assigned {k} role, tenure {n}", inheres_in=person, concretizes=f"def-{k}")
    act = f"{person}-assign-{k}-{n}"
    d.ind(act, C["assignment"], f"assignment of {person} to {k}", has_agent="officer",
          realizes="officer-authority", has_participant=person, has_output=role)
    d.when(act, when)
    return role


def activate(d, person, k, instance, when, assigned, n=1, granted=True):
    req = f"{person}-request-activate-{k}-{n}"
    d.ind(req, C["act_req"], f"{person} asks to activate {k}", requester=person, req_act=f"def-{k}",
          occurrent_part_of=instance)
    d.when(req, when)
    if granted:
        role = f"{person}-{k}-active-{n}"
        d.ind(role, C["active_role"], f"{person}'s active {k} role in {instance}", inheres_in=person,
              concretizes=f"def-{k}", sdep=assigned, activated_in=instance)
        act = f"{person}-activate-{k}-{n}"
        d.ind(act, C["activation"], f"activation of {k} by {person}", has_participant=person,
              has_output=role, occurrent_part_of=instance)
        d.when(act, when)
        d.g.add((EX[req], P["fulfilled_by"], EX[act]))
        return role


def deactivate(d, person, k, instance, when, n=1):
    act = f"{person}-deactivate-{k}-{n}"
    d.ind(act, C["deactivation"], f"deactivation of {k} by {person}", has_participant=person,
          has_input=f"{person}-{k}-active-{n}", occurrent_part_of=instance)
    d.when(act, when)


def access(d, name, person, op, instance, when, obj=None):
    props = dict(requester=person, req_op=op, occurrent_part_of=instance)
    if obj:
        props["req_obj"] = obj
    d.ind(name, C["access_req"], f"{person} asks to {op}" + (f" on {obj}" if obj else ""), **props)
    d.when(name, when)


def regulation(d, name, cls, k, op, label, **extra):
    return d.ind(name, cls, label, assigned_to=f"def-{k}", has_operation=op, **extra)


# ---------------------------------------------------------------- ROWLBAC section 3.1
def us_persons(out):
    d = Data("us-persons", "ROWLBAC section 3.1 scenario: the US persons role hierarchy (Figure 1), "
             "its permissions and prohibitions, two static and one dynamic separation of duty constraint, "
             "and Alice's and Bob's narratives, each hosted in one status eligibility review.")
    admin(d)
    defs = {"legal-person": "Person", "us-person": "US Person", "foreign-person": "Foreign Person",
            "citizen": "Citizen", "resident": "Resident", "visitor": "Visitor",
            "permanent-resident": "Permanent Resident", "pr-applicant": "Perm Residency Applicant",
            "temporary-resident": "Temporary Resident", "work-visa": "Work Visa Holder",
            "business-visa": "Business Visa Holder", "student-visa": "Student Visa Holder"}
    role_definitions(d, defs)
    universal = {"legal-person": RBO.RBO_0001001, "us-person": RBO.RBO_0001002,
                 "foreign-person": RBO.RBO_0001003, "citizen": RBO.RBO_0001004, "resident": RBO.RBO_0001005,
                 "visitor": RBO.RBO_0001006, "permanent-resident": RBO.RBO_0001007,
                 "pr-applicant": RBO.RBO_0001008, "temporary-resident": RBO.RBO_0001009,
                 "work-visa": RBO.RBO_0001010, "business-visa": RBO.RBO_0001011,
                 "student-visa": RBO.RBO_0001012}
    for k, cls in universal.items():
        d.g.add((cls, P["mirrors"], EX[f"def-{k}"]))
    # Figure 1 edges: senior (lower in the drawing) -> junior
    edges = [("us-person", "legal-person"), ("foreign-person", "legal-person"), ("citizen", "us-person"),
             ("resident", "us-person"), ("visitor", "us-person"), ("permanent-resident", "resident"),
             ("pr-applicant", "resident"), ("temporary-resident", "resident"),
             ("work-visa", "temporary-resident"), ("business-visa", "temporary-resident"),
             ("student-visa", "temporary-resident")]
    inh = [inheritance(d, s, j) for s, j in edges]
    for op, lab in (("op-vote", "vote-casting procedure"), ("op-work", "work procedure"),
                    ("op-jury", "jury service procedure")):
        d.ind(op, C["plan_spec"], lab)
    regs = [regulation(d, "perm-citizen-vote", C["permission"], "citizen", "op-vote", "Citizen: permitted Vote"),
            regulation(d, "perm-citizen-work", C["permission"], "citizen", "op-work", "Citizen: permitted Work"),
            regulation(d, "perm-citizen-jury", C["permission"], "citizen", "op-jury", "Citizen: permitted Jury"),
            regulation(d, "perm-pr-work", C["permission"], "permanent-resident", "op-work",
                       "Permanent Resident: permitted Work"),
            regulation(d, "perm-pra-work", C["permission"], "pr-applicant", "op-work",
                       "Perm Residency Applicant: permitted Work"),
            regulation(d, "perm-wvh-work", C["permission"], "work-visa", "op-work",
                       "Work Visa Holder: permitted Work"),
            regulation(d, "perm-bvh-work", C["permission"], "business-visa", "op-work",
                       "Business Visa Holder: permitted Work"),
            regulation(d, "proh-visitor-work", C["prohibition"], "visitor", "op-work", "Visitor: prohibited Work"),
            regulation(d, "proh-svh-work", C["prohibition"], "student-visa", "op-work",
                       "Student Visa Holder: prohibited Work")]
    one = Literal(2, datatype=XSD.positiveInteger)
    sod = [d.ind("ssd-resident-citizen", C["ssd"], "SSD {Resident, Citizen}, n = 2",
                 constrained=["def-resident", "def-citizen"], cardinality=one),
           d.ind("ssd-pr-tr", C["ssd"], "SSD {Permanent Resident, Temporary Resident}, n = 2",
                 constrained=["def-permanent-resident", "def-temporary-resident"], cardinality=one),
           d.ind("dsd-visitor-tr", C["dsd_same"], "DSD {Visitor, Temporary Resident}, n = 2, global",
                 constrained=["def-visitor", "def-temporary-resident"], cardinality=one)]
    plan = d.ind("plan-status-review", C["bp_plan"], "status eligibility review plan")
    issue(d, "policy-load", t("101", "08:00"),
          [EX[f"def-{k}"] for k in defs] + inh + regs + sod + [plan])

    for p in ("alice", "bob"):
        d.ind(p, C["person"], p.capitalize())
    a_cit = assign(d, "alice", "citizen", RBO.RBO_0001004, t("102", "09:00"))
    a_pr = assign(d, "alice", "permanent-resident", RBO.RBO_0001007, t("102", "10:00"))
    b_vis = assign(d, "bob", "visitor", RBO.RBO_0001006, t("102", "09:00"))
    b_tr = assign(d, "bob", "temporary-resident", RBO.RBO_0001009, t("102", "10:00"))

    d.ind("alice-review", C["status_review"], "Alice's status eligibility review", prescribed_by="plan-status-review")
    d.when("alice-review", t("105", "09:00"), t("105", "17:00"))
    activate(d, "alice", "citizen", "alice-review", t("105", "09:05"), a_cit)
    access(d, "alice-req-vote-1", "alice", "op-vote", "alice-review", t("105", "09:10"))
    access(d, "alice-req-work-1", "alice", "op-work", "alice-review", t("105", "09:11"))
    access(d, "alice-req-jury-1", "alice", "op-jury", "alice-review", t("105", "09:12"))
    deactivate(d, "alice", "citizen", "alice-review", t("105", "09:20"))
    activate(d, "alice", "permanent-resident", "alice-review", t("105", "09:25"), a_pr)
    access(d, "alice-req-vote-2", "alice", "op-vote", "alice-review", t("105", "09:30"))
    access(d, "alice-req-work-2", "alice", "op-work", "alice-review", t("105", "09:31"))
    access(d, "alice-req-jury-2", "alice", "op-jury", "alice-review", t("105", "09:32"))
    deactivate(d, "alice", "permanent-resident", "alice-review", t("105", "17:00"))

    d.ind("bob-review", C["status_review"], "Bob's status eligibility review", prescribed_by="plan-status-review")
    d.when("bob-review", t("105", "10:00"), t("105", "17:00"))
    activate(d, "bob", "visitor", "bob-review", t("105", "10:05"), b_vis)
    access(d, "bob-req-work-1", "bob", "op-work", "bob-review", t("105", "10:10"))
    activate(d, "bob", "temporary-resident", "bob-review", t("105", "10:15"), b_tr, granted=False)
    activate(d, "bob", "citizen", "bob-review", t("105", "10:20"), None, granted=False)
    deactivate(d, "bob", "visitor", "bob-review", t("105", "17:00"))
    d.save(os.path.join(out, "us-persons.ttl"))


# ---------------------------------------------------------------- CR-42
def code_review(out):
    d = Data("code-review", "Code change review CR-42: one business process instance shared by two "
             "participants, with a dynamic separation of duty constraint that counts the whole instance. "
             "Not in ROWLBAC; it exercises the business-process sessions this design introduces.")
    admin(d)
    role_definitions(d, {"submitter": "Submitter", "approver": "Approver"})
    d.ind("op-git-push", C["software"], "push commit (version control software)")
    d.ind("op-approve-merge", C["software"], "approve merge (review software)")
    d.ind("repo-acme", C["database"], "the acme code repository")
    d.ind("change-42", C["ice"], "change 42")
    regs = [regulation(d, "perm-submitter-push", C["permission"], "submitter", "op-git-push",
                       "Submitter: push commit to the acme repository", has_object="repo-acme"),
            regulation(d, "perm-approver-approve", C["permission"], "approver", "op-approve-merge",
                       "Approver: approve merge of change 42", has_object="change-42")]
    plan = d.ind("plan-code-review", C["bp_plan"], "code change review plan")
    dsd = d.ind("dsd-submitter-approver", C["dsd_whole"],
                "DSD {Submitter, Approver}, n = 2, code change reviews, whole instance",
                constrained=["def-submitter", "def-approver"], cardinality=Literal(2, datatype=XSD.positiveInteger),
                applies_within="plan-code-review")
    issue(d, "policy-load", t("101", "08:00"), [EX["def-submitter"], EX["def-approver"], plan, dsd] + regs)
    for p in ("dana", "eve"):
        d.ind(p, C["person"], p.capitalize())
    dana_sub = assign(d, "dana", "submitter", RBO.RBO_0000002, t("102", "09:00"))
    dana_app = assign(d, "dana", "approver", RBO.RBO_0000002, t("102", "09:01"))
    eve_app = assign(d, "eve", "approver", RBO.RBO_0000002, t("102", "09:02"))
    d.ind("cr-42", C["bp"], "code change review CR-42", prescribed_by="plan-code-review")
    d.when("cr-42", t("106", "09:00"), t("106", "18:00"))
    activate(d, "dana", "submitter", "cr-42", t("106", "09:05"), dana_sub)
    access(d, "dana-req-push", "dana", "op-git-push", "cr-42", t("106", "09:10"), obj="repo-acme")
    activate(d, "eve", "approver", "cr-42", t("106", "11:00"), eve_app)
    access(d, "eve-req-approve", "eve", "op-approve-merge", "cr-42", t("106", "11:05"), obj="change-42")
    deactivate(d, "eve", "approver", "cr-42", t("106", "11:10"))
    deactivate(d, "dana", "submitter", "cr-42", t("106", "12:00"))
    activate(d, "dana", "approver", "cr-42", t("106", "12:05"), dana_app, granted=False)
    access(d, "dana-req-approve", "dana", "op-approve-merge", "cr-42", t("106", "12:06"), obj="change-42")
    d.save(os.path.join(out, "code-review.ttl"))


# ---------------------------------------------------------------- ROWLBAC section 4.1
def abac(out):
    d = Data("abac", "ROWLBAC section 4.1: faculty can use any printer located in a classroom (an OWL "
             "defined class), and a university member can use any device located in her office "
             "(a role value map, decided by query only). Marie holds both roles.")
    admin(d)
    role_definitions(d, {"faculty": "Faculty", "university-member": "University Member"})
    d.g.add((RBO.RBO_0001025, P["mirrors"], EX["def-faculty"]))
    d.g.add((RBO.RBO_0001024, P["mirrors"], EX["def-university-member"]))
    for k, cls, lab in (("classroom-c101", C["classroom"], "classroom C101"), ("lab-l1", C["lab"], "laboratory L1"),
                        ("office-o12", C["office"], "office O12"), ("office-o13", C["office"], "office O13")):
        d.ind(k, cls, lab)
    for k, cls, lab, room in (("printer-p43", C["printer"], "printer p43", "classroom-c101"),
                              ("printer-p44", C["printer"], "printer p44", "lab-l1"),
                              ("display-d7", C["device"], "display d7", "office-o12"),
                              ("display-d8", C["device"], "display d8", "office-o13")):
        d.ind(k, cls, lab, located_in=room)
    d.ind("op-use-device", C["plan_spec"], "device use procedure")
    desc1 = d.ind("desc-classroom-printer", C["obj_desc"], "any printer located in a classroom")
    d.g.add((desc1, P["obj_type"], C["printer"])); d.g.add((desc1, P["loc_type"], C["classroom"]))
    d.g.add((desc1, P["criteria_class"], C["classroom_printer"]))
    desc2 = d.ind("desc-own-office-device", C["office_cond"], "any device located in the requester's office")
    d.g.add((desc2, P["obj_type"], C["device"]))
    regs = [regulation(d, "perm-faculty-classroom-printers", C["permission"], "faculty", "op-use-device",
                       "Faculty: use any printer located in a classroom", has_obj_desc="desc-classroom-printer"),
            regulation(d, "perm-member-office-devices", C["permission"], "university-member", "op-use-device",
                       "University member: use any device located in her office",
                       has_obj_desc="desc-own-office-device")]
    plan = d.ind("plan-teaching-day", C["bp_plan"], "teaching day plan")
    issue(d, "policy-load", t("101", "08:00"), [EX["def-faculty"], EX["def-university-member"], plan] + regs)
    d.ind("marie", C["person"], "Marie", has_office="office-o12")
    m_fac = assign(d, "marie", "faculty", RBO.RBO_0001025, t("102", "09:00"))
    m_mem = assign(d, "marie", "university-member", RBO.RBO_0001024, t("102", "09:01"))
    d.ind("marie-day", C["bp"], "Marie's teaching day", prescribed_by="plan-teaching-day")
    d.when("marie-day", t("107", "08:00"), t("107", "18:00"))
    activate(d, "marie", "faculty", "marie-day", t("107", "08:05"), m_fac)
    activate(d, "marie", "university-member", "marie-day", t("107", "08:06"), m_mem)
    for i, obj in enumerate(("printer-p43", "printer-p44", "display-d7", "display-d8"), 1):
        access(d, f"marie-req-use-{obj}", "marie", "op-use-device", "marie-day", t("107", f"09:0{i}"), obj=obj)
    d.save(os.path.join(out, "abac.ttl"))


# ---------------------------------------------------------------- ROWLBAC Figure 4
def rt_policy(out):
    d = Data("rt-policy", "ROWLBAC Figure 4: an RT access policy of a company, its fifteen statements, "
             "and an analysis specification naming the growth- and shrink-restricted roles. Figure 4 writes "
             "the type 1 statement for Alice as HR.manager; it is encoded against HR.managers, the role "
             "every other statement uses.")
    for k, lab in (("HQ", "HQ"), ("HR", "HR")):
        d.ind(f"rt-{k}", [C["organization"], C["agent"]], f"principal {lab}")
    for k in ("Alice", "Bob"):
        d.ind(f"rt-{k}", [C["person"], C["agent"]], f"principal {k}")
    roles = {"HQ": ["marketing", "ops", "marketingDelg", "staff", "specialPanel"],
             "HR": ["managers", "sales", "employee", "manufacturing", "researchDev"]}
    for iss, names in roles.items():
        for r in names:
            d.ind(f"rt-{iss}.{r}", C["rt_role"], f"{iss}.{r}", issuer=f"rt-{iss}",
                  rt_name=Literal(r, datatype=XSD.string))
    R = lambda s: f"rt-{s}"
    stmts = {"HQ": [], "HR": []}

    def st(n, cls, headrole, **kw):
        lab = kw.pop("label")
        s = d.ind(f"rt-stmt-{n:02d}", cls, lab, head=R(headrole), **kw)
        stmts[headrole.split(".")[0]].append(s)

    st(1, C["rt2"], "HQ.marketing", junior=R("HQ.marketing"), senior=R("HR.managers"), label="HQ.marketing <- HR.managers")
    st(2, C["rt2"], "HQ.marketing", junior=R("HQ.marketing"), senior=R("HQ.staff"), label="HQ.marketing <- HQ.staff")
    st(3, C["rt2"], "HQ.marketing", junior=R("HQ.marketing"), senior=R("HR.sales"), label="HQ.marketing <- HR.sales")
    st(4, C["rt4"], "HQ.marketing", body=[R("HQ.marketingDelg"), R("HR.employee")],
       label="HQ.marketing <- HQ.marketingDelg AND HR.employee")
    st(5, C["rt2"], "HQ.ops", junior=R("HQ.ops"), senior=R("HR.managers"), label="HQ.ops <- HR.managers")
    st(6, C["rt2"], "HQ.ops", junior=R("HQ.ops"), senior=R("HR.manufacturing"), label="HQ.ops <- HR.manufacturing")
    st(7, C["rt3"], "HQ.marketingDelg", link_base=R("HR.managers"),
       linked_name=Literal("access", datatype=XSD.string), label="HQ.marketingDelg <- HR.managers.access")
    st(8, C["rt2"], "HR.employee", junior=R("HR.employee"), senior=R("HR.managers"), label="HR.employee <- HR.managers")
    st(9, C["rt2"], "HR.employee", junior=R("HR.employee"), senior=R("HR.sales"), label="HR.employee <- HR.sales")
    st(10, C["rt2"], "HR.employee", junior=R("HR.employee"), senior=R("HR.manufacturing"),
       label="HR.employee <- HR.manufacturing")
    st(11, C["rt2"], "HR.employee", junior=R("HR.employee"), senior=R("HR.researchDev"),
       label="HR.employee <- HR.researchDev")
    st(12, C["rt2"], "HQ.staff", junior=R("HQ.staff"), senior=R("HR.managers"), label="HQ.staff <- HR.managers")
    st(13, C["rt4"], "HQ.staff", body=[R("HQ.specialPanel"), R("HR.researchDev")],
       label="HQ.staff <- HQ.specialPanel AND HR.researchDev")
    st(14, C["rt1"], "HR.managers", names_member=R("Alice"), label="HR.managers <- Alice (Figure 4: HR.manager)")
    st(15, C["rt1"], "HR.researchDev", names_member=R("Bob"), label="HR.researchDev <- Bob")
    for iss, out_stmts in stmts.items():
        d.ind(f"rt-{iss}-authority", C["authority_role"], f"authority of {iss} over its own roles",
              inheres_in=f"rt-{iss}")
        issue(d, f"rt-issue-{iss}", t("101", "08:00"),
              out_stmts + [EX[f"rt-{iss}.{r}"] for r in roles[iss]], agent=f"rt-{iss}")
    restricted = [R(x) for x in ("HQ.marketing", "HQ.ops", "HR.employee", "HQ.marketingDelg", "HQ.staff")]
    d.ind("rt-analysis", C["analysis"], "Figure 4 security analysis", growth=restricted, shrink=restricted)
    d.save(os.path.join(out, "rt-policy.ttl"))


# ---------------------------------------------------------------- Botha and Eloff 2001
def purchase(out):
    d = Data("purchase", "Botha and Eloff (2001): the purchase order workflow of Figure 2 on the role hierarchy "
             "of Figure 3, with Figure 6's Approver role, run under each of Table 2's dynamic interpretations "
             "(conflicting roles, permissions, users, tasks) in plans of their own, an internal purchase order "
             "process with a human performer requirement, a prior-task guard and a partial task binding, task-bound "
             "operations in the Figure 6 plan, and the static cross-entity "
             "rules of Tables 1 and 3. Each instance is one scenario.")
    admin(d)
    two = Literal(2, datatype=XSD.positiveInteger)
    defs = {"employee": "Employee", "sc": "Stock Controller", "buyer": "Buyer", "accountant": "Accountant",
            "clerk": "Clerk", "apm": "Assistant Purchase Manager", "approver": "Approver",
            "manager": "Manager", "stores": "Stores", "auditor": "Auditor"}
    role_definitions(d, defs)
    # Figure 3 (arrowheads on the junior), plus Figure 6's Approver, junior to the APM only
    edges = [("apm", "buyer"), ("apm", "accountant"), ("buyer", "sc"), ("accountant", "clerk"),
             ("sc", "employee"), ("clerk", "employee"), ("apm", "approver")]
    inh = [inheritance(d, s, j) for s, j in edges]
    ops = {"create-requisition": "create requisition", "create-order": "create order", "view-order": "view order",
           "send-email": "send e-mail", "confirm-funds": "confirm funds", "approve-order": "approve order",
           "create-rejection-letter": "create rejection letter", "complete-order-form": "complete order form",
           "approve-po": "approve purchase order", "issue-items": "issue items", "approve-audit": "approve audit"}
    for k, lab in ops.items():
        d.ind(f"op-{k}", C["plan_spec"], f"{lab} procedure")
    perms = [("employee", "email", "send-email"), ("sc", "requisition", "create-requisition"),
             ("buyer", "order", "create-order"), ("buyer", "view", "view-order"),
             ("accountant", "funds", "confirm-funds"), ("apm", "approve", "approve-order"),
             ("apm", "reject", "create-rejection-letter"), ("approver", "approve", "approve-order"),
             ("manager", "form", "complete-order-form"), ("manager", "approve-po", "approve-po"),
             ("stores", "issue", "issue-items"), ("auditor", "audit", "approve-audit")]
    regs = [regulation(d, f"perm-{k}-{s}", C["permission"], k, f"op-{op}", f"{defs[k]}: permitted {ops[op]}")
            for k, s, op in perms]
    plans = {"t2-roles": "purchase order process, conflicting roles",
             "t2-perms": "purchase order process, conflicting permissions",
             "t2-users": "purchase order process, conflicting users",
             "t2-tasks": "purchase order process, conflicting tasks",
             "fig6": "purchase order process, Figure 6 hierarchy",
             "internal-po": "internal purchase order process", "audit": "purchase audit process"}
    for k, lab in plans.items():
        d.ind(f"plan-{k}", C["bp_plan"], f"{lab} plan")
    t2 = [f"plan-{k}" for k in ("t2-roles", "t2-perms", "t2-users", "t2-tasks")]
    # task specifications: (short, label, required role, required operations, plans)
    tasks = [("prepare-requisition", "prepare requisition", "sc", ["create-requisition"], t2 + ["plan-fig6"]),
             ("order-stock", "order stock", "buyer", ["create-order", "view-order"], t2),
             ("check-funds", "check funds", "accountant", ["confirm-funds"], t2),
             ("approve-order", "approve order", "apm", ["approve-order"], t2),
             ("send-order", "send order", "buyer", ["send-email", "view-order"], t2),
             ("approve-order-fig6", "approve order (Figure 6)", "approver", ["approve-order"], ["plan-fig6"]),
             ("complete-form", "complete order form", "manager", ["complete-order-form"], ["plan-internal-po"]),
             ("approve-po", "approve purchase order", "manager", ["approve-po"], ["plan-internal-po"]),
             ("issue-items", "issue items", "stores", ["issue-items"], ["plan-internal-po"]),
             ("approve-audit", "approve audit", "auditor", ["approve-audit"], ["plan-audit"])]
    specs = [d.ind(f"ts-{k}", C["task_spec"], f"{lab} task specification", requires_role=f"def-{r}",
                   requires_op=[f"op-{o}" for o in os_], continuant_part_of=pl) for k, lab, r, os_, pl in tasks]
    d.g.add((EX["ts-issue-items"], P["requires_prior"], EX["ts-approve-po"]))
    d.ind("tom-dick-family", C["family"], "the family of Tom and Dick")
    d.ind("workflow-engine", C["agent"], "the workflow engine")
    for who, lab in (("stores-host", "the stores application host"), ("approval-bot", "the approval robot")):
        d.ind(who, C["agent"], lab)
    for p in ("tom", "dick", "harry"):
        d.ind(p, C["person"], p.capitalize())
    for p in ("tom", "dick"):
        d.g.add((EX[p], P["member_part_of"], EX["tom-dick-family"]))
    sod = [
        # static (Table 1): conflicting roles, permissions, tasks, and users
        d.ind("ssd-auditor-apm", C["ssd"], "SSD {Auditor, APM}, n = 2",
              constrained=["def-auditor", "def-apm"], cardinality=two),
        d.ind("pssd-approve-audit", C["ssd"], "permission SSD {APM: approve order, Auditor: approve audit}, n = 2",
              constrained_perm=["perm-apm-approve", "perm-auditor-audit"], cardinality=two),
        d.ind("tssd-approve-audit", C["ssd"], "task SSD {approve order, approve audit}, n = 2",
              constrained_task=["ts-approve-order", "ts-approve-audit"], cardinality=two),
        d.ind("sdes-family", C["static_des"], "static conflicting agents: the members of Tom and Dick's family",
              designates_group="tom-dick-family"),
        # static sets with no role constraint behind them (Table 3 rows 3 and 4, warnings)
        d.ind("pssd-issue-approve-po", C["ssd"],
              "permission SSD {Stores: issue items, Manager: approve purchase order}, n = 2",
              constrained_perm=["perm-stores-issue", "perm-manager-approve-po"], cardinality=two),
        d.ind("tssd-issue-approve-po", C["ssd"], "task SSD {issue items, approve purchase order}, n = 2",
              constrained_task=["ts-issue-items", "ts-approve-po"], cardinality=two),
        # dynamic, whole instance (Table 2)
        d.ind("dsd-sc-apm", C["dsd_whole"], "DSD {Stock Controller, APM}, n = 2, conflicting roles plan",
              constrained=["def-sc", "def-apm"], cardinality=two, applies_within="plan-t2-roles"),
        d.ind("pdsd-perms", C["dsd_whole"],
              "permission DSD {SC: create requisition, APM: approve order}, n = 2, conflicting permissions plan",
              constrained_perm=["perm-sc-requisition", "perm-apm-approve"], cardinality=two,
              applies_within="plan-t2-perms"),
        d.ind("pdsd-users", C["dsd_whole"],
              "permission DSD {SC: create requisition, APM: approve order}, n = 2, conflicting users plan",
              constrained_perm=["perm-sc-requisition", "perm-apm-approve"], cardinality=two,
              applies_within="plan-t2-users"),
        d.ind("ddes-users", C["dynamic_des"], "dynamic conflicting agents Tom and Dick, conflicting users plan",
              designates_agent=["tom", "dick"], applies_within="plan-t2-users"),
        d.ind("tdsd-tasks", C["dsd_whole"],
              "task DSD {prepare requisition, approve order}, n = 2, conflicting tasks plan",
              constrained_task=["ts-prepare-requisition", "ts-approve-order"], cardinality=two,
              applies_within="plan-t2-tasks"),
        d.ind("dsd-sc-approver", C["dsd_whole"], "DSD {Stock Controller, Approver}, n = 2, Figure 6 plan",
              constrained=["def-sc", "def-approver"], cardinality=two, applies_within="plan-fig6"),
        d.ind("tdsd-internal", C["dsd_whole"],
              "task DSD {complete order form, approve purchase order}, n = 2, internal purchase orders",
              constrained_task=["ts-complete-form", "ts-approve-po"], cardinality=two,
              applies_within="plan-internal-po"),
        d.ind("ddes-internal", C["dynamic_des"], "dynamic conflicting agents Tom and Dick, internal purchase orders",
              designates_agent=["tom", "dick"], applies_within="plan-internal-po"),
        d.ind("human-approve-po", C["human_req"], "a person approves internal purchase orders",
              requires_human="ts-approve-po", applies_within="plan-internal-po"),
        d.ind("ddes-audit", C["dynamic_des"], "dynamic conflicting agents Dick and Harry, purchase audits",
              designates_agent=["dick", "harry"], applies_within="plan-audit"),
        # task-bound operations: Figure 6's two conflicting operations only within their tasks; in
        # internal purchase orders, approval only (a partial binding, which check-sod-hierarchy.rq warns of)
        d.ind("tbr-fig6", C["task_bound_req"],
              "create requisition and approve order only within a task that requires them, Figure 6 plan",
              requires_binding=["op-create-requisition", "op-approve-order"], applies_within="plan-fig6"),
        d.ind("tbr-internal", C["task_bound_req"],
              "approve purchase order only within a task that requires it, internal purchase orders",
              requires_binding="op-approve-po", applies_within="plan-internal-po"),
    ]
    issue(d, "policy-load", t("101", "08:00"),
          [EX[f"def-{k}"] for k in defs] + inh + regs + specs + sod + [EX[f"plan-{k}"] for k in plans])
    # OWL has no unique-name assumption: without this, HermiT cannot count two members of a set, so it
    # can neither classify a constraint under its kind (RBO_0000042-44) nor reject a mixed set
    distinct = BNode()
    d.g.add((distinct, RDF.type, OWL.AllDifferent))
    d.g.add((distinct, OWL.distinctMembers, Collection(d.g, BNode(),
             [EX[f"def-{k}"] for k in defs] + regs + specs).uri))

    held = {}
    for who, k in (("tom", "apm"), ("tom", "manager"), ("dick", "sc"), ("dick", "manager"), ("harry", "apm"),
                   ("harry", "manager"), ("stores-host", "stores"), ("approval-bot", "manager")):
        held[(who, k)] = assign(d, who, k, RBO.RBO_0000002, t("102", "09:00"))

    def instance(n, plan, day, start, end):
        d.ind(n, C["bp"], f"purchase order {n}", prescribed_by=f"plan-{plan}")
        d.when(n, t(day, start), t(day, end))

    def work_item(inst, task, day, hhmm):
        wi = f"wi-{inst}-{task}"
        d.ind(wi, C["work_item"], f"work item: {task} in {inst}", wi_for=f"ts-{task}", wi_in=inst)
        act = f"issue-{wi}"
        d.ind(act, C["planned_act"], f"workflow engine issues {wi}", has_agent="workflow-engine", has_output=wi)
        d.when(act, t(day, hhmm))
        return wi

    def take(who, k, inst, day, start, end, wi=None, granted=True, behalf=None, steps=(), via=None):
        """who asks to activate k in inst at start, for work item wi if given. If granted and wi is
        given, the task instance runs from start to end; steps are (hhmm, operation) access requests
        inside it (or inside the instance, for an unbound activation). The role is dropped at end.
        via names the held role definition that authorizes k through the hierarchy, if not k itself."""
        n = inst
        role = activate(d, who, k, inst, t(day, start), held.get((who, via or k)),
                        n=n, granted=granted)
        req = EX[f"{who}-request-activate-{k}-{n}"]
        if wi:
            d.g.add((req, P["req_act_for"], EX[wi]))
        if behalf:
            d.g.add((req, P["on_behalf"], EX[behalf]))
        if not granted:
            return
        task = None
        if wi:
            task = f"task-{wi[3:]}"
            d.ind(task, C["task_instance"], f"{who}'s task instance for {wi}", has_agent=who,
                  prescribed_by=[wi, d.g.value(EX[wi], P["wi_for"])], occurrent_part_of=inst)
            d.when(task, t(day, start), t(day, end))
            d.g.add((EX[role], P["activated_for"], EX[task]))
        for hhmm, op in steps:
            name = f"{who}-req-{op}-{inst}"
            access(d, name, who, f"op-{op}", inst, t(day, hhmm))
            if task:
                d.g.add((EX[name], P["occurrent_part_of"], EX[task]))
        deactivate(d, who, k, inst, t(day, end), n=n)

    # po-1, Botha and Eloff's WSession example (p.674): Tom may not take the order-stock work item as
    # APM, only as Buyer, whose junior roles still reach send e-mail and create requisition
    instance("po-1", "t2-roles", "103", "09:00", "17:00")
    wi = work_item("po-1", "order-stock", "103", "09:00")
    take("tom", "apm", "po-1", "103", "09:05", None, wi=wi, granted=False)
    take("tom", "buyer", "po-1", "103", "09:06", "09:30", wi=wi, via="apm",
         steps=(("09:10", "create-order"), ("09:11", "view-order"), ("09:12", "send-email"),
                ("09:13", "create-requisition"), ("09:14", "approve-order")))
    # po-2, the hierarchy bypass (section 3.3.5): APM alone reaches both conflicting operations
    instance("po-2", "t2-roles", "104", "09:00", "17:00")
    take("tom", "apm", "po-2", "104", "09:00", "09:30",
         steps=(("09:05", "create-requisition"), ("09:10", "approve-order")))
    # po-3, the same steps under conflicting permissions: the second is denied
    instance("po-3", "t2-perms", "105", "09:00", "17:00")
    take("tom", "apm", "po-3", "105", "09:00", "09:30",
         steps=(("09:05", "create-requisition"), ("09:10", "approve-order")))
    # po-4, conflicting roles, task-bound: Harry prepared the requisition, so not Harry as APM
    instance("po-4", "t2-roles", "106", "09:00", "17:00")
    w1 = work_item("po-4", "prepare-requisition", "106", "09:00")
    w4 = work_item("po-4", "approve-order", "106", "09:00")
    take("harry", "sc", "po-4", "106", "09:05", "09:20", wi=w1, steps=(("09:10", "create-requisition"),), via="apm")
    take("harry", "apm", "po-4", "106", "09:30", None, wi=w4, granted=False)
    take("tom", "apm", "po-4", "106", "09:40", "09:50", wi=w4, steps=(("09:45", "approve-order"),))
    # po-5, conflicting users: Dick prepared the requisition, and Tom counts as one with Dick here
    instance("po-5", "t2-users", "107", "09:00", "17:00")
    w1 = work_item("po-5", "prepare-requisition", "107", "09:00")
    w4 = work_item("po-5", "approve-order", "107", "09:00")
    take("dick", "sc", "po-5", "107", "09:05", "09:20", wi=w1, steps=(("09:10", "create-requisition"),))
    take("tom", "apm", "po-5", "107", "09:40", "09:50", wi=w4, steps=(("09:45", "approve-order"),))
    # po-6, conflicting tasks
    instance("po-6", "t2-tasks", "108", "09:00", "17:00")
    w1 = work_item("po-6", "prepare-requisition", "108", "09:00")
    w4 = work_item("po-6", "approve-order", "108", "09:00")
    take("harry", "sc", "po-6", "108", "09:05", "09:20", wi=w1, steps=(("09:10", "create-requisition"),), via="apm")
    take("harry", "apm", "po-6", "108", "09:30", None, wi=w4, granted=False)
    take("tom", "apm", "po-6", "108", "09:40", "09:50", wi=w4, steps=(("09:45", "approve-order"),))
    # po-7, Figure 6: approval moves to Approver, which is not senior to Stock Controller
    instance("po-7", "fig6", "109", "09:00", "17:00")
    w1 = work_item("po-7", "prepare-requisition", "109", "09:00")
    w4 = work_item("po-7", "approve-order-fig6", "109", "09:00")
    take("tom", "sc", "po-7", "109", "09:05", "09:20", wi=w1, steps=(("09:10", "create-requisition"),), via="apm")
    take("tom", "approver", "po-7", "109", "09:30", None, wi=w4, granted=False, via="apm")
    take("harry", "approver", "po-7", "109", "09:40", "09:50", wi=w4, steps=(("09:45", "approve-order"),), via="apm")
    # po-7b, Figure 6 without a work item: APM reaches both conflicting operations through the
    # hierarchy, but both are task-bound in this plan (tbr-fig6), so both are denied; send e-mail is not
    instance("po-7b", "fig6", "110", "09:00", "17:00")
    take("tom", "apm", "po-7b", "110", "09:00", "09:30",
         steps=(("09:05", "create-requisition"), ("09:10", "approve-order"), ("09:15", "send-email")))
    # po-10, the internal purchase order process: Tom completes the form; neither Tom nor Dick,
    # counted as one here, may approve it; the stores host issues the items once a person has
    instance("po-10", "internal-po", "111", "09:00", "17:00")
    wf = work_item("po-10", "complete-form", "111", "09:00")
    wa = work_item("po-10", "approve-po", "111", "09:00")
    wx = work_item("po-10", "issue-items", "111", "09:00")
    take("tom", "manager", "po-10", "111", "09:00", "09:20", wi=wf, steps=(("09:05", "complete-order-form"),))
    take("dick", "manager", "po-10", "111", "09:40", None, wi=wa, granted=False)
    take("harry", "manager", "po-10", "111", "09:45", "10:00", wi=wa, steps=(("09:50", "approve-po"),))
    take("stores-host", "stores", "po-10", "111", "10:10", "10:20", wi=wx, steps=(("10:15", "issue-items"),))
    # po-11: the approval robot may not approve, even on Tom's behalf, and the stores host may not
    # issue items before a person has approved
    instance("po-11", "internal-po", "112", "09:00", "17:00")
    wf = work_item("po-11", "complete-form", "112", "09:00")
    wa = work_item("po-11", "approve-po", "112", "09:00")
    wx = work_item("po-11", "issue-items", "112", "09:00")
    take("tom", "manager", "po-11", "112", "09:00", "09:20", wi=wf, steps=(("09:05", "complete-order-form"),))
    take("approval-bot", "manager", "po-11", "112", "09:30", None, wi=wa, granted=False, behalf="tom")
    take("stores-host", "stores", "po-11", "112", "09:35", None, wi=wx, granted=False)
    # Table 1 row 3 and Table 3 row 1: Dick, of Tom's family, becomes an auditor while Tom holds APM
    assign(d, "dick", "auditor", RBO.RBO_0000002, t("120", "09:00"))
    d.save(os.path.join(out, "purchase.ttl"))


# ---------------------------------------------------------------- regression probes, read with purchase.ttl
def probes(out):
    d = Data("probes", "Regression probes for the remediations of 2026-10-31, read together with purchase.ttl: "
             "permissions identified by content (probes 1 and 2), access requests at one instant (3), an active "
             "role ending with the assigned role it depends on (4), designations counted only while in force "
             "(5 and 6), static separation of duty at an issuing act (7), and activation requests at one "
             "instant (8). Each probe has an instance or act of its own; tools/run_queries.py checks the "
             "results each must give.")
    two = Literal(2, datatype=XSD.positiveInteger)
    for k in ("2", "4"):
        d.ind(f"probe-plan-{k}", C["bp_plan"], f"probe {k} plan")
    d.ind("probe-pdsd-2", C["dsd_whole"],
          "permission DSD {SC: create requisition, APM: approve order, Approver: approve order}, n = 2, probe 2 plan",
          constrained_perm=["perm-sc-requisition", "perm-apm-approve", "perm-approver-approve"], cardinality=two,
          applies_within="probe-plan-2")
    issue(d, "probe-policy", t("201", "08:00"), [EX["probe-plan-2"], EX["probe-plan-4"], EX["probe-pdsd-2"]])

    def instance(n, plan, day):
        d.ind(n, C["bp"], f"purchase order {n}", prescribed_by=plan)
        d.when(n, t(day, "09:00"), t(day, "17:00"))

    # 1: the Approver's approve-order permission has the content of the APM's, a member of the set, so the
    #    conflicting-permissions DSD refuses it after the requisition
    instance("probe-1", "plan-t2-perms", "202")
    activate(d, "tom", "sc", "probe-1", t("202", "09:00"), "tom-apm-assigned-1", n="probe-1")
    access(d, "tom-req-create-requisition-probe-1", "tom", "op-create-requisition", "probe-1", t("202", "09:05"))
    activate(d, "tom", "approver", "probe-1", t("202", "09:10"), "tom-apm-assigned-1", n="probe-1")
    access(d, "tom-req-approve-order-probe-1", "tom", "op-approve-order", "probe-1", t("202", "09:15"))
    for k in ("sc", "approver"):
        deactivate(d, "tom", k, "probe-1", t("202", "09:30"), n="probe-1")
    # 2: the APM reaches approve order through two permissions of the set with one content, which count once
    instance("probe-2", "probe-plan-2", "203")
    activate(d, "tom", "apm", "probe-2", t("203", "09:00"), "tom-apm-assigned-1", n="probe-2")
    access(d, "tom-req-approve-order-probe-2", "tom", "op-approve-order", "probe-2", t("203", "09:05"))
    deactivate(d, "tom", "apm", "probe-2", t("203", "09:30"), n="probe-2")
    # 3: two access requests at one instant are taken in IRI order: approve order is granted, and the
    #    requisition then completes the conflicting-permissions set
    instance("probe-3", "plan-t2-perms", "204")
    activate(d, "tom", "apm", "probe-3", t("204", "09:00"), "tom-apm-assigned-1", n="probe-3")
    for op in ("approve-order", "create-requisition"):
        access(d, f"tom-req-{op}-probe-3", "tom", f"op-{op}", "probe-3", t("204", "09:05"))
    deactivate(d, "tom", "apm", "probe-3", t("204", "09:30"), n="probe-3")
    # 4: Harry loses Manager while it is active and never deactivates it: the later request is denied,
    #    and check-active-roles.rq reports the active role
    instance("probe-4", "probe-plan-4", "205")
    activate(d, "harry", "manager", "probe-4", t("205", "09:00"), "harry-manager-assigned-1", n="probe-4")
    d.ind("harry-deassign-manager-1", C["deassignment"], "deassignment of harry from manager", has_agent="officer",
          realizes="officer-authority", has_participant="harry", has_input="harry-manager-assigned-1")
    d.when("harry-deassign-manager-1", t("205", "09:30"))
    access(d, "harry-req-complete-order-form-probe-4", "harry", "op-complete-order-form", "probe-4",
           t("205", "09:40"))
    # 5: a designation of Tom and Dick issued after both activations does not join them in this instance
    instance("probe-5", "plan-t2-roles", "206")
    activate(d, "dick", "sc", "probe-5", t("206", "09:00"), "dick-sc-assigned-1", n="probe-5")
    activate(d, "tom", "apm", "probe-5", t("206", "09:05"), "tom-apm-assigned-1", n="probe-5")
    for who, k in (("dick", "sc"), ("tom", "apm")):
        deactivate(d, who, k, "probe-5", t("206", "09:30"), n="probe-5")
    d.ind("probe-ddes-roles", C["dynamic_des"], "dynamic conflicting agents Tom and Dick, conflicting roles plan",
          designates_agent=["tom", "dick"], applies_within="plan-t2-roles")
    issue(d, "probe-issue-ddes-roles", t("228", "08:00"), [EX["probe-ddes-roles"]])
    # 6: once ddes-users is retired, Tom and Dick no longer count as one under the conflicting-users plan
    d.ind("probe-retire-ddes-users", C["retiring"], "retiring act for ddes-users", has_agent="officer",
          realizes="officer-authority", has_input="ddes-users")
    d.when("probe-retire-ddes-users", t("207", "08:00"))
    instance("probe-6", "plan-t2-users", "207")
    activate(d, "dick", "sc", "probe-6", t("207", "09:00"), "dick-sc-assigned-1", n="probe-6")
    access(d, "dick-req-create-requisition-probe-6", "dick", "op-create-requisition", "probe-6", t("207", "09:05"))
    activate(d, "tom", "apm", "probe-6", t("207", "09:10"), "tom-apm-assigned-1", n="probe-6")
    access(d, "tom-req-approve-order-probe-6", "tom", "op-approve-order", "probe-6", t("207", "09:15"))
    for who, k in (("dick", "sc"), ("tom", "apm")):
        deactivate(d, who, k, "probe-6", t("207", "09:30"), n="probe-6")
    # 8: Harry asks at one instant for APM and, through it, Stock Controller, for the two conflicting tasks;
    #    the APM request sorts first and is fulfilled, so the conflicting-tasks DSD refuses the other
    instance("probe-8", "plan-t2-tasks", "208")
    wis = {}
    for task in ("prepare-requisition", "approve-order"):
        wi = wis[task] = f"wi-probe-8-{task}"
        d.ind(wi, C["work_item"], f"work item: {task} in probe-8", wi_for=f"ts-{task}", wi_in="probe-8")
        d.ind(f"issue-{wi}", C["planned_act"], f"workflow engine issues {wi}", has_agent="workflow-engine",
              has_output=wi)
        d.when(f"issue-{wi}", t("208", "09:00"))
    role = activate(d, "harry", "apm", "probe-8", t("208", "09:05"), "harry-apm-assigned-1", n="probe-8")
    activate(d, "harry", "sc", "probe-8", t("208", "09:05"), "harry-apm-assigned-1", n="probe-8", granted=False)
    for k, task in (("apm", "approve-order"), ("sc", "prepare-requisition")):
        d.g.add((EX[f"harry-request-activate-{k}-probe-8"], P["req_act_for"], EX[wis[task]]))
    d.ind("task-probe-8-approve-order", C["task_instance"], "harry's task instance for wi-probe-8-approve-order",
          has_agent="harry", prescribed_by=[wis["approve-order"], "ts-approve-order"], occurrent_part_of="probe-8")
    d.when("task-probe-8-approve-order", t("208", "09:05"), t("208", "09:30"))
    d.g.add((EX[role], P["activated_for"], EX["task-probe-8-approve-order"]))
    deactivate(d, "harry", "apm", "probe-8", t("208", "09:30"), n="probe-8")
    # 7: Manager comes to inherit from Auditor, so Tom, and Dick through their family, are authorized for
    #    APM and Auditor together; Harry lost Manager in probe 4
    issue(d, "probe-issue-inh", t("209", "08:00"), [inheritance(d, "manager", "auditor")])
    d.save(os.path.join(out, "probes.ttl"))


if __name__ == "__main__":
    LABELS = annotate_ttl.load_labels(sys.argv[1])
    out = os.path.join(sys.argv[1], "data")
    us_persons(out); code_review(out); abac(out); rt_policy(out); purchase(out); probes(out)
