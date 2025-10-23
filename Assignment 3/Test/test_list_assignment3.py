"""
Robust tests for the Assignment 3 custom singly linked List.
Assumptions based on the original List.py:
- Empty list is represented by a sentinel node with value None and next None.
- __str__ returns a Python style list string, for example "[1, 2, 3]".
- append works and preserves order.
- insert(v, i) inserts v before index i. Default i is 0.
- valueat(i) returns the value at index i. Negative indices are supported.
- member(v) returns True if v is present, else False.
- deletelast(v) removes the last occurrence of v. Raises ValueError if absent.
- slice(i, j) returns a new List for the slice, never raising on out of bounds.
- rotate(k) rotates in place without creating new nodes.
Place your List.py next to this file or ensure it is on sys.path.
Run with:  python -m unittest -v test_list_assignment3.py
"""

import sys
import unittest
from types import SimpleNamespace

# Ensure /mnt/data is on the path when running inside a notebook or similar
if "/mnt/data" not in sys.path:
    sys.path.append("/mnt/data")

try:
    from List import List
except Exception as e:
    raise SystemExit(
        "Could not import List from List.py. Ensure List.py is available. Error: %r" % (e,)
    )


def to_pylist(L):
    """Traverse the custom linked List into a regular Python list."""
    out = []
    if L is None or getattr(L, "value", None) is None:
        return out
    node = L
    while node is not None and getattr(node, "value", None) is not None:
        out.append(node.value)
        node = node.next
    return out


def from_pylist(values):
    """Create a custom List populated with values, using append."""
    L = List()
    for v in values:
        L.append(v)
    return L


def collect_node_ids(L):
    """Collect object ids of each node to check that rotate does not create new nodes."""
    ids = []
    node = L
    while node is not None:
        ids.append(id(node))
        if node.next is None:
            break
        node = node.next
    return ids


class SkipIfMissingMixin:
    """Skip tests when an expected method is missing, so the file is useful even before full implementation."""

    def require_method(self, obj, name):
        if not hasattr(obj, name):
            self.skipTest(f"Method {name} is not implemented")


class TestMember(SkipIfMissingMixin, unittest.TestCase):
    def test_member_found_and_not_found(self):
        self.require_method(List, "member")
        L = from_pylist([1, 2, 3, 4, 5])
        self.assertTrue(L.member(1))
        self.assertTrue(L.member(3))
        self.assertTrue(L.member(5))
        self.assertFalse(L.member(42))

    def test_member_with_duplicates(self):
        self.require_method(List, "member")
        L = from_pylist([7, 7, 7])
        self.assertTrue(L.member(7))
        self.assertFalse(L.member(8))


class TestValueAt(SkipIfMissingMixin, unittest.TestCase):
    def test_valueat_positive(self):
        self.require_method(List, "valueat")
        L = from_pylist([10, 20, 30, 40])
        self.assertEqual(L.valueat(0), 10)
        self.assertEqual(L.valueat(1), 20)
        self.assertEqual(L.valueat(3), 40)

    def test_valueat_negative(self):
        self.require_method(List, "valueat")
        L = from_pylist([10, 20, 30, 40])
        self.assertEqual(L.valueat(-1), 40)
        self.assertEqual(L.valueat(-2), 30)
        self.assertEqual(L.valueat(-4), 10)

    def test_valueat_out_of_bounds_low(self):
        self.require_method(List, "valueat")
        L = from_pylist([1, 2, 3])
        with self.assertRaises(IndexError) as cm:
            _ = L.valueat(-4)
        self.assertIn("-4", str(cm.exception))

    def test_valueat_out_of_bounds_high(self):
        self.require_method(List, "valueat")
        L = from_pylist([1, 2, 3])
        with self.assertRaises(IndexError) as cm:
            _ = L.valueat(3)
        self.assertIn("3", str(cm.exception))


class TestInsertWithIndex(SkipIfMissingMixin, unittest.TestCase):
    def test_default_inserts_at_head(self):
        self.require_method(List, "insert")
        L = from_pylist([2, 3, 4])
        L.insert(1)  # default i = 0
        self.assertEqual(to_pylist(L), [1, 2, 3, 4])

    def test_insert_middle_and_end(self):
        self.require_method(List, "insert")
        L = from_pylist([1, 3, 4])
        L.insert(2, 1)  # before index 1
        self.assertEqual(to_pylist(L), [1, 2, 3, 4])
        L.insert(5, 4)  # at end, like append
        self.assertEqual(to_pylist(L), [1, 2, 3, 4, 5])

    def test_insert_invalid_index_low(self):
        self.require_method(List, "insert")
        L = from_pylist([1, 2, 3])
        with self.assertRaises(IndexError) as cm:
            L.insert(0, -1)
        self.assertIn("-1", str(cm.exception))

    def test_insert_invalid_index_high(self):
        self.require_method(List, "insert")
        L = from_pylist([1, 2, 3])
        with self.assertRaises(IndexError) as cm:
            L.insert(99, 5)
        self.assertIn("5", str(cm.exception))

    def test_insert_on_empty_default(self):
        self.require_method(List, "insert")
        L = from_pylist([])
        L.insert(7)  # should behave like setting the first value
        self.assertEqual(to_pylist(L), [7])


class TestDeleteLast(SkipIfMissingMixin, unittest.TestCase):
    def test_deletelast_basic(self):
        self.require_method(List, "deletelast")
        L = from_pylist([1, 2, 3, 2, 4])
        L.deletelast(2)
        self.assertEqual(to_pylist(L), [1, 2, 3, 4])

    def test_deletelast_single_occurrence(self):
        self.require_method(List, "deletelast")
        L = from_pylist([5])
        L.deletelast(5)
        self.assertEqual(to_pylist(L), [])  # should be empty after deletion

    def test_deletelast_absent_raises(self):
        self.require_method(List, "deletelast")
        L = from_pylist([1, 2, 3])
        with self.assertRaises(ValueError) as cm:
            L.deletelast(9)
        # The message should include the value
        self.assertIn("9", str(cm.exception))


class TestSlice(SkipIfMissingMixin, unittest.TestCase):
    def test_slice_basic(self):
        self.require_method(List, "slice")
        L = from_pylist([0, 1, 2, 3, 4, 5])
        S = L.slice(1, 4)
        self.assertIsInstance(S, List)
        self.assertEqual(to_pylist(S), [1, 2, 3])

    def test_slice_negative_start(self):
        self.require_method(List, "slice")
        L = from_pylist([10, 20, 30])
        S = L.slice(-5, 2)  # should behave like start at 0
        self.assertEqual(to_pylist(S), [10, 20])

    def test_slice_end_beyond_length(self):
        self.require_method(List, "slice")
        L = from_pylist([1, 2, 3])
        S = L.slice(1, 10)  # should clamp to length
        self.assertEqual(to_pylist(S), [2, 3])

    def test_slice_empty_when_j_le_i(self):
        self.require_method(List, "slice")
        L = from_pylist([1, 2, 3, 4])
        self.assertEqual(to_pylist(L.slice(2, 2)), [])
        self.assertEqual(to_pylist(L.slice(3, 2)), [])

    def test_slice_independence(self):
        """Slice should return a new list whose nodes are independent of the original."""
        self.require_method(List, "slice")
        L = from_pylist([1, 2, 3, 4, 5])
        S = L.slice(1, 4)  # [2, 3, 4]
        # Modify original and ensure S is unchanged
        L.deletelast(4) if hasattr(List, "deletelast") else L.delete(4)
        self.assertEqual(to_pylist(S), [2, 3, 4])


class TestRotate(SkipIfMissingMixin, unittest.TestCase):
    def test_rotate_zero_is_noop(self):
        self.require_method(List, "rotate")
        L = from_pylist([1, 2, 3, 4, 5])
        ids_before = collect_node_ids(L)
        L.rotate(0)
        self.assertEqual(to_pylist(L), [1, 2, 3, 4, 5])
        self.assertEqual(set(ids_before), set(collect_node_ids(L)))

    def test_rotate_examples(self):
        self.require_method(List, "rotate")
        L = from_pylist([1, 2, 3, 4, 5])
        L.rotate(1)
        self.assertEqual(to_pylist(L), [5, 1, 2, 3, 4])
        L.rotate(2)
        self.assertEqual(to_pylist(L), [3, 4, 5, 1, 2])
        L.rotate(2)
        self.assertEqual(to_pylist(L), [1, 2, 3, 4, 5])  # back to original

    def test_rotate_by_length_and_more(self):
        self.require_method(List, "rotate")
        L = from_pylist([10, 20, 30])
        L.rotate(3)  # k equal to length, should be unchanged
        self.assertEqual(to_pylist(L), [10, 20, 30])
        L.rotate(4)  # k mod n equals 1
        self.assertEqual(to_pylist(L), [30, 10, 20])

    def test_rotate_no_new_nodes(self):
        self.require_method(List, "rotate")
        L = from_pylist([1, 2, 3, 4])
        before = set(collect_node_ids(L))
        L.rotate(3)
        after = set(collect_node_ids(L))
        self.assertEqual(before, after)


class TestRepresentationAndBasics(unittest.TestCase):
    def test_str_format(self):
        L = from_pylist([1, 2, 3])
        self.assertEqual(str(L), "[1, 2, 3]")
        L2 = from_pylist([])
        self.assertEqual(str(L2), "[]")

    def test_append_and_insert_default_on_empty(self):
        L = List()
        L.append(1)
        L.append(2)
        self.assertEqual(to_pylist(L), [1, 2])
        # Check default insert on empty list
        L2 = List()
        if hasattr(List, "insert"):
            L2.insert(99)
            self.assertEqual(to_pylist(L2), [99])


if __name__ == "__main__":
    unittest.main(verbosity=2)
