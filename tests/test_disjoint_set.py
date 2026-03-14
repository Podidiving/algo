import pytest

from algorithms.data_structures import DisjointSet


def test_disjoint_set_tracks_components_and_connectivity() -> None:
    dsu = DisjointSet(["a", "b", "c", "d"])

    assert len(dsu) == 4
    assert dsu.component_count == 4
    assert "a" in dsu
    assert "z" not in dsu

    root_ab = dsu.union("a", "b")
    root_abc = dsu.union("b", "c")

    dsu.validate()

    assert root_ab == root_abc
    assert dsu.connected("a", "c")
    assert not dsu.connected("a", "d")
    assert dsu.find("c") == root_ab
    assert dsu.component_size("a") == 3
    assert dsu.component_count == 2
    assert {frozenset(group) for group in dsu.groups()} == {
        frozenset({"a", "b", "c"}),
        frozenset({"d"}),
    }


def test_disjoint_set_add_is_idempotent_and_union_by_size_keeps_larger_root() -> None:
    dsu = DisjointSet[int]()

    assert dsu.add(1) is True
    assert dsu.add(2) is True
    assert dsu.add(3) is True
    assert dsu.add(1) is False

    root_small = dsu.union(1, 2)
    root_large = dsu.union(root_small, 3)

    dsu.validate()

    assert root_large == dsu.find(1)
    assert dsu.find(2) == root_large
    assert dsu.find(3) == root_large
    assert dsu.component_size(2) == 3
    assert dsu.component_count == 1


def test_disjoint_set_raises_for_missing_elements() -> None:
    dsu = DisjointSet([1, 2])

    with pytest.raises(KeyError):
        dsu.find(3)

    with pytest.raises(KeyError):
        dsu.union(1, 3)

    with pytest.raises(KeyError):
        dsu.connected(4, 1)
