
"""
PDSP 2025 - Assignment 5
Test suite for your Node class.

Usage:
1. Put your Node implementation in a file named `node.py` in the same folder.
   It must define a class called `Node` with the interface required by the
   assignment (tag, value, left, right, find, insert, delete, __str__).
2. Then run this file:
       python pdsp_assignment5_tests.py

If you use a different file name, just edit the import section below.
"""

from ast import literal_eval
import random

# --------------- import your Node class ---------------

try:
    from node import Node   # make sure you have node.py with class Node in it
except ImportError as e:
    raise ImportError(
        "Could not import Node from node.py. "
        "Make sure your implementation is in a file named 'node.py' "
        "in the same directory, or edit the import in this test file."
    ) from e


# --------------- helpers to inspect and validate the tree ---------------

def collect_leaf_values(node):
    """Return the list of all leaf values in left to right order."""
    if node is None:
        return []
    if node.tag == "L":
        # empty tree has a single leaf with value None
        return [] if node.value is None else [node.value]
    # internal node
    return collect_leaf_values(node.left) + collect_leaf_values(node.right)


def collect_nodes_inorder_from_str(tree):
    """
    Use __str__ output to get list of (tag, value) pairs.
    Assumes __str__ returns something like:
        [("L",1), ("I",2), ("L",2), ...]
    """
    s = str(tree)
    try:
        data = literal_eval(s)
    except Exception as e:
        raise AssertionError(
            f"__str__ should return a Python list literal, got: {s!r}"
        ) from e

    if not isinstance(data, list):
        raise AssertionError("__str__ should return a list literal of tuples")

    for item in data:
        if not (isinstance(item, tuple) and len(item) == 2):
            raise AssertionError(
                "__str__ list elements should be (tag, value) tuples"
            )
    return data


def min_leaf_value(node):
    """Return minimum leaf value in subtree. Assumes subtree not empty."""
    leaves = collect_leaf_values(node)
    if not leaves:
        raise AssertionError("min_leaf_value called on empty subtree")
    return min(leaves)


def validate_structure(node, is_root=True):
    """
    Recursively validate the invariants from the assignment:

      1. The empty tree is exactly one leaf with value None.
      2. In a non empty tree, every leaf has tag L and value is not None.
      3. Every internal node has tag I and both children are present.
      4. Internal node value v satisfies:
            all leaf values in left subtree < v
            all leaf values in right subtree >= v
         and v equals the minimum leaf value in the right subtree.
    """
    if node is None:
        raise AssertionError("There should never be a None node reference")

    # empty tree case: a single leaf with value None
    if node.tag == "L" and node.value is None:
        if not is_root:
            raise AssertionError(
                "Leaf with value None should appear only as the root of an empty tree"
            )
        if node.left is not None or node.right is not None:
            raise AssertionError(
                "Empty tree root leaf with None should have both children set to None"
            )
        return

    if node.tag == "L":
        # non empty leaf
        if node.value is None:
            raise AssertionError(
                "In a non empty tree, no node should have value None"
            )
        if node.left is not None or node.right is not None:
            raise AssertionError(
                "Leaf nodes should have both left and right set to None"
            )
        return

    # internal node
    if node.tag != "I":
        raise AssertionError("Non leaf nodes must have tag 'I'")

    if node.left is None or node.right is None:
        raise AssertionError(
            "Every internal node should have two children (no single child internal nodes)"
        )

    # recursive checks
    validate_structure(node.left, is_root=False)
    validate_structure(node.right, is_root=False)

    # all leaf values in left subtree should be strictly less than node.value
    left_vals = collect_leaf_values(node.left)
    right_vals = collect_leaf_values(node.right)

    if not left_vals or not right_vals:
        raise AssertionError(
            "Internal node should have non empty left and right subtrees with leaves"
        )

    v = node.value
    if any(x >= v for x in left_vals):
        raise AssertionError(
            "All values in the left subtree must be strictly less than the internal node value"
        )
    if any(x < v for x in right_vals):
        raise AssertionError(
            "All values in the right subtree must be greater than or equal to the internal node value"
        )

    # internal node value equals minimum of right subtree
    if v != min(right_vals):
        raise AssertionError(
            "Internal node value must equal the minimum leaf value in its right subtree"
        )


def assert_leaf_values_equal(tree, expected_values):
    """
    Check that the set of values stored in the tree equals expected_values
    and that they appear sorted when we collect leaves in left to right order.
    """
    leaf_vals = collect_leaf_values(tree)
    if sorted(leaf_vals) != sorted(expected_values):
        raise AssertionError(
            f"Leaf values {leaf_vals} do not match expected {expected_values}"
        )


# --------------- individual tests ---------------

def test_empty_tree():
    t = Node()
    # structure of empty tree
    assert t.tag == "L", "Empty tree root must be a leaf with tag 'L'"
    assert t.value is None, "Empty tree root leaf must have value None"
    assert t.left is None and t.right is None, "Empty root leaf must have no children"
    validate_structure(t)
    # behaviour
    assert t.find(10) is False, "find on empty tree should return False"
    pairs = collect_nodes_inorder_from_str(t)
    assert pairs == [("L", None)], (
        "For an empty tree, __str__ is expected to show a single leaf with value None"
    )


def test_singleton_tree():
    t = Node(7)
    validate_structure(t)
    assert_leaf_values_equal(t, [7])
    assert t.find(7) is True
    assert t.find(5) is False
    pairs = collect_nodes_inorder_from_str(t)
    assert pairs == [("L", 7)], "Singleton tree inorder should show one leaf"


def test_simple_inserts():
    t = Node()
    values = [3, 1, 5, 4, 2]
    for v in values:
        t.insert(v)
        validate_structure(t)
    assert_leaf_values_equal(t, values)
    for v in values:
        assert t.find(v) is True
    for v in [0, 6, 99]:
        assert t.find(v) is False


def test_insert_duplicates():
    t = Node()
    for v in [10, 20, 5, 15]:
        t.insert(v)
    # duplicate insert should not add new leaves
    t.insert(10)
    t.insert(5)
    validate_structure(t)
    assert_leaf_values_equal(t, [5, 10, 15, 20])


def test_delete_leaf_various_positions():
    t = Node()
    values = [10, 5, 15, 2, 7, 12, 20]
    for v in values:
        t.insert(v)
    validate_structure(t)
    assert_leaf_values_equal(t, values)

    # delete a middle value
    t.delete(7)
    validate_structure(t)
    assert_leaf_values_equal(t, [10, 5, 15, 2, 12, 20])
    assert t.find(7) is False

    # delete smallest
    t.delete(2)
    validate_structure(t)
    assert_leaf_values_equal(t, [10, 5, 15, 12, 20])
    assert t.find(2) is False

    # delete largest
    t.delete(20)
    validate_structure(t)
    assert_leaf_values_equal(t, [10, 5, 15, 12])
    assert t.find(20) is False


def test_delete_nonexistent_value():
    t = Node()
    for v in [3, 1, 4]:
        t.insert(v)
    before = collect_leaf_values(t)
    t.delete(99)   # should not break anything
    validate_structure(t)
    after = collect_leaf_values(t)
    assert before == after, "Deleting a missing value should not change the tree"


def test_delete_all_to_empty():
    t = Node()
    vals = [5, 3, 7]
    for v in vals:
        t.insert(v)
    for v in vals:
        t.delete(v)
        validate_structure(t)
    # after deleting all, tree should be back to empty form
    assert t.tag == "L"
    assert t.value is None
    assert t.left is None and t.right is None
    assert t.find(5) is False


def test_str_format_and_inorder_for_small_tree():
    t = Node()
    for v in [2, 1, 3]:
        t.insert(v)
    validate_structure(t)
    pairs = collect_nodes_inorder_from_str(t)

    # basic type checks
    for tag, val in pairs:
        assert tag in ("L", "I"), "tag must be 'L' or 'I'"
        # for a non empty tree, all values should be ints
        assert isinstance(val, int), "non empty tree nodes must have integer values"

    # at least one internal node is expected, plus three leaves
    leaf_vals = [v for (tag, v) in pairs if tag == "L"]
    assert sorted(leaf_vals) == [1, 2, 3]


# --------------- randomised property test ---------------

def test_random_operations(seed=42, rounds=200):
    """
    Random stress test.
    We keep a reference Python set as the source of truth,
    and after each operation, we compare it with the leaf values in the tree.
    """
    random.seed(seed)
    t = Node()
    model = set()

    for _ in range(rounds):
        op = random.choice(["insert", "delete", "find"])
        v = random.randint(0, 20)

        if op == "insert":
            t.insert(v)
            model.add(v)
        elif op == "delete":
            t.delete(v)
            if v in model:
                model.remove(v)
        else:  # find
            result = t.find(v)
            assert result == (v in model), "find result does not match model set"

        validate_structure(t)
        assert_leaf_values_equal(t, list(model))

    print("Random operations test passed")


# --------------- test runner ---------------

def run_all_tests():
    tests = [
        test_empty_tree,
        test_singleton_tree,
        test_simple_inserts,
        test_insert_duplicates,
        test_delete_leaf_various_positions,
        test_delete_nonexistent_value,
        test_delete_all_to_empty,
        test_str_format_and_inorder_for_small_tree,
        test_random_operations,
    ]

    for test in tests:
        print(f"Running {test.__name__}...")
        test()
    print("All tests passed successfully.")


if __name__ == "__main__":
    run_all_tests()
