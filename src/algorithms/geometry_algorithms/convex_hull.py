"""Convex hull algorithms in two dimensions.

This module provides several classical ways to compute the convex hull of a
set of 2D points. The implementations return the hull boundary in
counter-clockwise order without repeating the first point at the end.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2


@dataclass(frozen=True, order=True, slots=True)
class Point2D:
    """A point in the two-dimensional plane."""

    x: float
    y: float


@dataclass(frozen=True, slots=True)
class GrahamScanStep:
    """Single step of Graham scan for teaching and visualization.

    ``action`` describes what happened:
    - ``"choose_pivot"``: the lowest point was selected
    - ``"sort_points"``: points were ordered by polar angle
    - ``"push"``: a point was added to the hull stack
    - ``"pop"``: the last point was removed because it made a non-left turn
    """

    action: str
    hull: tuple[Point2D, ...]
    current_point: Point2D | None = None
    popped_point: Point2D | None = None
    ordered_points: tuple[Point2D, ...] = ()


def monotonic_chain_convex_hull(points: list[Point2D]) -> list[Point2D]:
    """Compute the convex hull with Andrew's monotonic chain algorithm.

    Asymptotic complexity:
    - Sorting dominates the running time: ``O(n log n)``
    - The hull construction pass is linear: ``O(n)``
    - Total extra memory: ``O(n)``
    """

    unique = sorted(set(points))
    if len(unique) <= 1:
        return unique

    lower: list[Point2D] = []
    for point in unique:
        # Remove the last turn while the chain is not strictly counter-clockwise.
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[Point2D] = []
    for point in reversed(unique):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def graham_scan_convex_hull(points: list[Point2D]) -> list[Point2D]:
    """Compute the convex hull with Graham's scan.

    Asymptotic complexity:
    - Sorting by polar angle: ``O(n log n)``
    - Single scan over sorted points: ``O(n)``
    - Total extra memory: ``O(n)``
    """

    steps = graham_scan_steps(points)
    if not steps:
        return []
    return list(steps[-1].hull)


def graham_scan_steps(points: list[Point2D]) -> list[GrahamScanStep]:
    """Return a step-by-step trace of Graham's scan.

    Asymptotic complexity:
    - Sorting by polar angle: ``O(n log n)``
    - Single scan over sorted points: ``O(n)``
    - Total extra memory: ``O(n)``

    The returned steps are intended for study, debugging, and visualization.
    """

    unique = list(set(points))
    if not unique:
        return []
    if len(unique) == 1:
        return [GrahamScanStep(action="choose_pivot", hull=(unique[0],))]

    pivot = min(unique, key=lambda point: (point.y, point.x))
    steps = [GrahamScanStep(action="choose_pivot", hull=(pivot,), current_point=pivot)]

    others = [point for point in unique if point != pivot]
    others.sort(
        key=lambda point: (
            atan2(point.y - pivot.y, point.x - pivot.x),
            _distance_squared(pivot, point),
        )
    )

    filtered: list[Point2D] = []
    for point in others:
        while filtered and atan2(point.y - pivot.y, point.x - pivot.x) == atan2(
            filtered[-1].y - pivot.y, filtered[-1].x - pivot.x
        ):
            filtered.pop()
        filtered.append(point)

    steps.append(
        GrahamScanStep(
            action="sort_points",
            hull=(pivot,),
            ordered_points=tuple(filtered),
        )
    )

    if not filtered:
        return steps

    hull = [pivot]
    for point in filtered:
        while len(hull) >= 2 and _cross(hull[-2], hull[-1], point) <= 0:
            removed = hull.pop()
            steps.append(
                GrahamScanStep(
                    action="pop",
                    hull=tuple(hull),
                    current_point=point,
                    popped_point=removed,
                    ordered_points=tuple(filtered),
                )
            )
        hull.append(point)
        steps.append(
            GrahamScanStep(
                action="push",
                hull=tuple(hull),
                current_point=point,
                ordered_points=tuple(filtered),
            )
        )
    return steps


def jarvis_march_convex_hull(points: list[Point2D]) -> list[Point2D]:
    """Compute the convex hull with Jarvis march, also called gift wrapping.

    Asymptotic complexity:
    - Each hull vertex scans all points: ``O(nh)``
      where ``h`` is the number of hull vertices
    - In the worst case this becomes ``O(n^2)``
    - Extra memory usage is ``O(h)``
    """

    unique = list(set(points))
    if len(unique) <= 1:
        return unique

    start = min(unique, key=lambda point: (point.x, point.y))
    hull: list[Point2D] = []
    current = start

    while True:
        hull.append(current)
        candidate = unique[0] if unique[0] != current else unique[1]
        for point in unique:
            if point == current:
                continue
            turn = _cross(current, candidate, point)
            if turn < 0:
                candidate = point
            elif turn == 0 and _distance_squared(current, point) > _distance_squared(
                current, candidate
            ):
                candidate = point
        current = candidate
        if current == start:
            break
    return hull


def _cross(origin: Point2D, first: Point2D, second: Point2D) -> float:
    """Return the signed area of the turn ``origin -> first -> second``."""

    return (first.x - origin.x) * (second.y - origin.y) - (first.y - origin.y) * (
        second.x - origin.x
    )


def _distance_squared(first: Point2D, second: Point2D) -> float:
    """Return squared Euclidean distance to avoid unnecessary square roots."""

    dx = first.x - second.x
    dy = first.y - second.y
    return dx * dx + dy * dy
