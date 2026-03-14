import pytest

from algorithms.data_structures import Treap


def test_treap_supports_ordered_map_operations() -> None:
    treap = Treap[int, str]()

    treap.insert(5, "e", priority=0.50)
    treap.insert(2, "b", priority=0.20)
    treap.insert(8, "h", priority=0.70)
    treap.insert(1, "a", priority=0.10)
    treap.insert(3, "c", priority=0.40)
    treap.insert(7, "g", priority=0.30)
    treap.insert(2, "beta")

    treap.validate()

    assert list(treap.items()) == [
        (1, "a"),
        (2, "beta"),
        (3, "c"),
        (5, "e"),
        (7, "g"),
        (8, "h"),
    ]
    assert len(treap) == 6
    assert 3 in treap
    assert 4 not in treap
    assert treap.get(7) == "g"
    assert treap.get(4, "missing") == "missing"
    assert treap.min_node().key == 1
    assert treap.max_node().key == 8
    assert treap.lower_bound(4).key == 5
    assert treap.upper_bound(5).key == 7
    assert treap.predecessor(5).key == 3
    assert treap.successor(5).key == 7
    assert treap.rank(5) == 3
    assert treap.kth(3).key == 5


def test_treap_split_merge_and_removal_preserve_invariants() -> None:
    treap = Treap((key, str(key)) for key in [4, 2, 6, 1, 3, 5, 7])

    left, right = treap.split(4)
    left.validate()
    right.validate()

    assert list(left.items()) == [(1, "1"), (2, "2"), (3, "3")]
    assert list(right.items()) == [(4, "4"), (5, "5"), (6, "6"), (7, "7")]

    merged = Treap.merge(left, right)
    merged.validate()

    root = merged.root
    smallest = merged.kth(0)

    assert root is not None
    assert root.is_ancestor_of(smallest)
    assert merged.pop_min() == (1, "1")
    assert merged.pop_max() == (7, "7")
    assert merged.remove(4) == "4"
    assert merged.discard(99) is False

    merged.validate()
    assert list(merged.items()) == [(2, "2"), (3, "3"), (5, "5"), (6, "6")]


def test_treap_raises_for_missing_keys_and_out_of_range_indexes() -> None:
    treap = Treap([(1, "a"), (2, "b")])

    with pytest.raises(KeyError):
        treap.remove(3)

    with pytest.raises(IndexError):
        treap.kth(-1)

    with pytest.raises(IndexError):
        treap.kth(2)
