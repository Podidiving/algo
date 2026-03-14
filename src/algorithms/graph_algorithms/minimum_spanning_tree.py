"""Minimum spanning tree algorithms.

This module provides Prim's and Kruskal's algorithms for undirected weighted
graphs. Both functions operate on the same ``WeightedEdge`` input and return an
``MSTResult`` describing the minimum spanning forest.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Generic, TypeVar

from algorithms.data_structures import DisjointSet

T = TypeVar("T")


@dataclass(frozen=True, slots=True, order=True)
class WeightedEdge(Generic[T]):
    """Undirected weighted edge between ``u`` and ``v``."""

    weight: float
    u: T
    v: T

    def normalized_endpoints(self) -> tuple[T, T]:
        """Return endpoints in deterministic order for comparisons and output."""

        return (self.u, self.v) if repr(self.u) <= repr(self.v) else (self.v, self.u)


@dataclass(frozen=True, slots=True)
class MSTResult(Generic[T]):
    """Result of a minimum spanning tree or forest computation."""

    total_weight: float
    edges: tuple[WeightedEdge[T], ...]
    component_count: int


def kruskal_mst(
    vertices: list[T] | tuple[T, ...] | set[T],
    edges: list[WeightedEdge[T]] | tuple[WeightedEdge[T], ...],
) -> MSTResult[T]:
    """Return the minimum spanning forest using Kruskal's algorithm.

    The implementation sorts edges by weight and uses :class:`DisjointSet` to
    skip edges that would form cycles.
    """

    vertex_list = list(vertices)
    dsu = DisjointSet(vertex_list)
    chosen_edges: list[WeightedEdge[T]] = []
    total_weight = 0.0

    for edge in sorted(edges, key=_edge_sort_key):
        if edge.u not in dsu or edge.v not in dsu:
            raise KeyError("all edge endpoints must be present in vertices")
        if dsu.connected(edge.u, edge.v):
            continue
        dsu.union(edge.u, edge.v)
        chosen_edges.append(_normalized_edge(edge))
        total_weight += edge.weight

    return MSTResult(
        total_weight=total_weight,
        edges=tuple(chosen_edges),
        component_count=dsu.component_count,
    )


def prim_mst(
    vertices: list[T] | tuple[T, ...] | set[T],
    edges: list[WeightedEdge[T]] | tuple[WeightedEdge[T], ...],
) -> MSTResult[T]:
    """Return the minimum spanning forest using Prim's algorithm.

    If the graph is disconnected, the algorithm runs Prim independently from
    each unvisited vertex and therefore returns a minimum spanning forest.
    """

    vertex_list = list(vertices)
    known_vertices = set(vertex_list)
    adjacency: dict[T, list[tuple[float, str, T, WeightedEdge[T]]]] = {
        vertex: [] for vertex in vertex_list
    }

    for edge in edges:
        if edge.u not in known_vertices or edge.v not in known_vertices:
            raise KeyError("all edge endpoints must be present in vertices")
        normalized = _normalized_edge(edge)
        heap_item_u = (normalized.weight, repr(normalized.u), normalized.v, normalized)
        heap_item_v = (normalized.weight, repr(normalized.v), normalized.u, normalized)
        adjacency[edge.u].append(heap_item_u)
        adjacency[edge.v].append(heap_item_v)

    visited: set[T] = set()
    chosen_edges: list[WeightedEdge[T]] = []
    total_weight = 0.0
    component_count = 0

    for start in vertex_list:
        if start in visited:
            continue
        component_count += 1
        visited.add(start)
        heap = adjacency[start][:]
        heapq.heapify(heap)

        while heap:
            _weight, _neighbor_key, next_vertex, edge = heapq.heappop(heap)
            if next_vertex in visited:
                continue
            visited.add(next_vertex)
            chosen_edges.append(edge)
            total_weight += edge.weight
            for outgoing in adjacency[next_vertex]:
                if outgoing[2] not in visited:
                    heapq.heappush(heap, outgoing)

    return MSTResult(
        total_weight=total_weight,
        edges=tuple(chosen_edges),
        component_count=component_count,
    )


def _normalized_edge(edge: WeightedEdge[T]) -> WeightedEdge[T]:
    first, second = edge.normalized_endpoints()
    return WeightedEdge(weight=edge.weight, u=first, v=second)


def _edge_sort_key(edge: WeightedEdge[T]) -> tuple[float, str, str]:
    normalized = edge.normalized_endpoints()
    return edge.weight, repr(normalized[0]), repr(normalized[1])
