from algorithms import (
    Point2D,
    delaunay_triangulation,
    delaunay_triangulation_steps,
    voronoi_diagram,
)


def test_delaunay_triangulation_handles_basic_triangle() -> None:
    points = [Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)]

    triangles = delaunay_triangulation(points)

    assert len(triangles) == 1
    assert set(triangles[0].vertices()) == set(points)


def test_delaunay_triangulation_on_square_satisfies_empty_circumcircle_property() -> (
    None
):
    points = [
        Point2D(0, 0),
        Point2D(1, 0),
        Point2D(1, 1),
        Point2D(0, 1),
    ]

    triangles = delaunay_triangulation(points)

    assert len(triangles) == 2
    for triangle in triangles:
        center = triangle.circumcenter()
        radius_squared = _distance_squared(center, triangle.a)
        for point in points:
            if point in triangle.vertices():
                continue
            assert _distance_squared(center, point) >= radius_squared - 1e-9


def test_delaunay_triangulation_steps_grow_incrementally() -> None:
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(1, 1),
        Point2D(0, 2),
    ]

    steps = delaunay_triangulation_steps(points)

    assert len(steps) == len(set(points))
    assert steps[-1] == delaunay_triangulation(points)


def test_voronoi_diagram_for_square_has_center_and_four_clipped_rays() -> None:
    points = [
        Point2D(0, 0),
        Point2D(1, 0),
        Point2D(1, 1),
        Point2D(0, 1),
    ]

    diagram = voronoi_diagram(points)

    assert Point2D(0.5, 0.5) in diagram.vertices
    assert len(diagram.edges) == 4
    min_x, max_x, min_y, max_y = diagram.bounding_box
    for edge in diagram.edges:
        assert edge.start == Point2D(0.5, 0.5)
        assert (
            abs(edge.end.x - min_x) < 1e-9
            or abs(edge.end.x - max_x) < 1e-9
            or abs(edge.end.y - min_y) < 1e-9
            or abs(edge.end.y - max_y) < 1e-9
        )


def test_voronoi_diagram_is_empty_for_collinear_points() -> None:
    points = [Point2D(0, 0), Point2D(1, 0), Point2D(2, 0)]

    diagram = voronoi_diagram(points)

    assert diagram.vertices == ()
    assert diagram.edges == ()


def _distance_squared(first: Point2D, second: Point2D) -> float:
    dx = first.x - second.x
    dy = first.y - second.y
    return dx * dx + dy * dy
