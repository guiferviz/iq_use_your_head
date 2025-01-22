from use_your_head.dancing_links import (
    Candidate,
    Problem,
    Constraint,
    DancingLinks,
    add_candidate,
    append_to_column,
    cover_node,
    cover_left_right,
    cover_up_down,
    min_header_count,
    Node,
    iter_node,
    connect_left_right,
    connect_up_down,
    create_header,
    connect_left_right_circularly,
    uncover_node,
    uncover_left_right,
    uncover_up_down,
)


def test_connect_left_right():
    c1 = Node("C1")
    c2 = Node("C2")
    connect_left_right(c1, c2)
    assert c1.right is c2
    assert c2.left is c1
    # Other connections left unchanged.
    assert c1.left is c1
    assert c1.up is c1
    assert c1.down is c1
    assert c2.right is c2
    assert c2.up is c2
    assert c2.down is c2


def test_connect_left_right_circularly():
    nodes = [c1, c2, c3] = [Node("C1"), Node("C2"), Node("C3")]
    connect_left_right_circularly(nodes)
    assert c1.left is c3
    assert c1.right is c2
    assert c2.left is c1
    assert c2.right is c3
    assert c3.left is c2
    assert c3.right is c1
    # Other connections left unchanged.
    assert c1.up is c1
    assert c1.down is c1
    assert c2.up is c2
    assert c2.down is c2
    assert c3.up is c3
    assert c3.down is c3


def test_connect_up_down():
    c1 = Node("C1")
    c2 = Node("C2")
    connect_up_down(c1, c2)
    assert c1.down is c2
    assert c2.up is c1
    # Other connections left unchanged.
    assert c1.left is c1
    assert c1.right is c1
    assert c1.up is c1
    assert c2.left is c2
    assert c2.right is c2
    assert c2.down is c2


def test_append_to_column():
    c1, c2, c3 = Node("C1"), Node("C1", 0), Node("C1", 1)
    header = {"C1": c1}
    counts = {"C1": 0}
    append_to_column(c2, header, counts)
    assert counts == {"C1": 1}
    assert c1.up is c2
    assert c1.down is c2
    assert c2.up is c1
    assert c2.down is c1
    # Other connections left unchanged.
    assert c1.right is c1
    assert c1.left is c1
    assert c2.right is c2
    assert c2.left is c2
    # Add another.
    append_to_column(c3, header, counts)
    assert counts == {"C1": 2}
    assert c1.up is c3
    assert c1.down is c2
    assert c2.up is c1
    assert c2.down is c3
    assert c3.up is c2
    assert c3.down is c1
    # Other connections left unchanged.
    assert c1.right is c1
    assert c1.left is c1
    assert c2.right is c2
    assert c2.left is c2
    assert c3.right is c3
    assert c3.left is c3


def test_add_candidate():
    candidate0 = Candidate(id=0, meet_constraints=["C", "A", "D"])
    candidate1 = Candidate(id=1, meet_constraints=["D", "A"])
    constraints = ["A", "B", "C", "D"]
    header = {i: Node(i) for i in constraints}
    counts = {i: 0 for i in constraints}
    add_candidate(candidate0, header, counts)
    add_candidate(candidate1, header, counts)
    # Test columns.
    cols = {}
    for constraint in constraints:
        cols[constraint] = [
            (i.constraint_id, i.candidate_id)
            for i in iter_node(header[constraint], "down", skip_first=True)
        ]
    assert cols["A"] == [
        ("A", 0),
        ("A", 1),
    ]
    assert cols["B"] == []
    assert cols["C"] == [("C", 0)]
    assert cols["D"] == [("D", 0), ("D", 1)]
    # Test rows.
    rows = {}
    for node in iter_node(header["A"], "down", skip_first=True):
        rows[node.candidate_id] = [
            (i.constraint_id, i.candidate_id) for i in iter_node(node, "right")
        ]
    assert rows[0] == [
        ("A", 0),
        ("C", 0),
        ("D", 0),
    ]
    assert rows[1] == [
        ("A", 1),
        ("D", 1),
    ]
    # Counts updated.
    assert counts == {"A": 2, "B": 0, "C": 1, "D": 2}


def test_iter_node():
    nodes = [c1, _, _] = [Node("C1"), Node("C2"), Node("C3")]
    connect_left_right_circularly(nodes)
    assert [i.constraint_id for i in iter_node(c1, "right")] == ["C1", "C2", "C3"]
    assert [i.constraint_id for i in iter_node(c1, "left")] == ["C1", "C3", "C2"]
    assert [i.constraint_id for i in iter_node(c1, "left", skip_first=True)] == [
        "C3",
        "C2",
    ]
    assert [i.constraint_id for i in iter_node(c1, "up")] == ["C1"]
    assert [i.constraint_id for i in iter_node(c1, "down", skip_first=True)] == []


def test_create_header():
    root = Node()
    constraints = [Constraint(id="C1"), Constraint(id="C2")]
    header = create_header(root, constraints)
    assert [i.constraint_id for i in iter_node(root, "right", skip_first=True)] == [
        i.constraint_id for i in header.values()
    ]
    assert [i.constraint_id for i in iter_node(root, "left", skip_first=True)] == [
        i.constraint_id for i in reversed(header.values())
    ]


def test_min_header_count():
    nodes = [root, _, _, c3] = [Node(), Node("C1"), Node("C2"), Node("C3")]
    connect_left_right_circularly(nodes)
    counts = {"C1": 3, "C2": 2, "C3": 1}
    assert min_header_count(root, counts) is c3


def test_min_header_count_empty():
    root = Node()
    counts = {"C1": 1}
    assert min_header_count(root, counts) is None


def test_cover_uncover_left_right():
    nodes = c1, c2, c3 = [Node("C1"), Node("C2"), Node("C3")]
    connect_left_right_circularly(nodes)
    cover_left_right(c2)
    assert list(iter_node(c1, "right")) == [c1, c3]
    uncover_left_right(c2)
    assert list(iter_node(c1, "right")) == [c1, c2, c3]


def test_cover_uncover_up_down():
    c, c0, c1 = Node("C"), Node("C", 0), Node("C", 1)
    header = {"C": c}
    counts = {"C": 0}
    append_to_column(c0, header, counts)
    append_to_column(c1, header, counts)
    assert counts == {"C": 2}
    cover_up_down(c0, counts)
    assert counts == {"C": 1}
    assert list(iter_node(c, "down")) == [c, c1]
    uncover_up_down(c0, counts)
    assert counts == {"C": 2}
    assert list(iter_node(c, "down")) == [c, c0, c1]


def test_cover_uncover_node():
    dlx = DancingLinks(
        constraints=[
            Constraint(id="A"),
            Constraint(id="B"),
            Constraint(id="C"),
        ],
        candidates=[
            Candidate(id=0, meet_constraints=["A", "B"]),
            Candidate(id=1, meet_constraints=["B", "C"]),
            Candidate(id=2, meet_constraints=["C"]),
            Candidate(id=3, meet_constraints=["A", "B", "C"]),
        ],
    )
    node = dlx.header["A"].down
    covered = cover_node(node, dlx.header, dlx.counts)
    assert dlx.counts == {"A": 0, "B": 0, "C": 1}
    assert [i.constraint_id for i in iter_node(dlx.root, "right", skip_first=True)] == [
        "C"
    ]
    assert [
        (i.constraint_id, i.candidate_id)
        for i in iter_node(dlx.header["C"], "down", skip_first=True)
    ] == [("C", 2)]
    uncover_node(node, dlx.header, dlx.counts, covered)
    assert dlx.counts == {"A": 2, "B": 3, "C": 3}
    assert [i.constraint_id for i in iter_node(dlx.root, "right", skip_first=True)] == [
        "A",
        "B",
        "C",
    ]
    assert [
        (i.constraint_id, i.candidate_id)
        for i in iter_node(dlx.header["A"], "down", skip_first=True)
    ] == [("A", 0), ("A", 3)]
    assert [
        (i.constraint_id, i.candidate_id)
        for i in iter_node(dlx.header["B"], "down", skip_first=True)
    ] == [("B", 0), ("B", 1), ("B", 3)]
    assert [
        (i.constraint_id, i.candidate_id)
        for i in iter_node(dlx.header["C"], "down", skip_first=True)
    ] == [("C", 1), ("C", 2), ("C", 3)]


def test_count_solutions():
    dlx = DancingLinks(
        constraints=[
            Constraint(id="A"),
            Constraint(id="B"),
        ],
        candidates=[
            Candidate(id=0, meet_constraints=["A", "B"]),
            Candidate(id=1, meet_constraints=["A"]),
            Candidate(id=2, meet_constraints=["B"]),
        ],
    )
    assert dlx.count_solutions() == 2


def test_solutions_exact_cover_2x2_4sol():
    problem = Problem.from_yaml("./tests/fixtures/exact_cover_2x2_4sol.yaml")
    dlx = DancingLinks(problem.constraints, problem.candidates)
    solutions = list(dlx.solutions())
    assert solutions == [
        [0, 7],
        [1, 6],
        [3, 5],
        [4, 2],
    ]


def test_solutions_exact_cover_2x2_16sol():
    problem = Problem.from_yaml("./tests/fixtures/exact_cover_2x2_16sol.yaml")
    dlx = DancingLinks(problem.constraints, problem.candidates)
    assert dlx.count_solutions() == 16
