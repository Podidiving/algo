"""Custom sorting algorithm implementations."""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


def quicksort(values: list[T]) -> list[T]:
    """Return a sorted copy of ``values`` using quicksort.

    The implementation uses a three-way partition around the middle element to
    handle duplicate values cleanly without mutating the input list.
    """

    items = list(values)
    if len(items) <= 1:
        return items

    pivot = items[len(items) // 2]
    lower = [value for value in items if value < pivot]
    equal = [value for value in items if value == pivot]
    higher = [value for value in items if value > pivot]
    return quicksort(lower) + equal + quicksort(higher)


def mergesort(values: list[T]) -> list[T]:
    """Return a sorted copy of ``values`` using mergesort."""

    items = list(values)
    if len(items) <= 1:
        return items

    middle = len(items) // 2
    left = mergesort(items[:middle])
    right = mergesort(items[middle:])
    return _merge(left, right)


def heapsort(values: list[T]) -> list[T]:
    """Return a sorted copy of ``values`` using heapsort."""

    heap = list(values)
    length = len(heap)
    for index in range(length // 2 - 1, -1, -1):
        _sift_down(heap, index, length)

    end = length - 1
    while end > 0:
        heap[0], heap[end] = heap[end], heap[0]
        _sift_down(heap, 0, end)
        end -= 1

    return heap


def radix_sort(values: list[int]) -> list[int]:
    """Return a sorted copy of integer ``values`` using LSD radix sort.

    Negative values are supported by sorting their absolute values separately
    and restoring sign/order afterward.
    """

    items = list(values)
    negatives = [-value for value in items if value < 0]
    non_negatives = [value for value in items if value >= 0]

    sorted_negatives = _radix_sort_non_negative(negatives)
    sorted_non_negatives = _radix_sort_non_negative(non_negatives)
    return [-value for value in reversed(sorted_negatives)] + sorted_non_negatives


def _merge(left: list[T], right: list[T]) -> list[T]:
    merged: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def _sift_down(heap: list[T], root: int, end: int) -> None:
    while True:
        child = 2 * root + 1
        if child >= end:
            return

        right_child = child + 1
        if right_child < end and heap[child] < heap[right_child]:
            child = right_child

        if heap[root] >= heap[child]:
            return

        heap[root], heap[child] = heap[child], heap[root]
        root = child


def _radix_sort_non_negative(values: list[int]) -> list[int]:
    if not values:
        return []

    result = list(values)
    max_value = max(result)
    exponent = 1
    while max_value // exponent > 0:
        buckets = [[] for _ in range(10)]
        for value in result:
            digit = (value // exponent) % 10
            buckets[digit].append(value)
        result = [value for bucket in buckets for value in bucket]
        exponent *= 10
    return result
