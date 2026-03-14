"""Least common ancestor queries with binary lifting."""

from __future__ import annotations

from collections import deque
from typing import TypeVar

T = TypeVar("T")


class LowestCommonAncestor:
    """Preprocess a rooted tree for ``O(log n)`` LCA queries."""

    def __init__(self, tree: dict[T, list[T]], root: T) -> None:
        if root not in tree:
            raise KeyError(root)

        self._tree = tree
        self._root = root
        self._nodes = list(tree)
        self._depth: dict[T, int] = {}
        self._parent: dict[T, T | None] = {}
        self._up: list[dict[T, T | None]] = []

        self._build()

    def lca(self, first: T, second: T) -> T:
        """Return the lowest common ancestor of ``first`` and ``second``."""

        self._ensure_known(first)
        self._ensure_known(second)

        if self._depth[first] < self._depth[second]:
            first, second = second, first

        first = self._lift(first, self._depth[first] - self._depth[second])
        if first == second:
            return first

        for level in range(len(self._up) - 1, -1, -1):
            up_first = self._up[level][first]
            up_second = self._up[level][second]
            if up_first != up_second:
                if up_first is None or up_second is None:
                    continue
                first = up_first
                second = up_second

        parent = self._parent[first]
        if parent is None:
            raise RuntimeError("tree structure is corrupted")
        return parent

    def distance(self, first: T, second: T) -> int:
        """Return the number of edges between ``first`` and ``second``."""

        ancestor = self.lca(first, second)
        return self._depth[first] + self._depth[second] - 2 * self._depth[ancestor]

    def kth_ancestor(self, node: T, k: int) -> T | None:
        """Return the ``k``-th ancestor of ``node`` or ``None`` above the root."""

        self._ensure_known(node)
        if k < 0:
            raise ValueError("k must be non-negative")
        return self._lift(node, k)

    def _build(self) -> None:
        for node, neighbors in self._tree.items():
            for neighbor in neighbors:
                if neighbor not in self._tree:
                    raise KeyError(
                        f"unknown node referenced in adjacency list: {neighbor!r}"
                    )

        queue = deque([self._root])
        self._depth[self._root] = 0
        self._parent[self._root] = None
        order: list[T] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self._tree[node]:
                if neighbor == self._parent.get(node):
                    continue
                if neighbor in self._depth:
                    raise ValueError(
                        "input graph must be a tree rooted at the given root"
                    )
                self._depth[neighbor] = self._depth[node] + 1
                self._parent[neighbor] = node
                queue.append(neighbor)

        if len(order) != len(self._tree):
            raise ValueError("input graph must be connected")

        max_log = max(1, len(self._tree).bit_length())
        self._up = [{node: self._parent[node] for node in self._nodes}]
        for level in range(1, max_log):
            previous = self._up[level - 1]
            current: dict[T, T | None] = {}
            for node in self._nodes:
                parent = previous[node]
                current[node] = None if parent is None else previous[parent]
            self._up.append(current)

    def _lift(self, node: T, distance: int) -> T | None:
        current: T | None = node
        bit = 0
        while distance > 0 and current is not None:
            if distance & 1:
                current = self._up[bit][current]
            distance >>= 1
            bit += 1
        return current

    def _ensure_known(self, node: T) -> None:
        if node not in self._depth:
            raise KeyError(node)
