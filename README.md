# algorithms

`algorithms` is a study-oriented Python library with classic data structures
and algorithms implemented in a readable way. The goal is to provide compact
reference implementations you can inspect, run, and test while learning.

## Purpose

Use this library for studying:

- balanced and unbalanced tree structures
- range-query data structures
- graph algorithms
- geometry algorithms
- string algorithms
- sorting algorithms

The code aims to stay explicit and educational. Each major implementation has
tests, and most modules include comments and short docs explaining how they
work.

## Installation

### With `uv`

```bash
uv sync
```

Run examples or your own scripts with:

```bash
uv run python your_script.py
```

If you want to run visualization scripts:

```bash
uv sync --group viz
uv run --group viz python scripts/visualize_delaunay.py
```

### With `pip`

From the repository root:

```bash
pip install .
```

For local development:

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

Complexity:

- `insert`, `remove`, `discard`, `get`, `find_node`, `lower_bound`, `upper_bound`, `predecessor`, `successor`, `rank`, `kth`: expected `O(log n)` time
- `split`, `merge`: expected `O(log n)` time
- `min_node`, `max_node`, `pop_min`, `pop_max`: expected `O(log n)` time
- `items`, `keys`, `values`, `inorder`: `O(n)` total iteration time
- space: `O(n)`

### Implicit Treap

```python
from algorithms import ImplicitTreap

sequence = ImplicitTreap(["a", "b", "d"])
sequence.insert(2, "c")
sequence.append("e")

print(sequence.to_list())
print(sequence.get(3))
```

Complexity:

- `insert`, `append`, `prepend`, `remove`, `pop`, `get`, `set`, `get_node`, `index_of`, `split`, `merge`: expected `O(log n)` time
- `to_list`, iteration: `O(n)`
- space: `O(n)`

### BST

```python
from algorithms import BST

bst = BST([(5, "x"), (2, "y"), (8, "z")])

print(bst.get(2))
print(bst.lower_bound(6))
```

Complexity:

- all search/update operations are `O(h)` time, where `h` is the current tree height
- worst-case `h = n`, so worst-case time is `O(n)` for `insert`, `remove`, `get`, `rank`, `kth`, bounds, predecessor/successor
- iteration and `to_list`-style traversal work: `O(n)`
- space: `O(n)`

### AVL Tree

```python
from algorithms import AVLTree

avl = AVLTree([(5, "x"), (2, "y"), (8, "z")])

print(avl.lower_bound(6).key)
print(avl.rank(8))
```

Complexity:

- `insert`, `remove`, `discard`, `get`, `find_node`, bounds, predecessor/successor, `rank`, `kth`: `O(log n)` time
- `min_node`, `max_node`, `pop_min`, `pop_max`: `O(log n)` time
- iteration and traversal: `O(n)`
- space: `O(n)`

### Red-Black Tree

```python
from algorithms import RedBlackTree

rbt = RedBlackTree([(5, "x"), (2, "y"), (8, "z")])

print(rbt.rank(8))
print(rbt.successor(2).key)
```

Complexity:

- `insert`, `remove`, `discard`, `get`, `find_node`, bounds, predecessor/successor, `rank`, `kth`: `O(log n)` time
- `min_node`, `max_node`, `pop_min`, `pop_max`: `O(log n)` time
- iteration and traversal: `O(n)`
- space: `O(n)`

### Segment Tree

```python
import operator

from algorithms import SegmentTree

tree = SegmentTree([2, 1, 3, 4, 5], combine=operator.add, identity=0)

print(tree.query(1, 4))
tree.update(3, 10)
print(tree.query())
```

Complexity:

- build: `O(n)` time
- `query`, `update`: `O(log n)` time
- indexing: `O(1)` time
- `to_list`, iteration: `O(n)`
- space: `O(n)`

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

Complexity:

- `add`: amortized `O(1)` time
- `find`, `union`, `connected`, `component_size`: amortized `O(alpha(n))` time
- `groups`: `O(n alpha(n))` time
- space: `O(n)`

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

Complexity:

- build: `O(n)` time
- `query`, `argmin`, `query_with_index`, `update`: `O(log n)` time
- indexing: `O(1)` time
- `to_list`, iteration: `O(n)`
- space: `O(n)`

## Graph algorithms

### BFS and DFS

```python
from algorithms import bfs_traversal, dfs_traversal

graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"],
}

print(bfs_traversal(graph, "A"))
print(dfs_traversal(graph, "A"))
```

Complexity:

- `bfs_traversal`, `dfs_traversal`: `O(V + E)` time, `O(V)` extra space
- `connected_components`: `O(V + E)` time, `O(V)` extra space

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

Complexity:

- `prim_mst`: `O(E log E)` time in this heap-based implementation, `O(V + E)` space
- `kruskal_mst`: `O(E log E)` time because of sorting, `O(V + E)` space

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

Complexity:

- `dijkstra_shortest_paths`: `O((V + E) log V)` time, `O(V + E)` space
- `distance_to`: `O(1)` time
- `path_to`: `O(length of returned path)` time and space

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

Complexity:

- `bellman_ford_shortest_paths`: `O(VE)` time, `O(V)` extra space beyond the edge list
- `distance_to`: `O(1)` time
- `path_to`: `O(length of returned path)` time and space

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

Complexity:

- `floyd_warshall_shortest_paths`: `O(V^3)` time, `O(V^2)` space
- `distance`: `O(1)` time
- `path`: `O(length of returned path)` time and space

## String algorithms

### Prefix function and KMP

```python
from algorithms import compute_prefix_function, kmp_search

pattern = "ababa"
text = "ababaabababa"

print(compute_prefix_function(pattern))
print(kmp_search(text, pattern))
```

Complexity:

- `compute_prefix_function`: `O(m)` time, `O(m)` space for pattern length `m`
- `kmp_search`: `O(n + m)` time, `O(m)` extra space

### Aho-Corasick

`AhoCorasickAutomaton` is useful when you want to search for many patterns in
one pass through the text.

```python
from algorithms import AhoCorasickAutomaton

automaton = AhoCorasickAutomaton(["he", "she", "his", "hers"])

matches = automaton.search("ushers")
grouped = automaton.search_as_dict("ushers")

print(matches)
print(grouped)
```

Complexity:

- trie build + failure links: `O(sum(len(pattern)))` time
- `search`: `O(n + matches)` time
- `search_as_dict`: `O(n + matches + number_of_patterns)` time
- space: `O(sum(len(pattern)))`

## Geometry algorithms

### Convex hull in 2D

The library includes several classical convex hull implementations so you can
compare approaches and asymptotics while studying:

```python
from algorithms import (
    Point2D,
    graham_scan_convex_hull,
    jarvis_march_convex_hull,
    monotonic_chain_convex_hull,
)

points = [
    Point2D(0, 0),
    Point2D(2, 0),
    Point2D(3, 1),
    Point2D(2, 3),
    Point2D(0, 2),
    Point2D(1, 1),
]

print(monotonic_chain_convex_hull(points))
print(graham_scan_convex_hull(points))
print(jarvis_march_convex_hull(points))
```

Complexity:

- `monotonic_chain_convex_hull`: `O(n log n)` time, `O(n)` space
- `graham_scan_convex_hull`: `O(n log n)` time, `O(n)` space
- `graham_scan_steps`: `O(n log n)` algorithmic work, plus `O(number_of_steps)` trace storage
- `jarvis_march_convex_hull`: `O(nh)` time, `O(h)` extra space
- `jarvis_march_steps`: `O(nh)` algorithmic work, plus `O(number_of_steps)` trace storage

### Delaunay triangulation and Voronoi diagram

```python
from algorithms import Point2D, delaunay_triangulation, voronoi_diagram

points = [
    Point2D(0, 0),
    Point2D(1, 0),
    Point2D(1, 1),
    Point2D(0, 1),
]

triangles = delaunay_triangulation(points)
diagram = voronoi_diagram(points)

print(triangles)
print(diagram.edges)
```

Complexity:

- `delaunay_triangulation`: about `O(n^2)` time in this Bowyer-Watson implementation, `O(n)` active triangulation space
- `delaunay_triangulation_steps`: same triangulation work plus stored step snapshots
- `voronoi_diagram`: dominated by triangulation, so about `O(n^2)` time here

Visualization scripts:

```bash
uv run --group viz python scripts/visualize_delaunay.py
uv run --group viz python scripts/visualize_convex_hull.py
uv run --group viz python scripts/visualize_graham_scan.py
uv run --group viz python scripts/visualize_jarvis_march.py
```

## Tree algorithms

### Least Common Ancestor

```python
from algorithms import LowestCommonAncestor

tree = {
    1: [2, 3],
    2: [1, 4, 5],
    3: [1, 6],
    4: [2],
    5: [2],
    6: [3],
}

lca = LowestCommonAncestor(tree, 1)

print(lca.lca(4, 5))
print(lca.distance(4, 6))
```

Complexity:

- preprocessing in `LowestCommonAncestor(...)`: `O(n log n)` time, `O(n log n)` space
- `lca`, `kth_ancestor`: `O(log n)` time
- `distance`: `O(log n)` time because it uses `lca`

## Sorting algorithms

```python
from algorithms import heapsort, mergesort, quicksort, radix_sort

values = [5, 1, 9, 3, 3, 0, -2, 8, 4]

print(quicksort(values))
print(mergesort(values))
print(heapsort(values))
print(radix_sort(values))
```

Complexity:

- `quicksort`: average `O(n log n)` time, worst-case `O(n^2)` time, `O(n)` extra space in this recursive copy-based version
- `mergesort`: `O(n log n)` time, `O(n)` extra space
- `heapsort`: `O(n log n)` time, `O(n)` total space here because the function sorts a copied list
- `radix_sort`: `O(d(n + b))` time for `d` digits and base `b = 10`, `O(n + b)` extra space

## What is included

- `data_structures`
  - `Treap`
  - `ImplicitTreap`
  - `BST`
  - `AVLTree`
  - `RedBlackTree`
  - `SegmentTree`
  - `DisjointSet`
- `range_queries`
  - `RMQ`
- `graph_algorithms`
  - `bfs_traversal`
  - `dfs_traversal`
  - `connected_components`
  - `prim_mst`
  - `kruskal_mst`
  - `dijkstra_shortest_paths`
  - `bellman_ford_shortest_paths`
  - `floyd_warshall_shortest_paths`
- `string_algorithms`
  - `compute_prefix_function`
  - `kmp_search`
  - `AhoCorasickAutomaton`
- `geometry_algorithms`
  - `Point2D`
  - `monotonic_chain_convex_hull`
  - `graham_scan_convex_hull`
  - `graham_scan_steps`
  - `jarvis_march_convex_hull`
  - `jarvis_march_steps`
  - `delaunay_triangulation`
  - `delaunay_triangulation_steps`
  - `voronoi_diagram`
- `tree_algorithms`
  - `LowestCommonAncestor`
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
