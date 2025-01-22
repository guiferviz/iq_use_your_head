from typing import Literal
from pydantic import BaseModel, field_validator, model_validator
import yaml
import math


class Constraint(BaseModel):
    id: str
    description: str | None = None


class Candidate(BaseModel):
    id: int
    meet_constraints: list[str]
    description: str | None = None


class Problem(BaseModel):
    constraints: list[Constraint]
    candidates: list[Candidate]

    @staticmethod
    def from_yaml(file_path: str) -> "Problem":
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        return Problem(**data)

    @field_validator("constraints", mode="before")
    def validate_restrictions(cls, v):
        if isinstance(v, dict):
            validated_restrictions = []
            for key, description in v.items():
                validated_restrictions.append(
                    Constraint(id=key, description=description)
                )
            return validated_restrictions
        return v

    @field_validator("candidates", mode="before")
    def validate_items(cls, v):
        if isinstance(v, dict):
            validated_items = []
            for i, (key, description) in enumerate(v.items()):
                meet_constraints = key.split()
                validated_items.append(
                    Candidate(
                        id=i,
                        meet_constraints=meet_constraints,
                        description=description,
                    )
                )
            return validated_items
        return v

    @model_validator(mode="after")
    def validate_meet_constraints(self):
        constraints = set(i.id for i in self.constraints)
        undefined_constraints = []
        for candidate in self.candidates:
            for i in candidate.meet_constraints:
                if i not in constraints:
                    undefined_constraints.append(i)
        if undefined_constraints:
            raise ValueError(
                f"Candidates meet undefined constraints: {undefined_constraints}"
            )
        return self


class Node:
    def __init__(
        self, constraint_id: str | None = None, candidate_id: int | None = None
    ):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.constraint_id = constraint_id
        self.candidate_id = candidate_id

    def __repr__(self):
        return f"Node({self.constraint_id}, {self.candidate_id})"


def node_in_direction(
    node: Node, direction: Literal["left", "right", "up", "down"]
) -> Node:
    return getattr(node, direction)


def iter_node(
    origin_node: Node,
    direction: Literal["left", "right", "up", "down"],
    skip_first: bool = False,
):
    if not skip_first:
        yield origin_node
    node = origin_node
    while (node := node_in_direction(node, direction)) is not origin_node:
        yield node


def connect_left_right(node_left: Node, node_right: Node):
    node_left.right = node_right
    node_right.left = node_left


def connect_left_right_circularly(nodes: list[Node]):
    for i in range(len(nodes)):
        connect_left_right(nodes[i], nodes[(i + 1) % len(nodes)])


def connect_up_down(node_up: Node, node_down: Node):
    node_up.down = node_down
    node_down.up = node_up


def append_to_column(node: Node, header: dict[str, Node], counts: dict[str, int]):
    assert node.constraint_id
    column = header[node.constraint_id]
    connect_up_down(column.up, node)
    connect_up_down(node, column)
    counts[node.constraint_id] += 1


def create_header(root: Node, constraints: list[Constraint]) -> dict[str, Node]:
    header = {}
    for constraint in constraints:
        header[constraint.id] = Node(constraint.id)
    connect_left_right_circularly([root, *header.values()])
    return header


def min_header_count(root: Node, counts: dict[str, int]) -> Node | None:
    min_count = math.inf
    min_node = None
    for i in iter_node(root, "right", skip_first=True):
        assert i.constraint_id is not None
        node_count = counts[i.constraint_id]
        if node_count < min_count:
            min_count = node_count
            min_node = i
    return min_node


def add_candidate(
    candidate: Candidate, header: dict[str, Node], counts: dict[str, int]
):
    nodes = []
    for constraint in candidate.meet_constraints:
        nodes.append(Node(constraint, candidate.id))
    key2index = {k: i for i, k in enumerate(header.keys())}
    nodes = sorted(nodes, key=lambda x: key2index[x.constraint_id])
    connect_left_right_circularly(nodes)
    for i in nodes:
        append_to_column(i, header, counts)


def cover_left_right(node: Node):
    node.left.right = node.right
    node.right.left = node.left


def uncover_left_right(node: Node):
    node.left.right = node
    node.right.left = node


def cover_up_down(node: Node, counts: dict[str, int]):
    node.up.down = node.down
    node.down.up = node.up
    assert node.constraint_id
    counts[node.constraint_id] -= 1


def uncover_up_down(node: Node, counts: dict[str, int]):
    node.up.down = node
    node.down.up = node
    assert node.constraint_id
    counts[node.constraint_id] += 1


def cover_node(node: Node, header: dict[str, Node], counts: dict[str, int]):
    covered = []
    for i in list(iter_node(node, "right")):
        assert i.constraint_id
        node_col = header[i.constraint_id]
        cover_left_right(node_col)
        for j in list(iter_node(i, "down", skip_first=True)):
            if j.candidate_id is None:
                continue
            for k in list(iter_node(j, "right")):
                cover_up_down(k, counts)
                covered.append(k)
        cover_up_down(i, counts)
        covered.append(i)
    return covered


def uncover_node(
    node: Node, header: dict[str, Node], counts: dict[str, int], covered: list[Node]
):
    for i in list(iter_node(node, "right")):
        assert i.constraint_id
        node_col = header[i.constraint_id]
        uncover_left_right(node_col)
    for i in covered:
        uncover_up_down(i, counts)


class DancingLinks:
    def __init__(self, constraints: list[Constraint], candidates: list[Candidate]):
        self.root = Node()
        self.header = create_header(self.root, constraints)
        self.counts = {k: 0 for k in self.header.keys()}
        for i in candidates:
            self.add_candidate(i)

    def min_header_count(self) -> Node | None:
        return min_header_count(self.root, self.counts)

    def add_candidate(self, candidate: Candidate):
        add_candidate(candidate, self.header, self.counts)

    def solutions(self):
        yield from self._solutions([])

    def _solutions(self, candidates: list[int]):
        min_node = self.min_header_count()
        if min_node is None:
            yield candidates
            return
        elif min_node == 0:
            return
        assert min_node.constraint_id
        for i in iter_node(min_node, "down", skip_first=True):
            covered = cover_node(i, self.header, self.counts)
            assert i.candidate_id is not None
            yield from self._solutions(candidates + [i.candidate_id])
            uncover_node(i, self.header, self.counts, covered)

    def count_solutions(self) -> int:
        return len(list(self.solutions()))
