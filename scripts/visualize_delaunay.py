"""Visualize the incremental Bowyer-Watson Delaunay triangulation process.

Run with:

    uv run --group viz python scripts/visualize_delaunay.py
"""

from __future__ import annotations

import argparse
import math
import random

import matplotlib.pyplot as plt

from algorithms import Point2D, delaunay_triangulation_steps


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show how Delaunay triangulation evolves step by step."
    )
    parser.add_argument("--count", type=int, default=9, help="Number of random points.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    points = [
        Point2D(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(args.count)
    ]
    steps = delaunay_triangulation_steps(points)

    _print_explanation(points, steps, args.seed)

    columns = 3
    rows = math.ceil(max(1, len(steps)) / columns)
    figure, axes = plt.subplots(rows, columns, figsize=(5 * columns, 4 * rows))
    axes_list = list(axes.flat) if hasattr(axes, "flat") else [axes]

    x_values = [point.x for point in points]
    y_values = [point.y for point in points]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    padding = max(max_x - min_x, max_y - min_y, 1.0) * 0.1

    for index, axis in enumerate(axes_list):
        if index >= len(steps):
            axis.axis("off")
            continue

        inserted = points[: index + 1]
        triangles = steps[index]

        for triangle in triangles:
            xs = [triangle.a.x, triangle.b.x, triangle.c.x, triangle.a.x]
            ys = [triangle.a.y, triangle.b.y, triangle.c.y, triangle.a.y]
            axis.plot(xs, ys, color="steelblue", linewidth=1.2)

        axis.scatter(
            [point.x for point in inserted],
            [point.y for point in inserted],
            color="crimson",
            zorder=3,
        )
        axis.set_title(f"Step {index + 1}")
        axis.set_xlim(min_x - padding, max_x + padding)
        axis.set_ylim(min_y - padding, max_y + padding)
        axis.set_aspect("equal", adjustable="box")
        axis.grid(alpha=0.25)

    figure.suptitle("Incremental Delaunay triangulation (Bowyer-Watson)")
    figure.tight_layout()
    plt.show()


def _print_explanation(
    points: list[Point2D], steps: list[list[object]], seed: int
) -> None:
    print("Delaunay triangulation visualization")
    print()
    print("This script shows the Bowyer-Watson incremental algorithm.")
    print("The main idea is:")
    print("1. Start from a very large triangle that contains all points.")
    print("2. Insert points one by one.")
    print("3. For each new point, find triangles whose circumcircles contain it.")
    print("4. Remove those triangles to create a polygonal cavity.")
    print("5. Connect the new point to the cavity boundary.")
    print("6. After all insertions, remove triangles touching the super-triangle.")
    print()
    print("The plot shows the visible triangulation after each inserted point.")
    print("Inserted points are red, triangulation edges are blue.")
    print()
    print(f"Random seed: {seed}")
    print(f"Number of generated points: {len(points)}")
    print("Insertion order:")
    for index, point in enumerate(points, start=1):
        triangle_count = len(steps[index - 1]) if index - 1 < len(steps) else 0
        print(
            f"  Step {index}: insert ({point.x:.3f}, {point.y:.3f}) "
            f"-> {triangle_count} visible triangle(s)"
        )
    print()
    print("Close the plot window when you are done inspecting the triangulation.")


if __name__ == "__main__":
    main()
