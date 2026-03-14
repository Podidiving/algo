"""AVL tree implementation.

An AVL tree is a self-balancing binary search tree. After every insertion or
deletion it restores the height difference between left and right subtrees to
at most one, using rotations. This keeps operations at ``O(log n)``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generator, Generic, Iterable, Iterator, TypeVar

from .tree import TreeNode

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True, eq=False)
class AVLNode(TreeNode["AVLNode[K, V]"], Generic[K, V]):
    """A node in an AVL tree."""

    key: K
    value: V
    height: int = field(default=1, init=False)

    def __repr__(self) -> str:
        return (
            f"AVLNode(key={self.key!r}, value={self.value!r}, "
            f"height={self.height}, size={self.size})"
        )

    def refresh(self) -> None:
        """Recompute cached subtree metadata and height from the children."""

        TreeNode.refresh(self)
        self.height = 1 + max(
            self._child_height(self.left), self._child_height(self.right)
        )

    @staticmethod
    def _child_height(node: "AVLNode[K, V] | None") -> int:
        return 0 if node is None else node.height

    def balance_factor(self) -> int:
        """Return left subtree height minus right subtree height."""

        return self._child_height(self.left) - self._child_height(self.right)


class AVLTree(Generic[K, V]):
    """Self-balancing ordered map based on AVL rotations."""

    def __init__(self, items: Iterable[tuple[K, V]] | None = None) -> None:
        self.root: AVLNode[K, V] | None = None
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

    def find_node(self, key: K) -> AVLNode[K, V] | None:
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

    def min_node(self) -> AVLNode[K, V] | None:
        """Return the smallest-key node."""

        return self._leftmost(self.root)

    def max_node(self) -> AVLNode[K, V] | None:
        """Return the largest-key node."""

        return self._rightmost(self.root)

    def lower_bound(self, key: K) -> AVLNode[K, V] | None:
        """Return the first node with key greater than or equal to ``key``."""

        current = self.root
        candidate: AVLNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def upper_bound(self, key: K) -> AVLNode[K, V] | None:
        """Return the first node with key strictly greater than ``key``."""

        current = self.root
        candidate: AVLNode[K, V] | None = None
        while current is not None:
            if key < current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def predecessor(self, key: K) -> AVLNode[K, V] | None:
        """Return the node with the largest key strictly smaller than ``key``."""

        current = self.root
        candidate: AVLNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                current = current.left
            else:
                candidate = current
                current = current.right
        return candidate

    def successor(self, key: K) -> AVLNode[K, V] | None:
        """Return the node with the smallest key strictly greater than ``key``."""

        return self.upper_bound(key)

    def kth(self, index: int) -> AVLNode[K, V]:
        """Return the node at zero-based sorted position ``index``."""

        if index < 0 or index >= len(self):
            raise IndexError("avl index out of range")

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
        raise RuntimeError("corrupted avl structure")

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

    def insert(self, key: K, value: V) -> AVLNode[K, V]:
        """Insert or replace a key/value pair and return its node."""

        if self.root is None:
            self.root = AVLNode(key=key, value=value)
            return self.root

        current = self.root
        parent: AVLNode[K, V] | None = None
        while current is not None:
            parent = current
            if key == current.key:
                current.value = value
                return current
            current = current.left if key < current.key else current.right

        node = AVLNode(key=key, value=value)
        node.parent = parent
        if key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._rebalance_from(parent)
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
            raise KeyError("pop from empty avl tree")
        item = (node.key, node.value)
        self._remove_node(node)
        return item

    def pop_max(self) -> tuple[K, V]:
        """Remove and return the largest item."""

        node = self.max_node()
        if node is None:
            raise KeyError("pop from empty avl tree")
        item = (node.key, node.value)
        self._remove_node(node)
        return item

    def inorder(self) -> Iterator[AVLNode[K, V]]:
        """Yield nodes in sorted-key order."""

        yield from self._inorder(self.root)

    def validate(self) -> None:
        """Raise ``ValueError`` if BST, AVL, size, or height invariants are broken."""

        def walk(
            node: AVLNode[K, V] | None, low: K | None, high: K | None
        ) -> tuple[int, int]:
            if node is None:
                return 0, 0
            if low is not None and node.key <= low:
                raise ValueError("BST invariant violated on left boundary")
            if high is not None and node.key >= high:
                raise ValueError("BST invariant violated on right boundary")
            if node.left is not None and node.left.parent is not node:
                raise ValueError("broken parent pointer")
            if node.right is not None and node.right.parent is not node:
                raise ValueError("broken parent pointer")

            left_size, left_height = walk(node.left, low, node.key)
            right_size, right_height = walk(node.right, node.key, high)
            if abs(left_height - right_height) > 1:
                raise ValueError("AVL balance invariant violated")

            expected_size = 1 + left_size + right_size
            if node.size != expected_size:
                raise ValueError("cached subtree size is incorrect")

            expected_height = 1 + max(left_height, right_height)
            if node.height != expected_height:
                raise ValueError("cached height is incorrect")

            return expected_size, expected_height

        walk(self.root, None, None)

    def _remove_node(self, node: AVLNode[K, V]) -> None:
        if node.left is not None and node.right is not None:
            successor = self._leftmost(node.right)
            if successor is None:
                raise RuntimeError("corrupted avl structure")
            node.key, successor.key = successor.key, node.key
            node.value, successor.value = successor.value, node.value
            node = successor

        child = node.left if node.left is not None else node.right
        parent = node.parent
        if child is not None:
            child.parent = parent

        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child

        node.parent = None
        node.left = None
        node.right = None
        self._rebalance_from(parent)

    def _rebalance_from(self, node: AVLNode[K, V] | None) -> None:
        while node is not None:
            node.refresh()
            balance = node.balance_factor()

            if balance > 1:
                left = node.left
                if left is None:
                    raise RuntimeError("corrupted avl structure")
                if left.balance_factor() < 0:
                    self._rotate_left(left)
                new_root = self._rotate_right(node)
                node = new_root.parent
                continue

            if balance < -1:
                right = node.right
                if right is None:
                    raise RuntimeError("corrupted avl structure")
                if right.balance_factor() > 0:
                    self._rotate_right(right)
                new_root = self._rotate_left(node)
                node = new_root.parent
                continue

            node = node.parent

    def _rotate_left(self, pivot: AVLNode[K, V]) -> AVLNode[K, V]:
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
        return child

    def _rotate_right(self, pivot: AVLNode[K, V]) -> AVLNode[K, V]:
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
        return child

    def _inorder(
        self, node: AVLNode[K, V] | None
    ) -> Generator[AVLNode[K, V], None, None]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield node
        yield from self._inorder(node.right)

    @staticmethod
    def _leftmost(node: AVLNode[K, V] | None) -> AVLNode[K, V] | None:
        while node is not None and node.left is not None:
            node = node.left
        return node

    @staticmethod
    def _rightmost(node: AVLNode[K, V] | None) -> AVLNode[K, V] | None:
        while node is not None and node.right is not None:
            node = node.right
        return node
