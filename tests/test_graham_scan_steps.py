from algorithms import Point2D, graham_scan_convex_hull, graham_scan_steps


def test_graham_scan_steps_end_with_final_hull() -> None:
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(3, 1),
        Point2D(2, 3),
        Point2D(0, 2),
        Point2D(1, 1),
    ]

    steps = graham_scan_steps(points)

    assert steps[0].action == "choose_pivot"
    assert steps[1].action == "sort_points"
    assert list(steps[-1].hull) == graham_scan_convex_hull(points)


def test_graham_scan_steps_include_pop_when_point_is_inside_turn() -> None:
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(1, 0.2),
        Point2D(2, 2),
        Point2D(0, 2),
    ]

    steps = graham_scan_steps(points)

    assert any(step.action == "pop" for step in steps)
