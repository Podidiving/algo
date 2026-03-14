"""Visualize Jarvis march step by step.

Run with:

    uv run --group viz python scripts/visualize_jarvis_march.py
"""

from __future__ import annotations

import argparse
import math
import random

import matplotlib.pyplot as plt

from algorithms import JarvisMarchStep, Point2D, jarvis_march_steps


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show Jarvis march one candidate update at a time."
    )
    parser.add_argument("--count", type=int, default=4, help="Number of random points.")
    parser.add_argument("--seed", type=int, default=5, help="Random seed.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    points = [
        Point2D(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(args.count)
    ]
    steps = jarvis_march_steps(points)

    _print_explanation(points, steps, args.seed)
    _plot_steps(points, steps)


def _plot_steps(points: list[Point2D], steps: list[JarvisMarchStep]) -> None:
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

        if len(step.hull) >= 2:
            axis.plot(
                [point.x for point in step.hull],
                [point.y for point in step.hull],
                color="steelblue",
                linewidth=1.6,
                zorder=2,
            )
        if step.hull:
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

        if step.candidate_point is not None:
            axis.scatter(
                [step.candidate_point.x],
                [step.candidate_point.y],
                color="forestgreen",
                s=70,
                zorder=5,
            )
            if step.current_point is not None:
                axis.plot(
                    [step.current_point.x, step.candidate_point.x],
                    [step.current_point.y, step.candidate_point.y],
                    color="forestgreen",
                    linestyle="--",
                    linewidth=1.1,
                    zorder=4,
                )

        if step.challenger_point is not None:
            axis.scatter(
                [step.challenger_point.x],
                [step.challenger_point.y],
                color="goldenrod",
                marker="x",
                s=90,
                zorder=6,
            )

        axis.set_title(f"Step {index + 1}: {step.action}")
        axis.set_xlim(min_x - padding, max_x + padding)
        axis.set_ylim(min_y - padding, max_y + padding)
        axis.set_aspect("equal", adjustable="box")
        axis.grid(alpha=0.25)

    figure.suptitle("Jarvis march step-by-step")
    figure.tight_layout()
    plt.show()


def _print_explanation(
    points: list[Point2D], steps: list[JarvisMarchStep], seed: int
) -> None:
    print("Jarvis march step-by-step visualization")
    print()
    print("This script disassembles Jarvis march into candidate comparisons.")
    print("High-level process:")
    print("1. Choose the leftmost point as the start.")
    print("2. From the current hull point, scan all other points.")
    print("3. Keep the point that makes the most counter-clockwise turn.")
    print("4. Commit that point as the next hull vertex.")
    print("5. Repeat until the algorithm returns to the start point.")
    print()
    print("Asymptotic complexity: O(nh), where h is the hull size.")
    print(f"Random seed: {seed}")
    print(f"Number of generated points: {len(points)}")
    print()
    for index, step in enumerate(steps, start=1):
        print(f"Step {index:02d}: {_step_description(step)}")
    print()
    print("In the plots:")
    print("- blue polyline = hull points committed so far")
    print("- red point = current hull point")
    print("- green point/segment = current best candidate")
    print("- yellow x = challenger point being tested")
    print()
    print("Close the plot window when you are done.")


def _step_description(step: JarvisMarchStep) -> str:
    if step.action == "choose_start" and step.current_point is not None:
        return (
            f"choose start at ({step.current_point.x:.3f}, {step.current_point.y:.3f})"
        )
    if step.action == "commit_hull_point" and step.current_point is not None:
        return (
            f"commit ({step.current_point.x:.3f}, {step.current_point.y:.3f}) "
            f"as hull vertex {len(step.hull)}"
        )
    if (
        step.action == "consider_candidate"
        and step.current_point is not None
        and step.candidate_point is not None
        and step.challenger_point is not None
    ):
        return (
            f"compare challenger ({step.challenger_point.x:.3f}, {step.challenger_point.y:.3f}) "
            f"against candidate ({step.candidate_point.x:.3f}, {step.candidate_point.y:.3f})"
        )
    if step.action == "update_candidate" and step.candidate_point is not None:
        return f"update candidate to ({step.candidate_point.x:.3f}, {step.candidate_point.y:.3f})"
    return step.action


if __name__ == "__main__":
    main()
