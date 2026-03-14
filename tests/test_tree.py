from algorithms.data_structures import TreeNode


def test_is_ancestor_of_tracks_parent_chain() -> None:
    root = TreeNode()
    left = TreeNode()
    right = TreeNode()

    root.left = left
    root.right = right
    left.parent = root
    right.parent = root
    root.refresh()

    assert root.is_ancestor_of(left)
    assert root.is_ancestor_of(right)
    assert left.is_ancestor_of(left)
    assert not left.is_ancestor_of(right)
    assert not right.is_ancestor_of(None)
