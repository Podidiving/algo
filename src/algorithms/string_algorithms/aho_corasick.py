"""Aho-Corasick multiple-pattern matching.

The algorithm builds a trie of patterns and augments it with failure links.
This lets it scan the text once while reporting all pattern occurrences.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass(slots=True)
class AhoCorasickNode:
    """Single node inside the Aho-Corasick automaton."""

    children: dict[str, "AhoCorasickNode"] = field(default_factory=dict)
    fail: "AhoCorasickNode | None" = None
    outputs: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class AhoCorasickMatch:
    """Single pattern match reported by the automaton."""

    pattern: str
    start: int
    end: int


class AhoCorasickAutomaton:
    """Trie-based automaton for searching many patterns at once.

    Asymptotic complexity:
    - Building the trie is ``O(sum(len(pattern)))``
    - Building failure links is also ``O(sum(len(pattern)))``
    - Searching a text of length ``n`` is ``O(n + matches)``
    - Memory usage is ``O(sum(len(pattern)))``
    """

    def __init__(self, patterns: list[str] | tuple[str, ...] | None = None) -> None:
        self.root = AhoCorasickNode()
        self.root.fail = self.root
        self._built = False
        self._patterns: list[str] = []

        if patterns is not None:
            for pattern in patterns:
                self.add_pattern(pattern)
            self.build()

    def add_pattern(self, pattern: str) -> None:
        """Insert ``pattern`` into the trie.

        Empty patterns are not allowed because they would match at every text
        position and make the reporting API ambiguous.
        """

        if self._built:
            raise ValueError("cannot add patterns after building the automaton")
        if pattern == "":
            raise ValueError("empty patterns are not supported")

        node = self.root
        for char in pattern:
            node = node.children.setdefault(char, AhoCorasickNode())
        node.outputs.append(pattern)
        self._patterns.append(pattern)

    def build(self) -> None:
        """Build failure links for the current trie."""

        queue = deque()
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            node = queue.popleft()
            for char, child in node.children.items():
                queue.append(child)
                fail = node.fail
                while fail is not self.root and char not in fail.children:
                    fail = fail.fail
                if fail is None:
                    child.fail = self.root
                elif char in fail.children and fail.children[char] is not child:
                    child.fail = fail.children[char]
                else:
                    child.fail = self.root
                child.outputs.extend(
                    child.fail.outputs if child.fail is not None else []
                )

        self._built = True

    def search(self, text: str) -> list[AhoCorasickMatch]:
        """Return all pattern occurrences found in ``text``."""

        if not self._built:
            self.build()

        result: list[AhoCorasickMatch] = []
        node = self.root
        for index, char in enumerate(text):
            while node is not self.root and char not in node.children:
                fail = node.fail
                if fail is None:
                    break
                node = fail
            if char in node.children:
                node = node.children[char]
            else:
                node = self.root

            for pattern in node.outputs:
                start = index - len(pattern) + 1
                result.append(
                    AhoCorasickMatch(pattern=pattern, start=start, end=index + 1)
                )
        return result

    def search_as_dict(self, text: str) -> dict[str, list[int]]:
        """Return occurrences grouped by pattern."""

        grouped = {pattern: [] for pattern in self._patterns}
        for match in self.search(text):
            grouped.setdefault(match.pattern, []).append(match.start)
        return grouped
