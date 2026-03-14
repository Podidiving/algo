"""Basic graph traversal algorithms."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def bfs_traversal(graph: dict[T, list[T]], start: T) -> list[T]:
    """Return vertices in breadth-first-search order from ``start``."""

    _validate_start(graph, start)
    order: list[T] = []
    visited = {start}
    queue = deque([start])

    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor in graph.get(vertex, []):
            if neighbor not in graph:
                raise KeyError(
                    f"unknown vertex referenced in adjacency list: {neighbor!r}"
                )
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs_traversal(graph: dict[T, list[T]], start: T) -> list[T]:
    """Return vertices in depth-first-search preorder from ``start``."""

    _validate_start(graph, start)
    order: list[T] = []
    visited: set[T] = set()
    stack = [start]

    while stack:
        vertex = stack.pop()
        if vertex in visited:
            continue
        visited.add(vertex)
        order.append(vertex)
        neighbors = graph.get(vertex, [])
        for neighbor in reversed(neighbors):
            if neighbor not in graph:
                raise KeyError(
                    f"unknown vertex referenced in adjacency list: {neighbor!r}"
                )
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def connected_components(graph: dict[T, list[T]]) -> list[list[T]]:
    """Return connected components for an undirected graph."""

    for vertex, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor not in graph:
                raise KeyError(
                    f"unknown vertex referenced in adjacency list: {neighbor!r}"
                )

    components: list[list[T]] = []
    visited: set[T] = set()
    for start in graph:
        if start in visited:
            continue
        component = bfs_traversal(graph, start)
        visited.update(component)
        components.append(component)
    return components


def _validate_start(graph: dict[T, Iterable[T]], start: T) -> None:
    if start not in graph:
        raise KeyError(start)
