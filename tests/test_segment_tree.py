import operator

import pytest

from algorithms.data_structures import SegmentTree


def test_segment_tree_supports_range_sum_queries_and_updates() -> None:
    tree = SegmentTree([2, 1, 3, 4, 5], combine=operator.add, identity=0)

    tree.validate()

    assert len(tree) == 5
    assert list(tree) == [2, 1, 3, 4, 5]
    assert tree.to_list() == [2, 1, 3, 4, 5]
    assert tree[0] == 2
    assert tree[-1] == 5
    assert tree.query() == 15
    assert tree.query(1, 4) == 8
    assert tree.query(2, 2) == 0

    tree.update(3, 10)
    tree.validate()

    assert tree.to_list() == [2, 1, 3, 10, 5]
    assert tree.query() == 21
    assert tree.query(2, 5) == 18


def test_segment_tree_supports_other_associative_operations() -> None:
    tree = SegmentTree([7, 2, 9, 1, 5], combine=min, identity=float("inf"))

    tree.validate()

    assert tree.query() == 1
    assert tree.query(0, 3) == 2
    assert tree.query(-3, -1) == 1

    tree.update(-2, 8)
    tree.validate()

    assert tree.query() == 2
    assert tree.query(2, 5) == 5


def test_segment_tree_raises_for_invalid_indexes_and_ranges() -> None:
    tree = SegmentTree([1, 2, 3], combine=operator.add, identity=0)

    with pytest.raises(IndexError):
        _ = tree[3]

    with pytest.raises(IndexError):
        tree.update(-4, 10)

    with pytest.raises(IndexError):
        tree.query(0, 4)

    with pytest.raises(ValueError):
        tree.query(2, 1)
