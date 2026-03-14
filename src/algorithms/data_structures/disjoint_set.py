"""Disjoint-set union implementation.

This structure tracks a partition of elements into disjoint components and
supports efficient merging and connectivity checks. It uses path compression
and union by size, giving near-constant amortized time per operation.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T", bound=Hashable)


class DisjointSet(Generic[T]):
    """Union-find data structure with path compression and union by size."""

    def __init__(self, elements: Iterable[T] | None = None) -> None:
        self._parent: dict[T, T] = {}
        self._size: dict[T, int] = {}
        self._component_count = 0

        if elements is not None:
            for element in elements:
                self.add(element)

    def __contains__(self, element: T) -> bool:
        return element in self._parent

    def __len__(self) -> int:
        return len(self._parent)

    def __iter__(self) -> Iterator[T]:
        return iter(self._parent)

    @property
    def component_count(self) -> int:
        """Return the current number of disjoint components."""

        return self._component_count

    def add(self, element: T) -> bool:
        """Create a singleton set for ``element`` if it is not present yet."""

        if element in self._parent:
            return False
        self._parent[element] = element
        self._size[element] = 1
        self._component_count += 1
        return True

    def find(self, element: T) -> T:
        """Return the canonical representative for ``element``."""

        self._ensure_present(element)
        parent = self._parent[element]
        if parent != element:
            self._parent[element] = self.find(parent)
        return self._parent[element]

    def union(self, first: T, second: T) -> T:
        """Merge the sets containing ``first`` and ``second``.

        The representative of the larger component remains the root.
        The resulting representative is returned.
        """

        root_first = self.find(first)
        root_second = self.find(second)
        if root_first == root_second:
            return root_first

        if self._size[root_first] < self._size[root_second]:
            root_first, root_second = root_second, root_first

        self._parent[root_second] = root_first
        self._size[root_first] += self._size[root_second]
        del self._size[root_second]
        self._component_count -= 1
        return root_first

    def connected(self, first: T, second: T) -> bool:
        """Return ``True`` if both elements belong to the same component."""

        return self.find(first) == self.find(second)

    def component_size(self, element: T) -> int:
        """Return the size of the component containing ``element``."""

        return self._size[self.find(element)]

    def groups(self) -> list[set[T]]:
        """Return the current partition as a list of element sets."""

        grouped: dict[T, set[T]] = defaultdict(set)
        for element in self._parent:
            grouped[self.find(element)].add(element)
        return list(grouped.values())

    def validate(self) -> None:
        """Raise ``ValueError`` if parent pointers or component sizes are inconsistent."""

        roots = {
            element for element, parent in self._parent.items() if element == parent
        }
        if len(roots) != self._component_count:
            raise ValueError("component count does not match number of roots")

        computed_sizes: dict[T, int] = defaultdict(int)
        for element in self._parent:
            root = self.find(element)
            if root not in self._parent or self._parent[root] != root:
                raise ValueError("every component must have a valid root")
            computed_sizes[root] += 1

        if set(computed_sizes) != set(self._size):
            raise ValueError("size table keys do not match current roots")

        for root, size in computed_sizes.items():
            if self._size[root] != size:
                raise ValueError("stored component size is incorrect")

    def _ensure_present(self, element: T) -> None:
        if element not in self._parent:
            raise KeyError(element)
