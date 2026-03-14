import pytest

from algorithms.data_structures import ImplicitTreap, ImplicitTreapNode


def test_implicit_treap_supports_sequence_operations() -> None:
    seq = ImplicitTreap[str](["b", "d"])

    seq.prepend("a", priority=0.40)
    inserted = seq.insert(2, "c", priority=0.10)
    seq.append("e", priority=0.30)
    seq.set(4, "E")

    seq.validate()

    assert seq.to_list() == ["a", "b", "c", "d", "E"]
    assert seq.get(0) == "a"
    assert seq.get(-1) == "E"
    assert seq.get_node(2) is inserted
    assert seq.index_of(inserted) == 2


def test_implicit_treap_split_merge_and_removal_work_by_index() -> None:
    seq = ImplicitTreap[int]([1, 2, 3, 4, 5])

    left, right = seq.split(3)
    left.validate()
    right.validate()

    assert left.to_list() == [1, 2, 3]
    assert right.to_list() == [4, 5]

    merged = ImplicitTreap.merge(left, right)
    merged.validate()

    assert merged.remove(1) == 2
    assert merged.pop() == 5
    assert merged.pop(0) == 1

    merged.validate()
    assert merged.to_list() == [3, 4]


def test_implicit_treap_raises_for_invalid_indexes_and_foreign_nodes() -> None:
    seq = ImplicitTreap(["a", "b"])
    foreign = ImplicitTreapNode("x")

    with pytest.raises(IndexError):
        seq.get(2)

    with pytest.raises(IndexError):
        seq.remove(-3)

    with pytest.raises(ValueError):
        seq.index_of(foreign)
