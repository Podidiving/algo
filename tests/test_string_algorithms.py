from algorithms import compute_prefix_function, kmp_search


def test_prefix_function_matches_expected_values() -> None:
    assert compute_prefix_function("ababcabab") == [0, 0, 1, 2, 0, 1, 2, 3, 4]
    assert compute_prefix_function("") == []
    assert compute_prefix_function("aaaa") == [0, 1, 2, 3]


def test_kmp_search_finds_all_occurrences() -> None:
    assert kmp_search("ababaabababa", "ababa") == [0, 5, 7]
    assert kmp_search("aaaaa", "aa") == [0, 1, 2, 3]
    assert kmp_search("abcdef", "gh") == []
    assert kmp_search("abc", "") == [0, 1, 2, 3]
