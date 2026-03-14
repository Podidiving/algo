"""Simple binary search tree implementation.

This module provides the same linked-node style as the treap implementation,
but without randomized balancing. It is useful when you want a clear reference
implementation of BST operations or when balancing is not required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Generic, Iterable, Iterator, TypeVar

from .tree import TreeNode

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True, eq=False)
class BSTNode(TreeNode["BSTNode[K, V]"], Generic[K, V]):
    """A node in a binary search tree."""

    key: K
    value: V

    def __repr__(self) -> str:
        return f"BSTNode(key={self.key!r}, value={self.value!r}, size={self.size})"


class BST(Generic[K, V]):
    """Classic unbalanced binary search tree.

    The tree stores ``(key, value)`` pairs ordered by key. Unlike the treap,
    this structure does not rebalance itself, so operations are ``O(h)``,
    where ``h`` is the current tree height.
    """

    def __init__(self, items: Iterable[tuple[K, V]] | None = None) -> None:
        self.root: BSTNode[K, V] | None = None
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
        """Iterate over keys in sorted-key order."""

        return iter(self)

    def values(self) -> Iterator[V]:
        """Iterate over values in sorted-key order."""

        for node in self.inorder():
            yield node.value

    def clear(self) -> None:
        """Remove all nodes from the tree."""

        self.root = None

    def find_node(self, key: K) -> BSTNode[K, V] | None:
        """Return the node with ``key`` or ``None`` if it is absent."""

        current = self.root
        while current is not None:
            if key == current.key:
                return current
            current = current.left if key < current.key else current.right
        return None

    def get(self, key: K, default: V | None = None) -> V | None:
        """Return the value for ``key`` or ``default`` if absent."""

        node = self.find_node(key)
        return default if node is None else node.value

    def min_node(self) -> BSTNode[K, V] | None:
        """Return the smallest-key node."""

        return self._leftmost(self.root)

    def max_node(self) -> BSTNode[K, V] | None:
        """Return the largest-key node."""

        return self._rightmost(self.root)

    def lower_bound(self, key: K) -> BSTNode[K, V] | None:
        """Return the first node with key greater than or equal to ``key``."""

        current = self.root
        candidate: BSTNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def upper_bound(self, key: K) -> BSTNode[K, V] | None:
        """Return the first node with key strictly greater than ``key``."""

        current = self.root
        candidate: BSTNode[K, V] | None = None
        while current is not None:
            if key < current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def predecessor(self, key: K) -> BSTNode[K, V] | None:
        """Return the node with the largest key strictly smaller than ``key``."""

        current = self.root
        candidate: BSTNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                current = current.left
            else:
                candidate = current
                current = current.right
        return candidate

    def successor(self, key: K) -> BSTNode[K, V] | None:
        """Return the node with the smallest key strictly greater than ``key``."""

        return self.upper_bound(key)

    def kth(self, index: int) -> BSTNode[K, V]:
        """Return the node at zero-based sorted position ``index``."""

        if index < 0 or index >= len(self):
            raise IndexError("bst index out of range")

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
        raise RuntimeError("corrupted bst structure")

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

    def insert(self, key: K, value: V) -> BSTNode[K, V]:
        """Insert or replace a key/value pair and return its node."""

        if self.root is None:
            self.root = BSTNode(key=key, value=value)
            return self.root

        current = self.root
        parent: BSTNode[K, V] | None = None
        while current is not None:
            parent = current
            if key == current.key:
                current.value = value
                return current
            current = current.left if key < current.key else current.right

        node = BSTNode(key=key, value=value)
        node.parent = parent
        if key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._recompute_to_root(parent)
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
        """Remove ``key`` if present and report whether it existed."""

        node = self.find_node(key)
        if node is None:
            return False
        self._remove_node(node)
        return True

    def pop_min(self) -> tuple[K, V]:
        """Remove and return the smallest item."""

        node = self.min_node()
        if node is None:
            raise KeyError("pop from empty bst")
        item = (node.key, node.value)
        self._remove_node(node)
        return item

    def pop_max(self) -> tuple[K, V]:
        """Remove and return the largest item."""

        node = self.max_node()
        if node is None:
            raise KeyError("pop from empty bst")
        item = (node.key, node.value)
        self._remove_node(node)
        return item

    def inorder(self) -> Iterator[BSTNode[K, V]]:
        """Yield nodes in sorted-key order."""

        yield from self._inorder(self.root)

    def validate(self) -> None:
        """Raise ``ValueError`` if BST ordering or sizes are broken."""

        def walk(node: BSTNode[K, V] | None, low: K | None, high: K | None) -> int:
            if node is None:
                return 0
            if low is not None and node.key <= low:
                raise ValueError("BST invariant violated on left boundary")
            if high is not None and node.key >= high:
                raise ValueError("BST invariant violated on right boundary")
            if node.left is not None and node.left.parent is not node:
                raise ValueError("broken parent pointer")
            if node.right is not None and node.right.parent is not node:
                raise ValueError("broken parent pointer")
            left_size = walk(node.left, low, node.key)
            right_size = walk(node.right, node.key, high)
            expected = 1 + left_size + right_size
            if node.size != expected:
                raise ValueError("cached subtree size is incorrect")
            return expected

        walk(self.root, None, None)

    def _remove_node(self, node: BSTNode[K, V]) -> None:
        if node.left is not None and node.right is not None:
            successor = self._leftmost(node.right)
            if successor is None:
                raise RuntimeError("corrupted bst structure")
            node.key, successor.key = successor.key, node.key
            node.value, successor.value = successor.value, node.value
            node = successor

        child = node.left if node.left is not None else node.right
        self._replace_node(node, child)

    def _replace_node(
        self, node: BSTNode[K, V], replacement: BSTNode[K, V] | None
    ) -> None:
        parent = node.parent
        if replacement is not None:
            replacement.parent = parent

        if parent is None:
            self.root = replacement
        elif parent.left is node:
            parent.left = replacement
        else:
            parent.right = replacement

        node.parent = None
        node.left = None
        node.right = None
        self._recompute_to_root(parent)

    def _recompute_to_root(self, node: BSTNode[K, V] | None) -> None:
        while node is not None:
            node.refresh()
            node = node.parent

    def _inorder(
        self, node: BSTNode[K, V] | None
    ) -> Generator[BSTNode[K, V], None, None]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield node
        yield from self._inorder(node.right)

    @staticmethod
    def _leftmost(node: BSTNode[K, V] | None) -> BSTNode[K, V] | None:
        while node is not None and node.left is not None:
            node = node.left
        return node

    @staticmethod
    def _rightmost(node: BSTNode[K, V] | None) -> BSTNode[K, V] | None:
        while node is not None and node.right is not None:
            node = node.right
        return node
