import pytest

from algorithms.data_structures import RedBlackTree


def test_red_black_tree_supports_ordered_map_operations() -> None:
    tree = RedBlackTree[int, str]()

    for key, value in [(5, "e"), (2, "b"), (8, "h"), (1, "a"), (3, "c"), (7, "g")]:
        tree.insert(key, value)
    tree.insert(2, "beta")

    tree.validate()

    assert list(tree.items()) == [
        (1, "a"),
        (2, "beta"),
        (3, "c"),
        (5, "e"),
        (7, "g"),
        (8, "h"),
    ]
    assert len(tree) == 6
    assert 7 in tree
    assert 9 not in tree
    assert tree.get(8) == "h"
    assert tree.get(100, "missing") == "missing"
    assert tree.min_node().key == 1
    assert tree.max_node().key == 8
    assert tree.lower_bound(4).key == 5
    assert tree.upper_bound(5).key == 7
    assert tree.predecessor(5).key == 3
    assert tree.successor(5).key == 7
    assert tree.rank(5) == 3
    assert tree.kth(4).key == 7


def test_red_black_tree_rebalances_after_insertions_and_deletions() -> None:
    tree = RedBlackTree(
        (key, str(key)) for key in [10, 20, 30, 40, 50, 25, 5, 35, 45, 1, 15]
    )

    tree.validate()

    assert tree.remove(40) == "40"
    assert tree.remove(10) == "10"
    assert tree.pop_min() == (1, "1")
    assert tree.pop_max() == (50, "50")
    assert tree.discard(999) is False

    tree.validate()
    assert list(tree.items()) == [
        (5, "5"),
        (15, "15"),
        (20, "20"),
        (25, "25"),
        (30, "30"),
        (35, "35"),
        (45, "45"),
    ]

    root = tree.root
    smallest = tree.kth(0)
    assert root is not None
    assert root.color == "black"
    assert root.is_ancestor_of(smallest)


def test_red_black_tree_raises_for_missing_keys_and_out_of_range_indexes() -> None:
    tree = RedBlackTree([(1, "a"), (2, "b")])

    with pytest.raises(KeyError):
        tree.remove(5)

    with pytest.raises(IndexError):
        tree.kth(-1)

    with pytest.raises(IndexError):
        tree.kth(2)
