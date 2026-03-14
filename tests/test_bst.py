import pytest

from algorithms.data_structures import BST


def test_bst_supports_search_order_statistics_and_updates() -> None:
    bst = BST[int, str]()

    for key, value in [(5, "e"), (2, "b"), (8, "h"), (1, "a"), (3, "c"), (7, "g")]:
        bst.insert(key, value)
    bst.insert(2, "beta")

    bst.validate()

    assert list(bst.items()) == [
        (1, "a"),
        (2, "beta"),
        (3, "c"),
        (5, "e"),
        (7, "g"),
        (8, "h"),
    ]
    assert len(bst) == 6
    assert 7 in bst
    assert 9 not in bst
    assert bst.get(8) == "h"
    assert bst.get(100, "missing") == "missing"
    assert bst.min_node().key == 1
    assert bst.max_node().key == 8
    assert bst.lower_bound(4).key == 5
    assert bst.upper_bound(5).key == 7
    assert bst.predecessor(5).key == 3
    assert bst.successor(5).key == 7
    assert bst.rank(5) == 3
    assert bst.kth(4).key == 7


def test_bst_removal_handles_leaf_single_child_and_two_children() -> None:
    bst = BST((key, str(key)) for key in [5, 2, 8, 1, 3, 7, 9, 6])

    assert bst.remove(1) == "1"
    bst.validate()

    assert bst.remove(7) == "7"
    bst.validate()

    assert bst.remove(5) == "5"
    bst.validate()

    assert bst.pop_min() == (2, "2")
    assert bst.pop_max() == (9, "9")
    assert bst.discard(100) is False

    bst.validate()
    assert list(bst.items()) == [(3, "3"), (6, "6"), (8, "8")]


def test_bst_raises_for_missing_keys_and_out_of_range_indexes() -> None:
    bst = BST([(1, "a"), (2, "b")])

    with pytest.raises(KeyError):
        bst.remove(5)

    with pytest.raises(IndexError):
        bst.kth(-1)

    with pytest.raises(IndexError):
        bst.kth(2)
