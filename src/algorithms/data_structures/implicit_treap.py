"""Implicit treap implementation.

An implicit treap stores a sequence rather than explicit keys. Element position
is derived from subtree sizes, so split and merge happen by index instead of by
comparing keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Generator, Generic, Iterable, Iterator, TypeVar

from .tree import TreeNode

T = TypeVar("T")


@dataclass(slots=True, eq=False)
class ImplicitTreapNode(TreeNode["ImplicitTreapNode[T]"], Generic[T]):
    """A node in an implicit treap sequence."""

    value: T
    priority: float = field(default_factory=random.random)

    def __repr__(self) -> str:
        return (
            f"ImplicitTreapNode(value={self.value!r}, "
            f"priority={self.priority:.6f}, size={self.size})"
        )


class ImplicitTreap(Generic[T]):
    """Randomized balanced sequence container.

    Instead of storing explicit keys, this structure uses in-order position as
    the logical index. That makes it a good fit for sequence editing:

    - insert at index
    - remove at index
    - split at index
    - merge sequences
    - random-access by index

    Average complexity is ``O(log n)`` for these operations.
    """

    def __init__(self, values: Iterable[T] | None = None) -> None:
        self.root: ImplicitTreapNode[T] | None = None
        if values is not None:
            for value in values:
                self.append(value)

    def __len__(self) -> int:
        return 0 if self.root is None else self.root.size

    def __bool__(self) -> bool:
        return self.root is not None

    def __iter__(self) -> Iterator[T]:
        for node in self.inorder():
            yield node.value

    def values(self) -> Iterator[T]:
        """Iterate over sequence values in order."""

        return iter(self)

    def clear(self) -> None:
        """Remove all elements from the sequence."""

        self.root = None

    def append(
        self, value: T, *, priority: float | None = None
    ) -> ImplicitTreapNode[T]:
        """Append a value to the end of the sequence."""

        return self.insert(len(self), value, priority=priority)

    def prepend(
        self, value: T, *, priority: float | None = None
    ) -> ImplicitTreapNode[T]:
        """Insert a value at the front of the sequence."""

        return self.insert(0, value, priority=priority)

    def insert(
        self, index: int, value: T, *, priority: float | None = None
    ) -> ImplicitTreapNode[T]:
        """Insert ``value`` before ``index`` and return the created node."""

        normalized = self._normalize_insert_index(index)
        left, right = self._split(self.root, normalized)
        node = ImplicitTreapNode(value=value)
        if priority is not None:
            node.priority = priority
        self.root = self._merge_roots(self._merge_roots(left, node), right)
        return node

    def get_node(self, index: int) -> ImplicitTreapNode[T]:
        """Return the node at zero-based position ``index``."""

        normalized = self._normalize_index(index)
        current = self.root
        while current is not None:
            left_size = current._child_size(current.left)
            if normalized < left_size:
                current = current.left
            elif normalized == left_size:
                return current
            else:
                normalized -= left_size + 1
                current = current.right
        raise RuntimeError("corrupted implicit treap structure")

    def get(self, index: int) -> T:
        """Return the value at ``index``."""

        return self.get_node(index).value

    def set(self, index: int, value: T) -> None:
        """Overwrite the value at ``index``."""

        self.get_node(index).value = value

    def index_of(self, node: ImplicitTreapNode[T]) -> int:
        """Return the current position of ``node`` inside the treap."""

        if self.root is None or not self.root.is_ancestor_of(node):
            raise ValueError("node does not belong to this treap")

        index = node._child_size(node.left)
        current = node
        while current.parent is not None:
            if current.parent.right is current:
                index += 1 + current.parent._child_size(current.parent.left)
            current = current.parent
        return index

    def remove(self, index: int) -> T:
        """Remove and return the value at ``index``."""

        normalized = self._normalize_index(index)
        left, middle = self._split(self.root, normalized)
        target, right = self._split(middle, 1)
        if target is None:
            raise RuntimeError("corrupted implicit treap structure")
        value = target.value
        self.root = self._merge_roots(left, right)
        target.parent = None
        target.left = None
        target.right = None
        target.refresh()
        return value

    def pop(self, index: int = -1) -> T:
        """Remove and return the element at ``index``. Defaults to the last item."""

        return self.remove(index)

    def split(self, index: int) -> tuple["ImplicitTreap[T]", "ImplicitTreap[T]"]:
        """Split into ``([:index], [index:])`` treaps."""

        normalized = self._normalize_split_index(index)
        left_root, right_root = self._split(self.root, normalized)
        left = self.__class__()
        right = self.__class__()
        left.root = left_root
        right.root = right_root
        self.root = None
        return left, right

    @classmethod
    def merge(
        cls, left: "ImplicitTreap[T]", right: "ImplicitTreap[T]"
    ) -> "ImplicitTreap[T]":
        """Concatenate two implicit treaps."""

        merged = cls()
        merged.root = cls._merge_roots(left.root, right.root)
        left.root = None
        right.root = None
        return merged

    def inorder(self) -> Iterator[ImplicitTreapNode[T]]:
        """Yield nodes in sequence order."""

        yield from self._inorder(self.root)

    def to_list(self) -> list[T]:
        """Materialize the sequence as a Python list."""

        return list(self)

    def validate(self) -> None:
        """Raise ``ValueError`` if heap, sizes, or parent links are broken."""

        def walk(node: ImplicitTreapNode[T] | None) -> int:
            if node is None:
                return 0
            if node.left is not None:
                if node.left.parent is not node:
                    raise ValueError("broken parent pointer")
                if node.left.priority < node.priority:
                    raise ValueError("heap invariant violated on left child")
            if node.right is not None:
                if node.right.parent is not node:
                    raise ValueError("broken parent pointer")
                if node.right.priority < node.priority:
                    raise ValueError("heap invariant violated on right child")
            left_size = walk(node.left)
            right_size = walk(node.right)
            expected = 1 + left_size + right_size
            if node.size != expected:
                raise ValueError("cached subtree size is incorrect")
            return expected

        walk(self.root)

    @classmethod
    def _split(
        cls, root: ImplicitTreapNode[T] | None, index: int
    ) -> tuple[ImplicitTreapNode[T] | None, ImplicitTreapNode[T] | None]:
        if root is None:
            return None, None

        left_size = root._child_size(root.left)
        if index <= left_size:
            left, root.left = cls._split(root.left, index)
            if root.left is not None:
                root.left.parent = root
            root.parent = None
            root.refresh()
            return left, root

        root.right, right = cls._split(root.right, index - left_size - 1)
        if root.right is not None:
            root.right.parent = root
        root.parent = None
        root.refresh()
        return root, right

    @classmethod
    def _merge_roots(
        cls,
        left: ImplicitTreapNode[T] | None,
        right: ImplicitTreapNode[T] | None,
    ) -> ImplicitTreapNode[T] | None:
        if left is None:
            if right is not None:
                right.parent = None
            return right
        if right is None:
            left.parent = None
            return left

        if left.priority < right.priority:
            left.right = cls._merge_roots(left.right, right)
            if left.right is not None:
                left.right.parent = left
            left.parent = None
            left.refresh()
            return left

        right.left = cls._merge_roots(left, right.left)
        if right.left is not None:
            right.left.parent = right
        right.parent = None
        right.refresh()
        return right

    def _normalize_index(self, index: int) -> int:
        length = len(self)
        normalized = index + length if index < 0 else index
        if normalized < 0 or normalized >= length:
            raise IndexError("implicit treap index out of range")
        return normalized

    def _normalize_insert_index(self, index: int) -> int:
        length = len(self)
        normalized = index + length if index < 0 else index
        if normalized < 0:
            normalized = 0
        if normalized > length:
            normalized = length
        return normalized

    def _normalize_split_index(self, index: int) -> int:
        length = len(self)
        normalized = index + length if index < 0 else index
        if normalized < 0:
            return 0
        if normalized > length:
            return length
        return normalized

    def _inorder(
        self, node: ImplicitTreapNode[T] | None
    ) -> Generator[ImplicitTreapNode[T], None, None]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield node
        yield from self._inorder(node.right)
