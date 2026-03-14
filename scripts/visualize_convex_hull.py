"""Visualize convex hull algorithms on a random 2D point set.

Run with:

    uv run --group viz python scripts/visualize_convex_hull.py
"""

from __future__ import annotations

import argparse
import math
import random

import matplotlib.pyplot as plt

from algorithms import (
    Point2D,
    graham_scan_convex_hull,
    jarvis_march_convex_hull,
    monotonic_chain_convex_hull,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare convex hull algorithms on the same point set."
    )
    parser.add_argument(
        "--count", type=int, default=12, help="Number of random points."
    )
    parser.add_argument("--seed", type=int, default=11, help="Random seed.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    points = [
        Point2D(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(args.count)
    ]

    hulls = {
        "Monotonic chain": monotonic_chain_convex_hull(points),
        "Graham scan": graham_scan_convex_hull(points),
        "Jarvis march": jarvis_march_convex_hull(points),
    }

    _print_explanation(points, hulls, args.seed)

    figure, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    x_values = [point.x for point in points]
    y_values = [point.y for point in points]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    padding = max(max_x - min_x, max_y - min_y, 1.0) * 0.1

    for axis, (title, hull) in zip(axes, hulls.items(), strict=True):
        axis.scatter(x_values, y_values, color="crimson", zorder=3)
        if hull:
            closed = hull + [hull[0]]
            axis.plot(
                [point.x for point in closed],
                [point.y for point in closed],
                color="steelblue",
                linewidth=1.5,
            )
        axis.set_title(title)
        axis.set_xlim(min_x - padding, max_x + padding)
        axis.set_ylim(min_y - padding, max_y + padding)
        axis.set_aspect("equal", adjustable="box")
        axis.grid(alpha=0.25)

    figure.suptitle("Convex hull comparison on the same point set")
    figure.tight_layout()
    plt.show()


def _print_explanation(
    points: list[Point2D], hulls: dict[str, list[Point2D]], seed: int
) -> None:
    print("Convex hull visualization")
    print()
    print("This script compares three classical 2D convex hull algorithms:")
    print("1. Monotonic chain: sort points, then build lower and upper hulls.")
    print("2. Graham scan: sort by polar angle around a pivot, then scan.")
    print("3. Jarvis march: wrap the hull one boundary point at a time.")
    print()
    print("Asymptotics:")
    print("  Monotonic chain: O(n log n)")
    print("  Graham scan:     O(n log n)")
    print("  Jarvis march:    O(nh), where h is the hull size")
    print()
    print(f"Random seed: {seed}")
    print(f"Number of generated points: {len(points)}")
    print("Generated points:")
    for index, point in enumerate(points, start=1):
        print(f"  {index:02d}. ({point.x:.3f}, {point.y:.3f})")
    print()
    for name, hull in hulls.items():
        print(f"{name}:")
        print(f"  hull size = {len(hull)}")
        if hull:
            print("  boundary order:")
            for point in hull:
                print(f"    ({point.x:.3f}, {point.y:.3f})")
    print()
    print("Each subplot shows the same points and the hull found by one algorithm.")
    print("Close the plot window when you are done.")


if __name__ == "__main__":
    main()
