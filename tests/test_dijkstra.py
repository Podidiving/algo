import pytest

from algorithms import WeightedEdge, dijkstra_shortest_paths


def test_dijkstra_computes_distances_and_paths_in_undirected_graph() -> None:
    vertices = ["A", "B", "C", "D", "E", "F"]
    edges = [
        WeightedEdge(4, "A", "B"),
        WeightedEdge(2, "A", "C"),
        WeightedEdge(1, "C", "B"),
        WeightedEdge(5, "B", "D"),
        WeightedEdge(8, "C", "D"),
        WeightedEdge(10, "C", "E"),
        WeightedEdge(2, "D", "E"),
    ]

    result = dijkstra_shortest_paths(vertices, edges, "A")

    assert result.distance_to("A") == 0
    assert result.distance_to("B") == 3
    assert result.distance_to("D") == 8
    assert result.distance_to("E") == 10
    assert result.distance_to("F") == float("inf")
    assert result.path_to("A") == ["A"]
    assert result.path_to("B") == ["A", "C", "B"]
    assert result.path_to("E") == ["A", "C", "B", "D", "E"]
    assert result.path_to("F") == []


def test_dijkstra_supports_directed_graphs() -> None:
    vertices = [1, 2, 3, 4]
    edges = [
        WeightedEdge(1, 1, 2),
        WeightedEdge(5, 2, 1),
        WeightedEdge(2, 2, 3),
        WeightedEdge(1, 1, 4),
        WeightedEdge(1, 4, 3),
    ]

    result = dijkstra_shortest_paths(vertices, edges, 1, directed=True)

    assert result.distance_to(1) == 0
    assert result.distance_to(2) == 1
    assert result.distance_to(3) == 2
    assert result.path_to(3) == [1, 4, 3]


def test_dijkstra_rejects_invalid_inputs() -> None:
    vertices = ["s", "t"]

    with pytest.raises(KeyError):
        dijkstra_shortest_paths(vertices, [], "x")

    with pytest.raises(KeyError):
        dijkstra_shortest_paths(vertices, [WeightedEdge(1, "s", "x")], "s")

    with pytest.raises(ValueError):
        dijkstra_shortest_paths(vertices, [WeightedEdge(-1, "s", "t")], "s")
