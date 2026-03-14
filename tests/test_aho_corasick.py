import pytest

from algorithms import AhoCorasickAutomaton, AhoCorasickMatch


def test_aho_corasick_finds_overlapping_multi_pattern_matches() -> None:
    automaton = AhoCorasickAutomaton(["he", "she", "his", "hers"])

    matches = automaton.search("ushers")

    assert matches == [
        AhoCorasickMatch(pattern="she", start=1, end=4),
        AhoCorasickMatch(pattern="he", start=2, end=4),
        AhoCorasickMatch(pattern="hers", start=2, end=6),
    ]


def test_aho_corasick_groups_matches_by_pattern() -> None:
    automaton = AhoCorasickAutomaton()
    automaton.add_pattern("aba")
    automaton.add_pattern("ba")
    automaton.build()

    assert automaton.search_as_dict("ababa") == {
        "aba": [0, 2],
        "ba": [1, 3],
    }


def test_aho_corasick_rejects_empty_patterns_and_mutation_after_build() -> None:
    automaton = AhoCorasickAutomaton()

    with pytest.raises(ValueError):
        automaton.add_pattern("")

    automaton.add_pattern("abc")
    automaton.build()

    with pytest.raises(ValueError):
        automaton.add_pattern("def")
