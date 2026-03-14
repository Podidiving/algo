"""Treap implementation.

A treap combines two invariants:

1. Keys follow the binary-search-tree ordering.
2. Priorities follow the heap ordering.

This gives a randomized balanced BST when priorities are chosen at random.
The implementation below keeps explicit parent pointers and subtree sizes,
which makes it useful both as an ordered map and as an order-statistics tree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Generator, Generic, Iterable, Iterator, TypeVar

from .tree import TreeNode

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True, eq=False)
class TreapNode(TreeNode["TreapNode[K, V]"], Generic[K, V]):
    """Single node stored inside a :class:`Treap`.

    ``priority`` controls balancing. Smaller priorities are placed closer
    to the root so the tree behaves like a min-heap by priority.
    """

    key: K
    value: V
    priority: float = field(default_factory=random.random)

    def __repr__(self) -> str:
        return (
            f"TreapNode(key={self.key!r}, value={self.value!r}, "
            f"priority={self.priority:.6f}, size={self.size})"
        )


class Treap(Generic[K, V]):
    """Randomized balanced binary-search tree.

    The treap stores ``(key, value)`` pairs and supports:

    - search by key
    - insertion and deletion
    - split and merge
    - predecessor/successor queries
    - ``k``-th element and rank lookup via subtree sizes

    Average complexity is ``O(log n)`` for updates and queries.
    """

    def __init__(self, items: Iterable[tuple[K, V]] | None = None) -> None:
        self.root: TreapNode[K, V] | None = None
        if items is not None:
            for key, value in items:
                self.insert(key, value)

    def __len__(self) -> int:
        return 0 if self.root is None else self.root.size

    def __bool__(self) -> bool:
        return self.root is not None

    def __contains__(self, key: K) -> bool:
        return self.find_node(key) is not None

    def __iter__(self) -> Iterator[K]:
        for node in self.inorder():
            yield node.key

    def items(self) -> Iterator[tuple[K, V]]:
        """Iterate over items in sorted-key order."""

        for node in self.inorder():
            yield node.key, node.value

    def keys(self) -> Iterator[K]:
        """Iterate over keys in sorted order."""

        return iter(self)

    def values(self) -> Iterator[V]:
        """Iterate over values in sorted-key order."""

        for node in self.inorder():
            yield node.value

    def clear(self) -> None:
        """Remove all nodes from the treap."""

        self.root = None

    def find_node(self, key: K) -> TreapNode[K, V] | None:
        """Return the node with ``key`` or ``None`` if it is absent."""

        current = self.root
        while current is not None:
            if key == current.key:
                return current
            if key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def get(self, key: K, default: V | None = None) -> V | None:
        """Return the value stored under ``key`` or ``default``."""

        node = self.find_node(key)
        return default if node is None else node.value

    def min_node(self) -> TreapNode[K, V] | None:
        """Return the smallest-key node."""

        return self._leftmost(self.root)

    def max_node(self) -> TreapNode[K, V] | None:
        """Return the largest-key node."""

        return self._rightmost(self.root)

    def lower_bound(self, key: K) -> TreapNode[K, V] | None:
        """Return the first node whose key is greater than or equal to ``key``."""

        current = self.root
        candidate: TreapNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def upper_bound(self, key: K) -> TreapNode[K, V] | None:
        """Return the first node whose key is strictly greater than ``key``."""

        current = self.root
        candidate: TreapNode[K, V] | None = None
        while current is not None:
            if key < current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def predecessor(self, key: K) -> TreapNode[K, V] | None:
        """Return the node with the largest key strictly smaller than ``key``."""

        current = self.root
        candidate: TreapNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                current = current.left
            else:
                candidate = current
                current = current.right
        return candidate

    def successor(self, key: K) -> TreapNode[K, V] | None:
        """Return the node with the smallest key strictly greater than ``key``."""

        return self.upper_bound(key)

    def kth(self, index: int) -> TreapNode[K, V]:
        """Return the node at zero-based sorted position ``index``."""

        if index < 0 or index >= len(self):
            raise IndexError("treap index out of range")

        current = self.root
        while current is not None:
            left_size = current._child_size(current.left)
            if index < left_size:
                current = current.left
            elif index == left_size:
                return current
            else:
                index -= left_size + 1
                current = current.right

        raise RuntimeError("corrupted treap structure")

    def rank(self, key: K) -> int:
        """Return the count of keys strictly smaller than ``key``."""

        current = self.root
        result = 0
        while current is not None:
            if key <= current.key:
                current = current.left
            else:
                result += 1 + current._child_size(current.left)
                current = current.right
        return result

    def insert(
        self, key: K, value: V, *, priority: float | None = None
    ) -> TreapNode[K, V]:
        """Insert or replace a key/value pair and return its node.

        The treap first follows BST ordering to find the key. If the key
        already exists, only its value is replaced. Otherwise a new node is
        inserted and then rotated upward until the heap invariant is restored.
        """

        if self.root is None:
            self.root = self._make_node(key, value, priority)
            return self.root

        current = self.root
        parent: TreapNode[K, V] | None = None
        while current is not None:
            parent = current
            if key == current.key:
                current.value = value
                return current
            if key < current.key:
                current = current.left
            else:
                current = current.right

        node = self._make_node(key, value, priority)
        node.parent = parent
        if key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._recompute_to_root(parent)
        self._bubble_up(node)
        return node

    def remove(self, key: K) -> V:
        """Remove ``key`` and return its associated value."""

        node = self.find_node(key)
        if node is None:
            raise KeyError(key)
        value = node.value
        self._remove_node(node)
        return value

    def discard(self, key: K) -> bool:
        """Remove ``key`` if present and report whether removal happened."""

        node = self.find_node(key)
        if node is None:
            return False
        self._remove_node(node)
        return True

    def pop_min(self) -> tuple[K, V]:
        """Remove and return the smallest item."""

        node = self.min_node()
        if node is None:
            raise KeyError("pop from empty treap")
        item = (node.key, node.value)
        self._remove_node(node)
        return item

    def pop_max(self) -> tuple[K, V]:
        """Remove and return the largest item."""

        node = self.max_node()
        if node is None:
            raise KeyError("pop from empty treap")
        item = (node.key, node.value)
        self._remove_node(node)
        return item

    def split(self, key: K) -> tuple["Treap[K, V]", "Treap[K, V]"]:
        """Split into ``(< key, >= key)`` treaps."""

        left_root, right_root = self._split(self.root, key)
        left = self.__class__()
        right = self.__class__()
        left.root = left_root
        right.root = right_root
        self.root = None
        return left, right

    @classmethod
    def merge(cls, left: "Treap[K, V]", right: "Treap[K, V]") -> "Treap[K, V]":
        """Merge two treaps where every key in ``left`` is smaller than in ``right``."""

        merged = cls()
        merged.root = cls._merge_roots(left.root, right.root)
        left.root = None
        right.root = None
        return merged

    def inorder(self) -> Iterator[TreapNode[K, V]]:
        """Yield nodes in sorted-key order."""

        yield from self._inorder(self.root)

    def validate(self) -> None:
        """Raise ``ValueError`` if BST, heap, or size invariants are broken."""

        def walk(
            node: TreapNode[K, V] | None,
            low: K | None,
            high: K | None,
        ) -> int:
            if node is None:
                return 0
            if low is not None and node.key <= low:
                raise ValueError("BST invariant violated on left boundary")
            if high is not None and node.key >= high:
                raise ValueError("BST invariant violated on right boundary")
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
            left_size = walk(node.left, low, node.key)
            right_size = walk(node.right, node.key, high)
            expected = 1 + left_size + right_size
            if node.size != expected:
                raise ValueError("cached subtree size is incorrect")
            return expected

        walk(self.root, None, None)

    def _make_node(
        self, key: K, value: V, priority: float | None = None
    ) -> TreapNode[K, V]:
        node = TreapNode(key=key, value=value)
        if priority is not None:
            node.priority = priority
        return node

    def _bubble_up(self, node: TreapNode[K, V]) -> None:
        # Rotate the inserted node upward until the heap order is restored.
        while node.parent is not None and node.priority < node.parent.priority:
            if node.parent.left is node:
                self._rotate_right(node.parent)
            else:
                self._rotate_left(node.parent)

    def _remove_node(self, node: TreapNode[K, V]) -> None:
        # Push the node down until it becomes a leaf, then detach it.
        while node.left is not None or node.right is not None:
            if node.left is None:
                self._rotate_left(node)
            elif node.right is None:
                self._rotate_right(node)
            elif node.left.priority < node.right.priority:
                self._rotate_right(node)
            else:
                self._rotate_left(node)

        parent = node.parent
        if parent is None:
            self.root = None
        elif parent.left is node:
            parent.left = None
            self._recompute_to_root(parent)
        else:
            parent.right = None
            self._recompute_to_root(parent)
        node.parent = None

    def _rotate_left(self, pivot: TreapNode[K, V]) -> None:
        child = pivot.right
        if child is None:
            raise ValueError("left rotation requires a right child")

        pivot.right = child.left
        if child.left is not None:
            child.left.parent = pivot

        child.parent = pivot.parent
        if pivot.parent is None:
            self.root = child
        elif pivot.parent.left is pivot:
            pivot.parent.left = child
        else:
            pivot.parent.right = child

        child.left = pivot
        pivot.parent = child

        pivot.refresh()
        child.refresh()
        self._recompute_to_root(child.parent)

    def _rotate_right(self, pivot: TreapNode[K, V]) -> None:
        child = pivot.left
        if child is None:
            raise ValueError("right rotation requires a left child")

        pivot.left = child.right
        if child.right is not None:
            child.right.parent = pivot

        child.parent = pivot.parent
        if pivot.parent is None:
            self.root = child
        elif pivot.parent.left is pivot:
            pivot.parent.left = child
        else:
            pivot.parent.right = child

        child.right = pivot
        pivot.parent = child

        pivot.refresh()
        child.refresh()
        self._recompute_to_root(child.parent)

    @classmethod
    def _split(
        cls, root: TreapNode[K, V] | None, key: K
    ) -> tuple[TreapNode[K, V] | None, TreapNode[K, V] | None]:
        if root is None:
            return None, None

        if key <= root.key:
            left, root.left = cls._split(root.left, key)
            if root.left is not None:
                root.left.parent = root
            root.parent = None
            root.refresh()
            return left, root

        root.right, right = cls._split(root.right, key)
        if root.right is not None:
            root.right.parent = root
        root.parent = None
        root.refresh()
        return root, right

    @classmethod
    def _merge_roots(
        cls,
        left: TreapNode[K, V] | None,
        right: TreapNode[K, V] | None,
    ) -> TreapNode[K, V] | None:
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

    def _recompute_to_root(self, node: TreapNode[K, V] | None) -> None:
        while node is not None:
            node.refresh()
            node = node.parent

    def _inorder(
        self, node: TreapNode[K, V] | None
    ) -> Generator[TreapNode[K, V], None, None]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield node
        yield from self._inorder(node.right)

    @staticmethod
    def _leftmost(node: TreapNode[K, V] | None) -> TreapNode[K, V] | None:
        while node is not None and node.left is not None:
            node = node.left
        return node

    @staticmethod
    def _rightmost(node: TreapNode[K, V] | None) -> TreapNode[K, V] | None:
        while node is not None and node.right is not None:
            node = node.right
        return node
