"""Visualize Graham scan step by step.

Run with:

    uv run --group viz python scripts/visualize_graham_scan.py
"""

from __future__ import annotations

import argparse
import math
import random

import matplotlib.pyplot as plt

from algorithms import GrahamScanStep, Point2D, graham_scan_steps


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show Graham scan one stack operation at a time."
    )
    parser.add_argument(
        "--count", type=int, default=10, help="Number of random points."
    )
    parser.add_argument("--seed", type=int, default=13, help="Random seed.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    points = [
        Point2D(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(args.count)
    ]
    steps = graham_scan_steps(points)

    _print_explanation(points, steps, args.seed)
    _plot_steps(points, steps)


def _plot_steps(points: list[Point2D], steps: list[GrahamScanStep]) -> None:
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

        step = steps[index]
        axis.scatter(x_values, y_values, color="lightgray", zorder=1)

        if step.ordered_points:
            axis.scatter(
                [point.x for point in step.ordered_points],
                [point.y for point in step.ordered_points],
                color="silver",
                zorder=1,
            )

        if step.hull:
            axis.plot(
                [point.x for point in step.hull],
                [point.y for point in step.hull],
                color="steelblue",
                linewidth=1.6,
                zorder=2,
            )
            axis.scatter(
                [point.x for point in step.hull],
                [point.y for point in step.hull],
                color="steelblue",
                zorder=3,
            )

        if step.current_point is not None:
            axis.scatter(
                [step.current_point.x],
                [step.current_point.y],
                color="crimson",
                s=70,
                zorder=4,
            )

        if step.popped_point is not None:
            axis.scatter(
                [step.popped_point.x],
                [step.popped_point.y],
                color="goldenrod",
                marker="x",
                s=90,
                zorder=5,
            )

        axis.set_title(_step_title(index + 1, step))
        axis.set_xlim(min_x - padding, max_x + padding)
        axis.set_ylim(min_y - padding, max_y + padding)
        axis.set_aspect("equal", adjustable="box")
        axis.grid(alpha=0.25)

    figure.suptitle("Graham scan step-by-step")
    figure.tight_layout()
    plt.show()


def _print_explanation(
    points: list[Point2D], steps: list[GrahamScanStep], seed: int
) -> None:
    print("Graham scan step-by-step visualization")
    print()
    print("This script disassembles Graham scan into stack operations.")
    print("High-level process:")
    print("1. Choose the pivot: the lowest point, breaking ties by x.")
    print("2. Sort all other points by polar angle around the pivot.")
    print("3. Scan in that order while maintaining a hull stack.")
    print("4. If the last turn is not counter-clockwise, pop the stack.")
    print("5. Push the current point after all bad turns are removed.")
    print()
    print("Asymptotic complexity: O(n log n) because sorting dominates the scan.")
    print(f"Random seed: {seed}")
    print(f"Number of generated points: {len(points)}")
    print()
    for index, step in enumerate(steps, start=1):
        print(f"Step {index:02d}: {_step_description(step)}")
    print()
    print("In the plots:")
    print("- blue polyline = current hull stack")
    print("- red point = current point under consideration")
    print("- yellow x = point popped from the stack")
    print()
    print("Close the plot window when you are done.")


def _step_title(index: int, step: GrahamScanStep) -> str:
    return f"Step {index}: {step.action}"


def _step_description(step: GrahamScanStep) -> str:
    if step.action == "choose_pivot" and step.current_point is not None:
        return (
            f"choose pivot at ({step.current_point.x:.3f}, {step.current_point.y:.3f})"
        )
    if step.action == "sort_points":
        return f"sort {len(step.ordered_points)} point(s) by polar angle"
    if step.action == "push" and step.current_point is not None:
        return (
            f"push ({step.current_point.x:.3f}, {step.current_point.y:.3f}); "
            f"hull size is now {len(step.hull)}"
        )
    if (
        step.action == "pop"
        and step.current_point is not None
        and step.popped_point is not None
    ):
        return (
            f"pop ({step.popped_point.x:.3f}, {step.popped_point.y:.3f}) "
            f"because of current point ({step.current_point.x:.3f}, {step.current_point.y:.3f})"
        )
    return step.action


if __name__ == "__main__":
    main()
