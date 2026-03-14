import pytest

from algorithms import (
    WeightedEdge,
    bellman_ford_shortest_paths,
    floyd_warshall_shortest_paths,
)


def test_bellman_ford_supports_negative_edges_without_negative_cycles() -> None:
    vertices = ["S", "A", "B", "C", "D"]
    edges = [
        WeightedEdge(4, "S", "A"),
        WeightedEdge(5, "S", "B"),
        WeightedEdge(-2, "A", "C"),
        WeightedEdge(3, "B", "C"),
        WeightedEdge(2, "C", "D"),
    ]

    result = bellman_ford_shortest_paths(vertices, edges, "S", directed=True)

    assert result.distance_to("S") == 0
    assert result.distance_to("C") == 2
    assert result.distance_to("D") == 4
    assert result.path_to("D") == ["S", "A", "C", "D"]


def test_bellman_ford_detects_reachable_negative_cycle() -> None:
    vertices = ["A", "B", "C"]
    edges = [
        WeightedEdge(1, "A", "B"),
        WeightedEdge(-3, "B", "C"),
        WeightedEdge(1, "C", "A"),
    ]

    with pytest.raises(ValueError):
        bellman_ford_shortest_paths(vertices, edges, "A", directed=True)


def test_floyd_warshall_computes_all_pairs_distances_and_paths() -> None:
    vertices = ["A", "B", "C", "D"]
    edges = [
        WeightedEdge(3, "A", "B"),
        WeightedEdge(1, "B", "C"),
        WeightedEdge(7, "A", "C"),
        WeightedEdge(2, "C", "D"),
        WeightedEdge(10, "A", "D"),
    ]

    result = floyd_warshall_shortest_paths(vertices, edges, directed=True)

    assert result.distance("A", "A") == 0
    assert result.distance("A", "C") == 4
    assert result.distance("A", "D") == 6
    assert result.path("A", "D") == ["A", "B", "C", "D"]
    assert result.path("D", "A") == []


def test_floyd_warshall_detects_negative_cycles() -> None:
    vertices = [1, 2, 3]
    edges = [
        WeightedEdge(1, 1, 2),
        WeightedEdge(-4, 2, 3),
        WeightedEdge(1, 3, 1),
    ]

    with pytest.raises(ValueError):
        floyd_warshall_shortest_paths(vertices, edges, directed=True)
