"""Range minimum query implementation.

The RMQ structure answers minimum queries over subranges of an array. This
implementation is backed by the generic :class:`algorithms.SegmentTree`, so it
supports logarithmic point updates and logarithmic range minimum queries.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from algorithms.data_structures import SegmentTree


class RMQ:
    """Range minimum query structure backed by a segment tree.

    Each segment stores ``(value, index)`` pairs. The combine function keeps
    the smaller value, and breaks ties by smaller index, so queries are stable
    and can report both the minimum value and where it occurs.
    """

    def __init__(self, values: Iterable[int]) -> None:
        self._values = list(values)
        self._tree = SegmentTree(
            ((value, index) for index, value in enumerate(self._values)),
            combine=min,
            identity=(float("inf"), -1),
        )

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[int]:
        return iter(self._values)

    def __getitem__(self, index: int) -> int:
        """Return the value stored at ``index``."""

        return self._values[index]

    def to_list(self) -> list[int]:
        """Materialize the tracked values as a Python list."""

        return self._values.copy()

    def update(self, index: int, value: int) -> None:
        """Overwrite the value at ``index``."""

        normalized = self._normalize_index(index)
        self._values[normalized] = value
        self._tree.update(normalized, (value, normalized))

    def query(self, left: int = 0, right: int | None = None) -> int:
        """Return the minimum value over the half-open interval ``[left, right)``."""

        return self.query_with_index(left, right)[1]

    def argmin(self, left: int = 0, right: int | None = None) -> int:
        """Return the index of the minimum value over ``[left, right)``."""

        return self.query_with_index(left, right)[0]

    def query_with_index(
        self, left: int = 0, right: int | None = None
    ) -> tuple[int, int]:
        """Return ``(index, value)`` for the minimum over ``[left, right)``."""

        if len(self) == 0:
            raise ValueError("cannot query an empty RMQ")

        index_value = self._tree.query(left, right)
        if index_value[1] == -1:
            raise ValueError("range minimum query requires a non-empty interval")
        return index_value[1], index_value[0]

    def validate(self) -> None:
        """Raise ``ValueError`` if the underlying segment tree is inconsistent."""

        if len(self._values) != len(self._tree):
            raise ValueError("RMQ value array and segment tree length differ")
        for index, value in enumerate(self._values):
            if self._tree[index] != (value, index):
                raise ValueError("RMQ leaf state does not match the stored values")
        self._tree.validate()

    def _normalize_index(self, index: int) -> int:
        normalized = index + len(self) if index < 0 else index
        if normalized < 0 or normalized >= len(self):
            raise IndexError("rmq index out of range")
        return normalized
