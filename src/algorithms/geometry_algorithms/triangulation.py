"""Delaunay triangulation and Voronoi diagram algorithms in two dimensions.

The Delaunay triangulation is implemented with the Bowyer-Watson incremental
algorithm. The Voronoi diagram is then built as the geometric dual of the
triangulation and clipped to a bounding box so it is easy to inspect and
visualize.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TypeAlias

from .convex_hull import Point2D

EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class Edge2D:
    """Undirected segment between two points."""

    start: Point2D
    end: Point2D


@dataclass(frozen=True, slots=True)
class Triangle2D:
    """Triangle in counter-clockwise order."""

    a: Point2D
    b: Point2D
    c: Point2D

    def edges(self) -> tuple[Edge2D, Edge2D, Edge2D]:
        """Return the three undirected edges of the triangle."""

        return (
            _normalized_edge(self.a, self.b),
            _normalized_edge(self.b, self.c),
            _normalized_edge(self.c, self.a),
        )

    def vertices(self) -> tuple[Point2D, Point2D, Point2D]:
        """Return the triangle vertices."""

        return self.a, self.b, self.c

    def circumcenter(self) -> Point2D:
        """Return the circumcenter of the triangle."""

        return _circumcenter(self)


@dataclass(frozen=True, slots=True)
class VoronoiEdge:
    """Finite clipped edge of a Voronoi diagram."""

    start: Point2D
    end: Point2D


@dataclass(frozen=True, slots=True)
class VoronoiDiagram:
    """Clipped Voronoi diagram representation."""

    vertices: tuple[Point2D, ...]
    edges: tuple[VoronoiEdge, ...]
    bounding_box: tuple[float, float, float, float]


_BoundingBox: TypeAlias = tuple[float, float, float, float]


def delaunay_triangulation(points: list[Point2D]) -> list[Triangle2D]:
    """Compute a Delaunay triangulation with Bowyer-Watson.

    Asymptotic complexity:
    - Average behavior is typically around ``O(n^2)`` in this simple
      implementation because each inserted point scans the current triangles.
    - The worst case remains quadratic or worse depending on point order.
    - Extra memory usage is ``O(n)`` for the active triangulation.
    """

    triangulation, _ = _bowyer_watson(points)
    return triangulation


def delaunay_triangulation_steps(points: list[Point2D]) -> list[list[Triangle2D]]:
    """Return incremental Bowyer-Watson triangulation states for visualization.

    Each entry contains the visible triangles after inserting the next point.
    This is useful for plotting how the triangulation evolves.
    """

    _, steps = _bowyer_watson(points)
    return steps


def voronoi_diagram(points: list[Point2D], *, padding: float = 0.25) -> VoronoiDiagram:
    """Build a clipped Voronoi diagram from the Delaunay triangulation.

    Asymptotic complexity:
    - Dominated by the triangulation step, which is ``O(n^2)`` here.
    - The dual construction over triangles and triangle adjacencies is linear
      in the triangulation size.
    """

    triangles = delaunay_triangulation(points)
    if not triangles:
        bounding_box = _compute_bounding_box(points, padding)
        return VoronoiDiagram(vertices=(), edges=(), bounding_box=bounding_box)

    bounding_box = _compute_bounding_box(points, padding)
    centers = {triangle: triangle.circumcenter() for triangle in triangles}
    edge_to_triangles: dict[Edge2D, list[Triangle2D]] = defaultdict(list)
    for triangle in triangles:
        for edge in triangle.edges():
            edge_to_triangles[edge].append(triangle)

    voronoi_edges: list[VoronoiEdge] = []
    vertices: set[Point2D] = set()

    for edge, incident in edge_to_triangles.items():
        if len(incident) == 2:
            first_center = centers[incident[0]]
            second_center = centers[incident[1]]
            if first_center != second_center:
                voronoi_edges.append(VoronoiEdge(first_center, second_center))
                vertices.add(first_center)
                vertices.add(second_center)
            continue

        triangle = incident[0]
        center = centers[triangle]
        endpoint = _clip_hull_ray(center, triangle, edge, bounding_box)
        if endpoint is None or endpoint == center:
            continue
        voronoi_edges.append(VoronoiEdge(center, endpoint))
        vertices.add(center)
        vertices.add(endpoint)

    return VoronoiDiagram(
        vertices=tuple(sorted(vertices)),
        edges=tuple(voronoi_edges),
        bounding_box=bounding_box,
    )


def _bowyer_watson(
    points: list[Point2D],
) -> tuple[list[Triangle2D], list[list[Triangle2D]]]:
    unique = sorted(set(points))
    if len(unique) < 3 or _are_collinear(unique):
        return [], []

    super_triangle = _build_super_triangle(unique)
    super_vertices = set(super_triangle.vertices())
    triangles = [super_triangle]
    steps: list[list[Triangle2D]] = []

    for point in unique:
        bad_triangles = [
            triangle
            for triangle in triangles
            if _circumcircle_contains(triangle, point)
        ]
        boundary_counts: dict[Edge2D, int] = defaultdict(int)
        for triangle in bad_triangles:
            for edge in triangle.edges():
                boundary_counts[edge] += 1

        triangles = [
            triangle for triangle in triangles if triangle not in bad_triangles
        ]

        for edge, count in boundary_counts.items():
            if count != 1:
                continue
            new_triangle = _make_triangle(edge.start, edge.end, point)
            if new_triangle is not None:
                triangles.append(new_triangle)

        steps.append(
            [
                triangle
                for triangle in triangles
                if not any(vertex in super_vertices for vertex in triangle.vertices())
            ]
        )

    final = [
        triangle
        for triangle in triangles
        if not any(vertex in super_vertices for vertex in triangle.vertices())
    ]
    return final, steps


def _make_triangle(
    first: Point2D, second: Point2D, third: Point2D
) -> Triangle2D | None:
    area = _cross(first, second, third)
    if abs(area) <= EPSILON:
        return None
    if area < 0:
        return Triangle2D(first, third, second)
    return Triangle2D(first, second, third)


def _build_super_triangle(points: list[Point2D]) -> Triangle2D:
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)

    delta = max(max_x - min_x, max_y - min_y)
    if delta <= EPSILON:
        delta = 1.0
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    triangle = _make_triangle(
        Point2D(mid_x - 20 * delta, mid_y - delta),
        Point2D(mid_x, mid_y + 20 * delta),
        Point2D(mid_x + 20 * delta, mid_y - delta),
    )
    if triangle is None:
        raise RuntimeError("failed to build a valid super-triangle")
    return triangle


def _circumcircle_contains(triangle: Triangle2D, point: Point2D) -> bool:
    ax = triangle.a.x - point.x
    ay = triangle.a.y - point.y
    bx = triangle.b.x - point.x
    by = triangle.b.y - point.y
    cx = triangle.c.x - point.x
    cy = triangle.c.y - point.y

    determinant = (
        (ax * ax + ay * ay) * (bx * cy - by * cx)
        - (bx * bx + by * by) * (ax * cy - ay * cx)
        + (cx * cx + cy * cy) * (ax * by - ay * bx)
    )
    return determinant > EPSILON


def _circumcenter(triangle: Triangle2D) -> Point2D:
    ax, ay = triangle.a.x, triangle.a.y
    bx, by = triangle.b.x, triangle.b.y
    cx, cy = triangle.c.x, triangle.c.y

    denominator = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(denominator) <= EPSILON:
        raise ValueError("circumcenter is undefined for collinear points")

    ux = (
        (ax * ax + ay * ay) * (by - cy)
        + (bx * bx + by * by) * (cy - ay)
        + (cx * cx + cy * cy) * (ay - by)
    ) / denominator
    uy = (
        (ax * ax + ay * ay) * (cx - bx)
        + (bx * bx + by * by) * (ax - cx)
        + (cx * cx + cy * cy) * (bx - ax)
    ) / denominator
    return Point2D(ux, uy)


def _compute_bounding_box(points: list[Point2D], padding: float) -> _BoundingBox:
    if not points:
        return (-1.0, 1.0, -1.0, 1.0)

    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)

    scale = max(max_x - min_x, max_y - min_y)
    if scale <= EPSILON:
        scale = 1.0
    pad = scale * padding
    return min_x - pad, max_x + pad, min_y - pad, max_y + pad


def _clip_hull_ray(
    center: Point2D,
    triangle: Triangle2D,
    edge: Edge2D,
    bounding_box: _BoundingBox,
) -> Point2D | None:
    midpoint = Point2D(
        (edge.start.x + edge.end.x) / 2,
        (edge.start.y + edge.end.y) / 2,
    )
    third = next(
        vertex
        for vertex in triangle.vertices()
        if vertex != edge.start and vertex != edge.end
    )
    dx = edge.end.x - edge.start.x
    dy = edge.end.y - edge.start.y
    normal = Point2D(dy, -dx)
    toward_third = Point2D(third.x - midpoint.x, third.y - midpoint.y)
    if normal.x * toward_third.x + normal.y * toward_third.y > 0:
        normal = Point2D(-normal.x, -normal.y)

    return _ray_box_intersection(center, normal, bounding_box)


def _ray_box_intersection(
    origin: Point2D, direction: Point2D, bounding_box: _BoundingBox
) -> Point2D | None:
    min_x, max_x, min_y, max_y = bounding_box
    candidates: list[tuple[float, Point2D]] = []

    if abs(direction.x) > EPSILON:
        for boundary_x in (min_x, max_x):
            t = (boundary_x - origin.x) / direction.x
            if t > EPSILON:
                y = origin.y + t * direction.y
                if min_y - EPSILON <= y <= max_y + EPSILON:
                    candidates.append((t, Point2D(boundary_x, y)))

    if abs(direction.y) > EPSILON:
        for boundary_y in (min_y, max_y):
            t = (boundary_y - origin.y) / direction.y
            if t > EPSILON:
                x = origin.x + t * direction.x
                if min_x - EPSILON <= x <= max_x + EPSILON:
                    candidates.append((t, Point2D(x, boundary_y)))

    if not candidates:
        return None
    return min(candidates, key=lambda item: item[0])[1]


def _normalized_edge(first: Point2D, second: Point2D) -> Edge2D:
    if second < first:
        first, second = second, first
    return Edge2D(first, second)


def _cross(origin: Point2D, first: Point2D, second: Point2D) -> float:
    return (first.x - origin.x) * (second.y - origin.y) - (first.y - origin.y) * (
        second.x - origin.x
    )


def _are_collinear(points: list[Point2D]) -> bool:
    if len(points) < 3:
        return True
    first = points[0]
    second = points[1]
    return all(abs(_cross(first, second, point)) <= EPSILON for point in points[2:])
