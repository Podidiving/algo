"""Shared building blocks for linked tree data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Self, TypeVar

T = TypeVar("T", bound="TreeNode[object]")


@dataclass(slots=True)
class TreeNode(Generic[T]):
    """Base node for pointer-based binary trees.

    The class only knows about parent/child links and subtree size.
    Concrete trees can inherit from it and add their own payload, such
    as keys, values, or balancing metadata.
    """

    parent: Self | None = field(default=None, init=False, repr=False)
    left: Self | None = field(default=None, init=False, repr=False)
    right: Self | None = field(default=None, init=False, repr=False)
    size: int = field(default=1, init=False)

    def is_ancestor_of(self, node: Self | None) -> bool:
        """Return ``True`` if this node is on the path from ``node`` to the root."""

        current = node
        while current is not None:
            if current is self:
                return True
            current = current.parent
        return False

    def refresh(self) -> None:
        """Recompute cached subtree metadata from the children."""

        self.size = 1 + self._child_size(self.left) + self._child_size(self.right)

    @staticmethod
    def _child_size(node: Self | None) -> int:
        """Return the size of a child subtree, treating ``None`` as empty."""

        return 0 if node is None else node.size
