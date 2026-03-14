"""Shortest-path algorithms for weighted graphs."""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Generic, TypeVar

from .minimum_spanning_tree import WeightedEdge

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class DijkstraResult(Generic[T]):
    """Result of running Dijkstra's algorithm from a single source."""

    source: T
    distances: dict[T, float]
    previous: dict[T, T | None]

    def distance_to(self, target: T) -> float:
        """Return the shortest distance from the source to ``target``."""

        return self.distances[target]

    def path_to(self, target: T) -> list[T]:
        """Reconstruct the shortest path from the source to ``target``."""

        if target not in self.distances:
            raise KeyError(target)
        if self.distances[target] == float("inf"):
            return []

        path: list[T] = []
        current: T | None = target
        while current is not None:
            path.append(current)
            current = self.previous[current]
        path.reverse()
        return path


@dataclass(frozen=True, slots=True)
class BellmanFordResult(Generic[T]):
    """Result of running Bellman-Ford from a single source."""

    source: T
    distances: dict[T, float]
    previous: dict[T, T | None]

    def distance_to(self, target: T) -> float:
        """Return the shortest distance from the source to ``target``."""

        return self.distances[target]

    def path_to(self, target: T) -> list[T]:
        """Reconstruct the shortest path from the source to ``target``."""

        if target not in self.distances:
            raise KeyError(target)
        if self.distances[target] == float("inf"):
            return []

        path: list[T] = []
        current: T | None = target
        while current is not None:
            path.append(current)
            current = self.previous[current]
        path.reverse()
        return path


@dataclass(frozen=True, slots=True)
class FloydWarshallResult(Generic[T]):
    """All-pairs shortest paths produced by Floyd-Warshall."""

    vertices: tuple[T, ...]
    distances: dict[T, dict[T, float]]
    next_vertex: dict[T, dict[T, T | None]]

    def distance(self, source: T, target: T) -> float:
        """Return the shortest distance from ``source`` to ``target``."""

        return self.distances[source][target]

    def path(self, source: T, target: T) -> list[T]:
        """Reconstruct a shortest path from ``source`` to ``target``."""

        if source not in self.next_vertex or target not in self.next_vertex[source]:
            raise KeyError((source, target))
        if self.next_vertex[source][target] is None:
            return []

        path = [source]
        current = source
        while current != target:
            current = self.next_vertex[current][target]
            if current is None:
                return []
            path.append(current)
        return path


def dijkstra_shortest_paths(
    vertices: list[T] | tuple[T, ...] | set[T],
    edges: list[WeightedEdge[T]] | tuple[WeightedEdge[T], ...],
    source: T,
    *,
    directed: bool = False,
) -> DijkstraResult[T]:
    """Compute shortest paths from ``source`` using Dijkstra's algorithm.

    Edge weights must be non-negative. When ``directed`` is ``False``, every
    edge is treated as undirected and is added in both directions.
    """

    vertex_list = list(vertices)
    known_vertices = set(vertex_list)
    if source not in known_vertices:
        raise KeyError(source)

    adjacency: dict[T, list[tuple[T, float]]] = {vertex: [] for vertex in vertex_list}
    for edge in edges:
        if edge.weight < 0:
            raise ValueError("Dijkstra's algorithm requires non-negative edge weights")
        if edge.u not in known_vertices or edge.v not in known_vertices:
            raise KeyError("all edge endpoints must be present in vertices")
        adjacency[edge.u].append((edge.v, edge.weight))
        if not directed:
            adjacency[edge.v].append((edge.u, edge.weight))

    distances = {vertex: float("inf") for vertex in vertex_list}
    previous = {vertex: None for vertex in vertex_list}
    distances[source] = 0.0

    heap: list[tuple[float, str, T]] = [(0.0, repr(source), source)]
    while heap:
        distance, _, vertex = heapq.heappop(heap)
        if distance != distances[vertex]:
            continue

        for neighbor, weight in adjacency[vertex]:
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = vertex
                heapq.heappush(heap, (candidate, repr(neighbor), neighbor))

    return DijkstraResult(source=source, distances=distances, previous=previous)


def bellman_ford_shortest_paths(
    vertices: list[T] | tuple[T, ...] | set[T],
    edges: list[WeightedEdge[T]] | tuple[WeightedEdge[T], ...],
    source: T,
    *,
    directed: bool = False,
) -> BellmanFordResult[T]:
    """Compute shortest paths from ``source`` using Bellman-Ford.

    Unlike Dijkstra, this algorithm supports negative edge weights, but it
    raises ``ValueError`` if a reachable negative cycle exists.
    """

    vertex_list = list(vertices)
    known_vertices = set(vertex_list)
    if source not in known_vertices:
        raise KeyError(source)

    normalized_edges: list[tuple[T, T, float]] = []
    for edge in edges:
        if edge.u not in known_vertices or edge.v not in known_vertices:
            raise KeyError("all edge endpoints must be present in vertices")
        normalized_edges.append((edge.u, edge.v, edge.weight))
        if not directed:
            normalized_edges.append((edge.v, edge.u, edge.weight))

    distances = {vertex: float("inf") for vertex in vertex_list}
    previous = {vertex: None for vertex in vertex_list}
    distances[source] = 0.0

    for _ in range(len(vertex_list) - 1):
        updated = False
        for u, v, weight in normalized_edges:
            if distances[u] == float("inf"):
                continue
            candidate = distances[u] + weight
            if candidate < distances[v]:
                distances[v] = candidate
                previous[v] = u
                updated = True
        if not updated:
            break

    for u, v, weight in normalized_edges:
        if distances[u] == float("inf"):
            continue
        if distances[u] + weight < distances[v]:
            raise ValueError("graph contains a reachable negative-weight cycle")

    return BellmanFordResult(source=source, distances=distances, previous=previous)


def floyd_warshall_shortest_paths(
    vertices: list[T] | tuple[T, ...] | set[T],
    edges: list[WeightedEdge[T]] | tuple[WeightedEdge[T], ...],
    *,
    directed: bool = False,
) -> FloydWarshallResult[T]:
    """Compute all-pairs shortest paths using Floyd-Warshall.

    The algorithm supports negative weights, but it raises ``ValueError`` when
    a negative cycle exists.
    """

    vertex_list = list(vertices)
    known_vertices = set(vertex_list)
    distances: dict[T, dict[T, float]] = {
        u: {v: float("inf") for v in vertex_list} for u in vertex_list
    }
    next_vertex: dict[T, dict[T, T | None]] = {
        u: {v: None for v in vertex_list} for u in vertex_list
    }

    for vertex in vertex_list:
        distances[vertex][vertex] = 0.0
        next_vertex[vertex][vertex] = vertex

    for edge in edges:
        if edge.u not in known_vertices or edge.v not in known_vertices:
            raise KeyError("all edge endpoints must be present in vertices")
        if edge.weight < distances[edge.u][edge.v]:
            distances[edge.u][edge.v] = edge.weight
            next_vertex[edge.u][edge.v] = edge.v
        if not directed and edge.weight < distances[edge.v][edge.u]:
            distances[edge.v][edge.u] = edge.weight
            next_vertex[edge.v][edge.u] = edge.u

    for middle in vertex_list:
        for source in vertex_list:
            if distances[source][middle] == float("inf"):
                continue
            for target in vertex_list:
                if distances[middle][target] == float("inf"):
                    continue
                candidate = distances[source][middle] + distances[middle][target]
                if candidate < distances[source][target]:
                    distances[source][target] = candidate
                    next_vertex[source][target] = next_vertex[source][middle]

    for vertex in vertex_list:
        if distances[vertex][vertex] < 0:
            raise ValueError("graph contains a negative-weight cycle")

    return FloydWarshallResult(
        vertices=tuple(vertex_list),
        distances=distances,
        next_vertex=next_vertex,
    )
