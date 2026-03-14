import pytest

from algorithms import LowestCommonAncestor


def test_lca_queries_and_distances_work() -> None:
    tree = {
        1: [2, 3],
        2: [1, 4, 5],
        3: [1, 6, 7],
        4: [2],
        5: [2],
        6: [3],
        7: [3, 8],
        8: [7],
    }
    lca = LowestCommonAncestor(tree, 1)

    assert lca.lca(4, 5) == 2
    assert lca.lca(4, 6) == 1
    assert lca.lca(6, 8) == 3
    assert lca.distance(4, 8) == 5
    assert lca.kth_ancestor(8, 1) == 7
    assert lca.kth_ancestor(8, 3) == 1
    assert lca.kth_ancestor(8, 4) is None


def test_lca_rejects_invalid_queries_and_non_tree_input() -> None:
    tree = {1: [2], 2: [1, 3], 3: [2]}
    lca = LowestCommonAncestor(tree, 1)

    with pytest.raises(KeyError):
        lca.lca(1, 99)

    with pytest.raises(ValueError):
        lca.kth_ancestor(2, -1)

    cyclic = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
    with pytest.raises(ValueError):
        LowestCommonAncestor(cyclic, 1)
