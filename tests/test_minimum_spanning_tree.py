import pytest

from algorithms import WeightedEdge, kruskal_mst, prim_mst


def test_prim_and_kruskal_agree_on_connected_graph() -> None:
    vertices = ["A", "B", "C", "D", "E"]
    edges = [
        WeightedEdge(1, "A", "B"),
        WeightedEdge(4, "A", "C"),
        WeightedEdge(3, "B", "C"),
        WeightedEdge(2, "B", "D"),
        WeightedEdge(5, "C", "D"),
        WeightedEdge(7, "C", "E"),
        WeightedEdge(6, "D", "E"),
        WeightedEdge(8, "A", "E"),
    ]

    prim_result = prim_mst(vertices, edges)
    kruskal_result = kruskal_mst(vertices, edges)

    assert prim_result.total_weight == 12
    assert prim_result.total_weight == kruskal_result.total_weight
    assert prim_result.component_count == 1
    assert kruskal_result.component_count == 1
    assert (
        _edge_set(prim_result.edges)
        == _edge_set(kruskal_result.edges)
        == {
            ("A", "B", 1),
            ("B", "C", 3),
            ("B", "D", 2),
            ("D", "E", 6),
        }
    )


def test_prim_and_kruskal_return_minimum_spanning_forest_for_disconnected_graph() -> (
    None
):
    vertices = [1, 2, 3, 4, 5]
    edges = [
        WeightedEdge(1, 1, 2),
        WeightedEdge(5, 1, 3),
        WeightedEdge(2, 2, 3),
        WeightedEdge(4, 4, 5),
    ]

    prim_result = prim_mst(vertices, edges)
    kruskal_result = kruskal_mst(vertices, edges)

    assert prim_result.total_weight == 7
    assert kruskal_result.total_weight == 7
    assert prim_result.component_count == 2
    assert kruskal_result.component_count == 2
    assert (
        _edge_set(prim_result.edges)
        == _edge_set(kruskal_result.edges)
        == {
            (1, 2, 1),
            (2, 3, 2),
            (4, 5, 4),
        }
    )


def test_mst_algorithms_reject_edges_with_unknown_vertices() -> None:
    vertices = ["x", "y"]
    edges = [WeightedEdge(1, "x", "z")]

    with pytest.raises(KeyError):
        prim_mst(vertices, edges)

    with pytest.raises(KeyError):
        kruskal_mst(vertices, edges)


def _edge_set(
    edges: tuple[WeightedEdge[object], ...],
) -> set[tuple[object, object, float]]:
    return {(edge.u, edge.v, edge.weight) for edge in edges}
