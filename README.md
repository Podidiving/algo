# algorithms

`algorithms` is a study-oriented Python library with classic data structures
and algorithms implemented in a readable way. The goal of the project is not
to hide the ideas behind a large framework, but to provide compact reference
implementations you can inspect, run, and test while learning.

## Purpose

Use this library for studying:

- balanced and unbalanced tree structures
- range-query data structures
- graph algorithms
- sorting algorithms

The code aims to stay practical and explicit, with documentation, comments,
and tests for each major implementation.

## Installation

### With `uv`

```bash
uv sync
```

Run examples or your own scripts with:

```bash
uv run python your_script.py
```

### With `pip`

From the repository root:

```bash
pip install .
```

If you want to work on the project itself and run tests:

```bash
pip install -e .
pip install pytest
```

## Running tests

```bash
uv run --group dev pytest
```

## Basic usage

Import directly from the top-level package:

```python
from algorithms import Treap, RMQ, WeightedEdge, dijkstra_shortest_paths
```

## Data structures

### Treap

```python
from algorithms import Treap

treap = Treap([(3, "c"), (1, "a"), (2, "b")])

treap.insert(4, "d")
print(list(treap.items()))
print(treap.rank(3))
print(treap.kth(0).key)
```

### Implicit Treap

```python
from algorithms import ImplicitTreap

sequence = ImplicitTreap(["a", "b", "d"])
sequence.insert(2, "c")
sequence.append("e")

print(sequence.to_list())
print(sequence.get(3))
```

### BST and AVL Tree

```python
from algorithms import BST, AVLTree

bst = BST([(5, "x"), (2, "y"), (8, "z")])
avl = AVLTree([(5, "x"), (2, "y"), (8, "z")])

print(bst.get(2))
print(avl.lower_bound(6).key)
```

### Segment Tree

```python
import operator

from algorithms import SegmentTree

tree = SegmentTree([2, 1, 3, 4, 5], combine=operator.add, identity=0)

print(tree.query(1, 4))
tree.update(3, 10)
print(tree.query())
```

### Disjoint Set Union

```python
from algorithms import DisjointSet

dsu = DisjointSet(["a", "b", "c", "d"])
dsu.union("a", "b")
dsu.union("b", "c")

print(dsu.connected("a", "c"))
print(dsu.component_size("a"))
print(dsu.groups())
```

## Range queries

### RMQ

`RMQ` uses the segment tree internally and supports minimum queries with point
updates.

```python
from algorithms import RMQ

rmq = RMQ([5, 2, 7, 1, 3])

print(rmq.query(1, 4))
print(rmq.argmin())

rmq.update(3, 6)
print(rmq.query_with_index())
```

## Graph algorithms

### Minimum spanning tree

```python
from algorithms import WeightedEdge, kruskal_mst, prim_mst

vertices = ["A", "B", "C", "D"]
edges = [
    WeightedEdge(1, "A", "B"),
    WeightedEdge(4, "A", "C"),
    WeightedEdge(2, "B", "C"),
    WeightedEdge(3, "B", "D"),
]

prim_result = prim_mst(vertices, edges)
kruskal_result = kruskal_mst(vertices, edges)

print(prim_result.total_weight)
print(kruskal_result.edges)
```

### Dijkstra

```python
from algorithms import WeightedEdge, dijkstra_shortest_paths

vertices = ["A", "B", "C", "D"]
edges = [
    WeightedEdge(1, "A", "B"),
    WeightedEdge(4, "A", "C"),
    WeightedEdge(2, "B", "C"),
    WeightedEdge(5, "C", "D"),
]

result = dijkstra_shortest_paths(vertices, edges, "A")

print(result.distance_to("D"))
print(result.path_to("D"))
```

### Bellman-Ford

```python
from algorithms import WeightedEdge, bellman_ford_shortest_paths

vertices = ["S", "A", "B", "C"]
edges = [
    WeightedEdge(4, "S", "A"),
    WeightedEdge(5, "S", "B"),
    WeightedEdge(-2, "A", "C"),
    WeightedEdge(3, "B", "C"),
]

result = bellman_ford_shortest_paths(vertices, edges, "S", directed=True)

print(result.distance_to("C"))
print(result.path_to("C"))
```

### Floyd-Warshall

```python
from algorithms import WeightedEdge, floyd_warshall_shortest_paths

vertices = ["A", "B", "C"]
edges = [
    WeightedEdge(3, "A", "B"),
    WeightedEdge(1, "B", "C"),
    WeightedEdge(10, "A", "C"),
]

result = floyd_warshall_shortest_paths(vertices, edges, directed=True)

print(result.distance("A", "C"))
print(result.path("A", "C"))
```

## Sorting algorithms

```python
from algorithms import heapsort, mergesort, quicksort, radix_sort

values = [5, 1, 9, 3, 3, 0, -2, 8, 4]

print(quicksort(values))
print(mergesort(values))
print(heapsort(values))
print(radix_sort(values))
```

## What is included

- `data_structures`
  - `Treap`
  - `ImplicitTreap`
  - `BST`
  - `AVLTree`
  - `SegmentTree`
  - `DisjointSet`
- `range_queries`
  - `RMQ`
- `graph_algorithms`
  - `prim_mst`
  - `kruskal_mst`
  - `dijkstra_shortest_paths`
  - `bellman_ford_shortest_paths`
  - `floyd_warshall_shortest_paths`
- `sorting_algorithms`
  - `quicksort`
  - `mergesort`
  - `heapsort`
  - `radix_sort`

## Notes

- The library is meant for learning and experimentation first.
- The implementations are tested, but the main value here is readability and
  study, not replacing specialized production libraries.
- Most APIs return plain Python data structures or small dataclasses to keep
  usage simple.
