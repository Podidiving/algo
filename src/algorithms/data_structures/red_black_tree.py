"""Red-black tree implementation.

A red-black tree is a balanced binary search tree that stores one extra bit of
color on each node. The color rules guarantee logarithmic height without
needing explicit subtree-height rebalancing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generator, Generic, Iterable, Iterator, Literal, TypeVar

from .tree import TreeNode

K = TypeVar("K")
V = TypeVar("V")
Color = Literal["red", "black"]


@dataclass(slots=True, eq=False)
class RedBlackNode(TreeNode["RedBlackNode[K, V]"], Generic[K, V]):
    """A node in a red-black tree."""

    key: K
    value: V
    color: Color = field(default="red", init=False)

    def __repr__(self) -> str:
        return (
            f"RedBlackNode(key={self.key!r}, value={self.value!r}, "
            f"color={self.color}, size={self.size})"
        )


class RedBlackTree(Generic[K, V]):
    """Self-balancing ordered map based on red-black invariants."""

    def __init__(self, items: Iterable[tuple[K, V]] | None = None) -> None:
        self.root: RedBlackNode[K, V] | None = None
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

    def find_node(self, key: K) -> RedBlackNode[K, V] | None:
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

    def min_node(self) -> RedBlackNode[K, V] | None:
        """Return the smallest-key node."""

        return self._leftmost(self.root)

    def max_node(self) -> RedBlackNode[K, V] | None:
        """Return the largest-key node."""

        return self._rightmost(self.root)

    def lower_bound(self, key: K) -> RedBlackNode[K, V] | None:
        """Return the first node with key greater than or equal to ``key``."""

        current = self.root
        candidate: RedBlackNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def upper_bound(self, key: K) -> RedBlackNode[K, V] | None:
        """Return the first node with key strictly greater than ``key``."""

        current = self.root
        candidate: RedBlackNode[K, V] | None = None
        while current is not None:
            if key < current.key:
                candidate = current
                current = current.left
            else:
                current = current.right
        return candidate

    def predecessor(self, key: K) -> RedBlackNode[K, V] | None:
        """Return the node with the largest key strictly smaller than ``key``."""

        current = self.root
        candidate: RedBlackNode[K, V] | None = None
        while current is not None:
            if key <= current.key:
                current = current.left
            else:
                candidate = current
                current = current.right
        return candidate

    def successor(self, key: K) -> RedBlackNode[K, V] | None:
        """Return the node with the smallest key strictly greater than ``key``."""

        return self.upper_bound(key)

    def kth(self, index: int) -> RedBlackNode[K, V]:
        """Return the node at zero-based sorted position ``index``."""

        if index < 0 or index >= len(self):
            raise IndexError("red-black tree index out of range")

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
        raise RuntimeError("corrupted red-black tree structure")

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

    def insert(self, key: K, value: V) -> RedBlackNode[K, V]:
        """Insert or replace a key/value pair and return its node."""

        if self.root is None:
            self.root = RedBlackNode(key=key, value=value)
            self.root.color = "black"
            return self.root

        current = self.root
        parent: RedBlackNode[K, V] | None = None
        while current is not None:
            parent = current
            if key == current.key:
                current.value = value
                return current
            current = current.left if key < current.key else current.right

        node = RedBlackNode(key=key, value=value)
        node.parent = parent
        if key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._recompute_to_root(parent)
        self._fix_insert(node)
        return node

    def remove(self, key: K) -> V:
        """Remove ``key`` and return its associated value."""

        node = self.find_node(key)
        if node is None:
            raise KeyError(key)
        value = node.value
        self._delete_node(node)
        return value

    def discard(self, key: K) -> bool:
        """Remove ``key`` if present and report whether it existed."""

        node = self.find_node(key)
        if node is None:
            return False
        self._delete_node(node)
        return True

    def pop_min(self) -> tuple[K, V]:
        """Remove and return the smallest item."""

        node = self.min_node()
        if node is None:
            raise KeyError("pop from empty red-black tree")
        item = (node.key, node.value)
        self._delete_node(node)
        return item

    def pop_max(self) -> tuple[K, V]:
        """Remove and return the largest item."""

        node = self.max_node()
        if node is None:
            raise KeyError("pop from empty red-black tree")
        item = (node.key, node.value)
        self._delete_node(node)
        return item

    def inorder(self) -> Iterator[RedBlackNode[K, V]]:
        """Yield nodes in sorted-key order."""

        yield from self._inorder(self.root)

    def validate(self) -> None:
        """Raise ``ValueError`` if BST, color, or size invariants are broken."""

        def walk(
            node: RedBlackNode[K, V] | None, low: K | None, high: K | None
        ) -> tuple[int, int]:
            if node is None:
                return 0, 1
            if low is not None and node.key <= low:
                raise ValueError("BST invariant violated on left boundary")
            if high is not None and node.key >= high:
                raise ValueError("BST invariant violated on right boundary")
            if node.left is not None and node.left.parent is not node:
                raise ValueError("broken parent pointer")
            if node.right is not None and node.right.parent is not node:
                raise ValueError("broken parent pointer")
            if node.color == "red":
                if self._color(node.left) == "red" or self._color(node.right) == "red":
                    raise ValueError("red node cannot have red children")

            left_size, left_black_height = walk(node.left, low, node.key)
            right_size, right_black_height = walk(node.right, node.key, high)
            if left_black_height != right_black_height:
                raise ValueError("black-height invariant violated")

            expected_size = 1 + left_size + right_size
            if node.size != expected_size:
                raise ValueError("cached subtree size is incorrect")

            black_height = left_black_height + (1 if node.color == "black" else 0)
            return expected_size, black_height

        if self.root is not None and self.root.color != "black":
            raise ValueError("root must be black")
        walk(self.root, None, None)

    def _delete_node(self, node: RedBlackNode[K, V]) -> None:
        original_color = node.color
        if node.left is None:
            replacement = node.right
            parent = node.parent
            self._transplant(node, node.right)
            self._recompute_to_root(parent)
            if original_color == "black":
                self._fix_delete(replacement, parent)
            return

        if node.right is None:
            replacement = node.left
            parent = node.parent
            self._transplant(node, node.left)
            self._recompute_to_root(parent)
            if original_color == "black":
                self._fix_delete(replacement, parent)
            return

        successor = self._leftmost(node.right)
        if successor is None:
            raise RuntimeError("corrupted red-black tree structure")

        original_color = successor.color
        replacement = successor.right
        if successor.parent is node:
            parent = successor
        else:
            parent = successor.parent
            self._transplant(successor, successor.right)
            successor.right = node.right
            if successor.right is not None:
                successor.right.parent = successor

        self._transplant(node, successor)
        successor.left = node.left
        if successor.left is not None:
            successor.left.parent = successor
        successor.color = node.color
        successor.refresh()
        self._recompute_to_root(successor.parent)

        if original_color == "black":
            self._fix_delete(replacement, parent)

    def _fix_insert(self, node: RedBlackNode[K, V]) -> None:
        while node.parent is not None and node.parent.color == "red":
            grandparent = node.parent.parent
            if grandparent is None:
                break
            if node.parent is grandparent.left:
                uncle = grandparent.right
                if self._color(uncle) == "red":
                    node.parent.color = "black"
                    if uncle is not None:
                        uncle.color = "black"
                    grandparent.color = "red"
                    node = grandparent
                    continue
                if node is node.parent.right:
                    node = node.parent
                    self._rotate_left(node)
                node.parent.color = "black"
                grandparent.color = "red"
                self._rotate_right(grandparent)
            else:
                uncle = grandparent.left
                if self._color(uncle) == "red":
                    node.parent.color = "black"
                    if uncle is not None:
                        uncle.color = "black"
                    grandparent.color = "red"
                    node = grandparent
                    continue
                if node is node.parent.left:
                    node = node.parent
                    self._rotate_right(node)
                node.parent.color = "black"
                grandparent.color = "red"
                self._rotate_left(grandparent)
        if self.root is not None:
            self.root.color = "black"

    def _fix_delete(
        self,
        node: RedBlackNode[K, V] | None,
        parent: RedBlackNode[K, V] | None,
    ) -> None:
        while node is not self.root and self._color(node) == "black":
            if parent is None:
                break
            if node is parent.left:
                sibling = parent.right
                if self._color(sibling) == "red":
                    sibling.color = "black"
                    parent.color = "red"
                    self._rotate_left(parent)
                    sibling = parent.right
                if (
                    self._color(self._left(sibling)) == "black"
                    and self._color(self._right(sibling)) == "black"
                ):
                    if sibling is not None:
                        sibling.color = "red"
                    node = parent
                    parent = node.parent
                else:
                    if self._color(self._right(sibling)) == "black":
                        left_child = self._left(sibling)
                        if left_child is not None:
                            left_child.color = "black"
                        if sibling is not None:
                            sibling.color = "red"
                            self._rotate_right(sibling)
                        sibling = parent.right
                    if sibling is not None:
                        sibling.color = parent.color
                    parent.color = "black"
                    right_child = self._right(sibling)
                    if right_child is not None:
                        right_child.color = "black"
                    self._rotate_left(parent)
                    node = self.root
                    parent = None
            else:
                sibling = parent.left
                if self._color(sibling) == "red":
                    sibling.color = "black"
                    parent.color = "red"
                    self._rotate_right(parent)
                    sibling = parent.left
                if (
                    self._color(self._left(sibling)) == "black"
                    and self._color(self._right(sibling)) == "black"
                ):
                    if sibling is not None:
                        sibling.color = "red"
                    node = parent
                    parent = node.parent
                else:
                    if self._color(self._left(sibling)) == "black":
                        right_child = self._right(sibling)
                        if right_child is not None:
                            right_child.color = "black"
                        if sibling is not None:
                            sibling.color = "red"
                            self._rotate_left(sibling)
                        sibling = parent.left
                    if sibling is not None:
                        sibling.color = parent.color
                    parent.color = "black"
                    left_child = self._left(sibling)
                    if left_child is not None:
                        left_child.color = "black"
                    self._rotate_right(parent)
                    node = self.root
                    parent = None
        if node is not None:
            node.color = "black"
        if self.root is not None:
            self.root.color = "black"

    def _transplant(
        self,
        target: RedBlackNode[K, V],
        replacement: RedBlackNode[K, V] | None,
    ) -> None:
        if target.parent is None:
            self.root = replacement
        elif target is target.parent.left:
            target.parent.left = replacement
        else:
            target.parent.right = replacement
        if replacement is not None:
            replacement.parent = target.parent
        target.parent = None

    def _rotate_left(self, pivot: RedBlackNode[K, V]) -> RedBlackNode[K, V]:
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
        return child

    def _rotate_right(self, pivot: RedBlackNode[K, V]) -> RedBlackNode[K, V]:
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
        return child

    def _recompute_to_root(self, node: RedBlackNode[K, V] | None) -> None:
        while node is not None:
            node.refresh()
            node = node.parent

    def _inorder(
        self, node: RedBlackNode[K, V] | None
    ) -> Generator[RedBlackNode[K, V], None, None]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield node
        yield from self._inorder(node.right)

    @staticmethod
    def _leftmost(node: RedBlackNode[K, V] | None) -> RedBlackNode[K, V] | None:
        while node is not None and node.left is not None:
            node = node.left
        return node

    @staticmethod
    def _rightmost(node: RedBlackNode[K, V] | None) -> RedBlackNode[K, V] | None:
        while node is not None and node.right is not None:
            node = node.right
        return node

    @staticmethod
    def _color(node: RedBlackNode[K, V] | None) -> Color:
        return "black" if node is None else node.color

    @staticmethod
    def _left(node: RedBlackNode[K, V] | None) -> RedBlackNode[K, V] | None:
        return None if node is None else node.left

    @staticmethod
    def _right(node: RedBlackNode[K, V] | None) -> RedBlackNode[K, V] | None:
        return None if node is None else node.right
