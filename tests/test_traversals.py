import pytest

from algorithms import bfs_traversal, connected_components, dfs_traversal


def test_bfs_and_dfs_traverse_graph_from_start_vertex() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B"],
        "F": ["C"],
    }

    assert bfs_traversal(graph, "A") == ["A", "B", "C", "D", "E", "F"]
    assert dfs_traversal(graph, "A") == ["A", "B", "D", "E", "C", "F"]


def test_connected_components_groups_undirected_graph() -> None:
    graph = {
        1: [2],
        2: [1, 3],
        3: [2],
        4: [5],
        5: [4],
        6: [],
    }

    assert connected_components(graph) == [[1, 2, 3], [4, 5], [6]]


def test_traversals_reject_unknown_vertices() -> None:
    graph = {"A": ["B"], "B": ["A", "C"]}

    with pytest.raises(KeyError):
        bfs_traversal(graph, "Z")

    with pytest.raises(KeyError):
        dfs_traversal(graph, "A")
