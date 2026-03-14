"""Knuth-Morris-Pratt string matching and prefix function."""

from __future__ import annotations


def compute_prefix_function(pattern: str) -> list[int]:
    """Return the prefix-function table for ``pattern``.

    ``pi[i]`` stores the length of the longest proper prefix of
    ``pattern[: i + 1]`` that is also a suffix of that substring.
    """

    prefix = [0] * len(pattern)
    border = 0
    for index in range(1, len(pattern)):
        while border > 0 and pattern[index] != pattern[border]:
            border = prefix[border - 1]
        if pattern[index] == pattern[border]:
            border += 1
            prefix[index] = border
    return prefix


def kmp_search(text: str, pattern: str) -> list[int]:
    """Return all starting indexes where ``pattern`` occurs in ``text``."""

    if pattern == "":
        return list(range(len(text) + 1))

    prefix = compute_prefix_function(pattern)
    result: list[int] = []
    matched = 0

    for index, char in enumerate(text):
        while matched > 0 and char != pattern[matched]:
            matched = prefix[matched - 1]
        if char == pattern[matched]:
            matched += 1
            if matched == len(pattern):
                result.append(index - len(pattern) + 1)
                matched = prefix[matched - 1]
    return result
