"""Segment tree implementation.

This structure stores aggregate information for subranges of an array and
supports point updates with logarithmic range queries. The aggregation logic is
user supplied via a binary ``combine`` function and an ``identity`` value.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class SegmentTree(Generic[T]):
    """Array-based segment tree.

    The tree stores values in a complete binary tree over a power-of-two leaf
    count. Internal nodes cache aggregates for their covered ranges, which
    makes the following operations ``O(log n)``:

    - point update by index
    - inclusive-exclusive range query ``query(left, right)``

    ``combine`` must be associative, and ``identity`` must be its neutral
    element, otherwise query results are not well defined.
    """

    def __init__(
        self,
        values: Iterable[T],
        *,
        combine: Callable[[T, T], T],
        identity: T,
    ) -> None:
        self._combine = combine
        self._identity = identity
        self._values = list(values)
        self._length = len(self._values)
        self._size = 1
        while self._size < self._length:
            self._size *= 2

        self._tree = [identity for _ in range(2 * self._size)]
        for index, value in enumerate(self._values):
            self._tree[self._size + index] = value
        for index in range(self._size - 1, 0, -1):
            self._tree[index] = combine(
                self._tree[2 * index], self._tree[2 * index + 1]
            )

    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> Iterator[T]:
        return iter(self._values)

    def __getitem__(self, index: int) -> T:
        """Return the value stored at ``index``."""

        normalized = self._normalize_index(index)
        return self._values[normalized]

    def to_list(self) -> list[T]:
        """Materialize the current leaf values as a Python list."""

        return self._values.copy()

    def update(self, index: int, value: T) -> None:
        """Overwrite the value at ``index`` and rebuild the affected path."""

        normalized = self._normalize_index(index)
        self._values[normalized] = value

        tree_index = self._size + normalized
        self._tree[tree_index] = value
        tree_index //= 2
        while tree_index > 0:
            self._tree[tree_index] = self._combine(
                self._tree[2 * tree_index],
                self._tree[2 * tree_index + 1],
            )
            tree_index //= 2

    def query(self, left: int = 0, right: int | None = None) -> T:
        """Return the aggregate over the half-open interval ``[left, right)``."""

        if right is None:
            right = self._length
        normalized_left, normalized_right = self._normalize_query_bounds(left, right)

        result_left = self._identity
        result_right = self._identity
        normalized_left += self._size
        normalized_right += self._size

        while normalized_left < normalized_right:
            if normalized_left % 2 == 1:
                result_left = self._combine(result_left, self._tree[normalized_left])
                normalized_left += 1
            if normalized_right % 2 == 1:
                normalized_right -= 1
                result_right = self._combine(self._tree[normalized_right], result_right)
            normalized_left //= 2
            normalized_right //= 2

        return self._combine(result_left, result_right)

    def validate(self) -> None:
        """Raise ``ValueError`` if cached internal aggregates are inconsistent."""

        for index in range(self._size, self._size + self._length):
            value_index = index - self._size
            if self._tree[index] != self._values[value_index]:
                raise ValueError("leaf value does not match stored array value")

        for index in range(self._size + self._length, 2 * self._size):
            if self._tree[index] != self._identity:
                raise ValueError("unused leaves must store the identity value")

        for index in range(self._size - 1, 0, -1):
            expected = self._combine(self._tree[2 * index], self._tree[2 * index + 1])
            if self._tree[index] != expected:
                raise ValueError("cached segment aggregate is incorrect")

    def _normalize_index(self, index: int) -> int:
        normalized = index + self._length if index < 0 else index
        if normalized < 0 or normalized >= self._length:
            raise IndexError("segment tree index out of range")
        return normalized

    def _normalize_query_bounds(self, left: int, right: int) -> tuple[int, int]:
        normalized_left = left + self._length if left < 0 else left
        normalized_right = right + self._length if right < 0 else right

        if normalized_left < 0 or normalized_left > self._length:
            raise IndexError("left bound out of range")
        if normalized_right < 0 or normalized_right > self._length:
            raise IndexError("right bound out of range")
        if normalized_left > normalized_right:
            raise ValueError("left bound must not exceed right bound")

        return normalized_left, normalized_right
