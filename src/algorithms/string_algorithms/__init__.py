"""String-processing algorithms."""

from .aho_corasick import AhoCorasickAutomaton, AhoCorasickMatch, AhoCorasickNode
from .pattern_matching import compute_prefix_function, kmp_search

__all__ = [
    "AhoCorasickAutomaton",
    "AhoCorasickMatch",
    "AhoCorasickNode",
    "compute_prefix_function",
    "kmp_search",
]
