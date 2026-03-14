from algorithms import Point2D, jarvis_march_convex_hull, jarvis_march_steps


def test_jarvis_march_steps_end_with_final_hull() -> None:
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(3, 1),
        Point2D(2, 3),
        Point2D(0, 2),
        Point2D(1, 1),
    ]

    steps = jarvis_march_steps(points)
    committed = [
        step.current_point
        for step in steps
        if step.action == "commit_hull_point" and step.current_point is not None
    ]

    assert steps[0].action == "choose_start"
    assert committed[-1] == committed[0]
    assert committed[:-1] == jarvis_march_convex_hull(points)


def test_jarvis_march_steps_include_candidate_updates() -> None:
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(3, 1),
        Point2D(1, 2),
        Point2D(0, 2),
    ]

    steps = jarvis_march_steps(points)

    assert any(step.action == "consider_candidate" for step in steps)
    assert any(step.action == "update_candidate" for step in steps)
