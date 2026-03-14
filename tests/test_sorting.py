from algorithms import heapsort, mergesort, quicksort, radix_sort


def test_comparison_sorts_match_python_sorted() -> None:
    data = [5, 1, 9, 3, 3, 0, -2, 8, 4]
    expected = sorted(data)

    assert quicksort(data) == expected
    assert mergesort(data) == expected
    assert heapsort(data) == expected
    assert data == [5, 1, 9, 3, 3, 0, -2, 8, 4]


def test_comparison_sorts_handle_empty_singleton_and_sorted_inputs() -> None:
    for values in ([], [1], [1, 2, 3, 4], [4, 3, 2, 1]):
        expected = sorted(values)
        assert quicksort(values) == expected
        assert mergesort(values) == expected
        assert heapsort(values) == expected


def test_radix_sort_handles_positive_negative_and_duplicate_integers() -> None:
    data = [170, 45, 75, -90, -802, 24, 2, 66, 45, 0]
    expected = sorted(data)

    assert radix_sort(data) == expected
    assert data == [170, 45, 75, -90, -802, 24, 2, 66, 45, 0]


def test_radix_sort_handles_edge_cases() -> None:
    assert radix_sort([]) == []
    assert radix_sort([7]) == [7]
    assert radix_sort([0, 0, 0]) == [0, 0, 0]
    assert radix_sort([-5, -1, -10, -3]) == [-10, -5, -3, -1]
