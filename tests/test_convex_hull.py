from algorithms import (
    Point2D,
    graham_scan_convex_hull,
    jarvis_march_convex_hull,
    monotonic_chain_convex_hull,
)


def test_convex_hull_algorithms_agree_on_general_point_set() -> None:
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(3, 1),
        Point2D(2, 3),
        Point2D(0, 2),
        Point2D(1, 1),
        Point2D(2, 1),
        Point2D(1, 2),
        Point2D(0, 0),
    ]

    expected = {
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(3, 1),
        Point2D(2, 3),
        Point2D(0, 2),
    }

    for algorithm in (
        monotonic_chain_convex_hull,
        graham_scan_convex_hull,
        jarvis_march_convex_hull,
    ):
        hull = algorithm(points)
        assert set(hull) == expected
        assert len(hull) == len(expected)
        assert _is_counter_clockwise(hull)


def test_convex_hull_removes_inner_collinear_points() -> None:
    points = [
        Point2D(0, 0),
        Point2D(1, 0),
        Point2D(2, 0),
        Point2D(2, 2),
        Point2D(1, 2),
        Point2D(0, 2),
        Point2D(1, 1),
    ]
    expected = {Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)}

    assert set(monotonic_chain_convex_hull(points)) == expected
    assert set(graham_scan_convex_hull(points)) == expected
    assert set(jarvis_march_convex_hull(points)) == expected


def test_convex_hull_handles_small_inputs() -> None:
    empty: list[Point2D] = []
    one = [Point2D(1, 1)]
    two = [Point2D(1, 1), Point2D(2, 2)]

    for algorithm in (
        monotonic_chain_convex_hull,
        graham_scan_convex_hull,
        jarvis_march_convex_hull,
    ):
        assert algorithm(empty) == []
        assert algorithm(one) == one
        assert set(algorithm(two)) == set(two)


def _is_counter_clockwise(points: list[Point2D]) -> bool:
    if len(points) < 3:
        return True
    for index in range(len(points)):
        first = points[index]
        second = points[(index + 1) % len(points)]
        third = points[(index + 2) % len(points)]
        cross = (second.x - first.x) * (third.y - first.y) - (second.y - first.y) * (
            third.x - first.x
        )
        if cross <= 0:
            return False
    return True
