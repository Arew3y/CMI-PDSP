
import math
import re
import builtins
import itertools
import types

import pytest


# ---------- Helper to check "sensible" printing without zero terms ----------
def has_zero_terms(s: str) -> bool:
    """Heuristically detect zero terms like '0x', '+ 0', '- 0x^k' in a string representation."""
    z_patterns = [
        r"\b0x",                 # 0x, 0x^k
        r"(^|\s)[\+\-]\s*0\b",   # + 0, - 0
        r"\b\+?\s*0\s*(?:$|[+\-])",
    ]
    return any(re.search(p, s) for p in z_patterns)

class Polynomial:
    def __init__(self, poly_list=None):
        poly_list = poly_list or [] # Empty list handling
        self.poly_list = poly_list
        self.poly_dict = {} # Creating a dictionary to store the exponent : coefficient
        if poly_list != []: # Exception handling for empty list
            # Adding elements to the poly_dict
            for elem in poly_list:
                if elem[1] in self.poly_dict:
                    self.poly_dict[elem[1]] = self.poly_dict[elem[1]] + elem[0]
                else:
                    if elem[0] != 0:
                        self.poly_dict[elem[1]] = elem[0]
        self.rmv_empty() # Removing any empty elements
        self.key_list = sorted(self.poly_dict.keys())[::-1] # Sorting the keylist to show the higher exponents first
        #
    def iszero(self): # Zero polynomial check by checking empty dict
        return self.poly_dict == {}
        #
    def rmv_empty(self): # Removing elements with coefficient 0
        temp_poly_dict = dict(self.poly_dict) # Working on a copy while deleting from the original
        for elem in temp_poly_dict:
            if temp_poly_dict[elem] == 0:
                del self.poly_dict[elem] # Erasing entries where coefficient became 0
        #
    def __add__(self, q):
        new_poly = Polynomial([]) # Making a polynomial to hold the sum
        new_poly.poly_dict = dict(self.poly_dict) # Adding the first polynomial to the sum polynomial
        for expo in q.poly_dict: # Adding all the elements of the second elements in the sum polynomial
            if expo in new_poly.poly_dict:
                new_poly.poly_dict[expo] = new_poly.poly_dict[expo] + q.poly_dict[expo]
            else:
                new_poly.poly_dict[expo] = q.poly_dict[expo]
        new_poly.rmv_empty() # Cleaning the new sum polynomial
        new_poly.key_list = sorted(new_poly.poly_dict.keys())[::-1] # Filling the sum polynomial key_list
        return new_poly # Returning the result polynomial
        #
    def __sub__(self, q):
        new_poly = Polynomial([]) # Making a polynomial to hold the subtraction
        new_poly.poly_dict = dict(self.poly_dict) # Adding the first polynomial to the sub polynomial
        for expo in q.poly_dict: # Subtracting all the elements of the second elements in the sub polynomial
            if expo in new_poly.poly_dict:
                new_poly.poly_dict[expo] = new_poly.poly_dict[expo] - q.poly_dict[expo]
            else:
                new_poly.poly_dict[expo] = -q.poly_dict[expo]
        new_poly.rmv_empty() # Cleaning the new sub polynomial
        new_poly.key_list = sorted(new_poly.poly_dict.keys())[::-1] # Filling the sub polynomial key_list
        return new_poly # Returning the result polynomial
        #
    def __mul__(self, q):
        new_poly = Polynomial([]) # Making a polynomial to hold the multiplication
        for expo1 in q.poly_dict: # Looping over terms of the right side polynomial
            for expo2 in self.poly_dict: # Looping over terms of the left side polynomial
                if expo1 + expo2 in new_poly.poly_dict: # Adding the elements the mult poly dictionary
                    new_poly.poly_dict[expo1 + expo2] = new_poly.poly_dict[expo2 + expo1] + (self.poly_dict[expo2] * q.poly_dict[expo1]) # Combining like exponents by summing products
                else:
                    new_poly.poly_dict[expo1 + expo2] = self.poly_dict[expo2] * q.poly_dict[expo1] # First product for this exponent
        new_poly.rmv_empty() # Cleaning the new mult polynomial
        new_poly.key_list = sorted(new_poly.poly_dict.keys())[::-1] # Filling the mult polynomial key_list
        return new_poly # Returning the result polynomial
        #
    def __neg__(self):
        n = len(self.poly_list)
        new_poly_list = []
        for i in range(n):
            new_poly_list.append([-self.poly_list[i][0],self.poly_list[i][1]])
        return Polynomial(new_poly_list)
        #
    def __lt__(self, q):
        # Making copy of the dict and keylist
        self_poly_dict = self.poly_dict.copy()
        self_key_list = sorted(self.poly_dict.keys())[::-1]
        q_poly_dict = q.poly_dict.copy()
        q_key_list = sorted(q.poly_dict.keys())[::-1]

        # Handling zero polynomials
        if self_poly_dict == {}:
            self_poly_dict[0] = 0 # Represent zero with exponent 0 for comparison use
            self_key_list = sorted(self_poly_dict.keys())[::-1]
        if q_poly_dict == {}:
            q_poly_dict[0] = 0 # Same handling for the other polynomial
            q_key_list = sorted(q_poly_dict.keys())[::-1]

        # Defining Minimum length for the range check
        min_len = min(len(self_key_list), len(q_key_list)) # Compare up to the shorter length

        for i in range(min_len):
            key1 = self_key_list[i] # Current highest remaining exponent of self
            key2 = q_key_list[i] # Current highest remaining exponent of q
            if key1 < key2:
                return True # Smaller leading exponent means less
            if key2 < key1:
                return False # Larger leading exponent on self means greater
            if key1 == key2:
                pval = self_poly_dict[key1] # Coefficient for this exponent in self
                qval = q_poly_dict[key2] # Coefficient for this exponent in q
                if pval < qval:
                    return True # Same exponent so compare coefficients
                elif pval > qval:
                    return False # Coefficient is larger so not less
                else:
                    continue # Move to next term when both match
        if len(self_key_list) < len(q_key_list):
            return True
        return False # No deciding difference found so treat as not less
        #
    def __le__(self, q):
        return self.__lt__(q) or self.__eq__(q) # Lesser or equal by using or statement
        #
    def __ge__(self, q):
        return q.__le__(self) # Greater or equal by swapping the operands
        #
    def __gt__(self, q):
        return q.__lt__(self) # Greater than by reusing less than on swapped operands
        #
    def __eq__(self, q):
        for key1 in self.key_list: # Every exponent in self must be present in q
            if key1 not in q.key_list:
                return False # Missing exponent means not equal
            else:
                if q.poly_dict[key1] != self.poly_dict[key1]:
                    return False # Different coefficient means not equal
        for key2 in q.key_list: # Every exponent in q must be present in self
            if key2 not in self.key_list:
                return False # Missing exponent means not equal
            else:
                if self.poly_dict[key2] != q.poly_dict[key2]:
                    return False # Different coefficient means not equal
        return True # All exponents and coefficients match
        #
    def __ne__(self, q):
        return not self.__eq__(q) # Not equal is the logical negation of equal
        #
    def __str__(self):
        poly_print = "" # Building the printable string
        n = len(self.key_list) # Number of distinct exponents
        if n != 0:
            for i in range(n):
                key = self.key_list[i] # Current exponent
                cons = self.poly_dict[key] # Current coefficient

                if cons == 0: # might be unnecessary
                    break # Skip remaining when a zero is encountered

                if key == 0:
                    var = str(abs(cons)) # Pure constant term
                elif key == 1:
                    var = str(abs(cons)) + "x" # Linear term
                else:
                    var = str(abs(cons)) + "x^" + str(key) # General term

                if cons < 0 and i != 0:
                    var = " - " + var # Negative sign for subsequent terms
                elif cons > 0 and i != 0:
                    var = " + " + var # Positive sign for subsequent terms
                poly_print = poly_print + var # Appending this term to the output
        if poly_print == "":
            poly_print = "" # Zero polynomial string
        return str(poly_print) # Returning the final string
        #
    def __repr__(self):
        return str(self) # Same text for interactive display

# A small factory so the student can import Polynomial from their notebook or script.
# The test suite will attempt to import `Polynomial` from a module named `polynomial` if available;
# otherwise it expects the test to be run in the same environment where Polynomial is defined.
def get_Polynomial_class():
    try:
        from polynomial import Polynomial  # optional convenience if student put class in polynomial.py
        return Polynomial
    except Exception:
        # Fall back to global definition in the test session (pytest will raise a clear error if missing)
        return globals().get("Polynomial", None)


@pytest.fixture(scope="module")
def P():
    Poly = get_Polynomial_class()
    if Poly is None:
        pytest.fail(
            "Polynomial class not found. Either define `class Polynomial` in the test session "
            "or create polynomial.py with `class Polynomial` and run pytest again."
        )
    return Poly


# ---------- Core constructor and normalization ----------

def test_constructor_zero_default(P):
    p = P()
    assert p.iszero(), "Default constructor must create the zero polynomial."


def test_constructor_combines_like_terms(P):
    p = P([(2, 4), (3, 4), (-5, 4)])  # sums to 0x^4 -> zero poly
    assert p.iszero(), "Constructor must combine like exponents and drop zero coefficients."


def test_constructor_drops_explicit_zero_terms(P):
    p = P([(0, 5), (0, 1), (0, 0)])
    assert p.iszero(), "All explicit zero-coefficient terms should be dropped, yielding zero polynomial."


def test_constructor_unsorted_input_is_ok(P):
    # Input exponents not sorted and with duplicates
    p = P([(5, 0), (-3, 1), (3, 4), (-17, 2), (2, 1), (-5, 0)])
    # After combining like terms: constant term 0, x term -1
    # Final: 3x^4 - 17x^2 - 1x
    q = P([(3, 4), (-17, 2), (-1, 1)])
    assert p == q, "Constructor must accept unsorted input with duplicates and normalize correctly."


# ---------- iszero() correctness ----------

def test_iszero_true_only_for_zero(P):
    zero = P()
    nonzero = P([(0, 2), (1, 0)])
    assert zero.iszero() is True
    assert nonzero.iszero() is False


# ---------- Equality and independence from term order ----------

def test_equality_independent_of_input_order(P):
    p1 = P([(3, 2), (1, 0), (-2, 2), (4, 1)])
    p2 = P([(1, 0), (1, 2), (4, 1)])
    assert p1 == p2, "Equal polynomials must compare equal regardless of input order and duplicates."


def test_inequality_when_different(P):
    p = P([(1, 1)])
    q = P([(1, 0)])
    assert p != q
    assert not (p == q)


# ---------- Addition, subtraction ----------

def test_addition_simple(P):
    x2 = P([(1, 2)])
    x = P([(1, 1)])
    const = P([(5, 0)])
    assert x2 + x == P([(1, 2), (1, 1)])
    assert x + const == P([(1, 1), (5, 0)])


def test_addition_with_cancellation(P):
    p = P([(3, 4), (-2, 2), (7, 0)])
    q = P([(-3, 4), (2, 2), (-7, 0)])
    s = p + q
    assert s.iszero(), "Terms should cancel to zero when coefficients sum to zero."


def test_subtraction_simple(P):
    p = P([(2, 2), (1, 0)])
    q = P([(1, 2), (3, 0)])
    assert p - q == P([(1, 2), (-2, 0)])


def test_add_sub_identities(P):
    p = P([(4, 5), (3, 0)])
    zero = P()
    assert p + zero == p
    assert p - zero == p
    assert p + (-p) == zero  # relies on __neg__ via subtraction definition p + (-p)


# ---------- Multiplication ----------

def test_multiplication_basic(P):
    # (x + 1) * (x - 1) = x^2 - 1
    a = P([(1, 1), (1, 0)])
    b = P([(1, 1), (-1, 0)])
    prod = a * b
    assert prod == P([(1, 2), (-1, 0)])


def test_multiplication_by_zero_and_one(P):
    zero = P()
    one = P([(1, 0)])
    p = P([(2, 3), (5, 1)])
    assert p * zero == zero
    assert zero * p == zero
    assert p * one == p
    assert one * p == p


def test_multiplication_combines_like_terms(P):
    # (2x^2 + 3x) * (x + 4) = 2x^3 + 8x^2 + 3x^2 + 12x = 2x^3 + 11x^2 + 12x
    p = P([(2, 2), (3, 1)])
    q = P([(1, 1), (4, 0)])
    assert p * q == P([(2, 3), (11, 2), (12, 1)])


# ---------- Algebraic properties ----------

def test_commutativity_add(P):
    p = P([(1, 3), (2, 1)])
    q = P([(3, 2), (-5, 0)])
    assert p + q == q + p


def test_commutativity_mul(P):
    p = P([(1, 3), (2, 1)])
    q = P([(3, 2), (-5, 0)])
    assert p * q == q * p


def test_associativity_add(P):
    p = P([(2, 3)])
    q = P([(3, 2)])
    r = P([(4, 1)])
    assert (p + q) + r == p + (q + r)


def test_distributivity(P):
    p = P([(1, 2)])
    q = P([(2, 1)])
    r = P([(3, 0)])
    assert p * (q + r) == p * q + p * r


# ---------- Ordering: lexicographic on (exponent, coefficient) descending by exponent ----------

def test_ordering_highest_exponent_decides(P):
    # Compare 3x^4 + ... vs 100x^3 + ...
    a = P([(3, 4), (1, 0)])
    b = P([(100, 3), (5, 0)])
    # Highest exponents: 4 vs 3, so a > b
    assert a > b
    assert not (a < b)


def test_ordering_same_highest_exponent_compare_coefficient(P):
    # Highest exponent both 5; compare coefficients of x^5
    a = P([(2, 5), (1, 0)])
    b = P([(-1, 5), (100, 0)])
    assert a > b
    assert not (a < b)


def test_ordering_tiebreaker_next_terms(P):
    # Both have x^4 term with coeff 7
    a = P([(7, 4), (3, 2)])
    b = P([(7, 4), (4, 2)])
    # Next smaller term exponent 2: 3 vs 4 so b > a
    assert b > a


def test_ordering_with_zero_polynomial(P):
    zero = P()
    p = P([(1, 0)])
    # Highest term of p is exponent 0 with coeff 1; zero has no terms, so p > zero
    assert p > zero
    assert zero < p
    assert zero <= p
    assert p >= zero


def test_total_order_consistency(P):
    # Ensure comparisons are consistent and anti-symmetric
    polys = [
        P(),
        P([(1, 0)]),
        P([(-1, 0)]),
        P([(1, 1)]),
        P([(1, 2)]),
        P([(1, 2), (-5, 0)]),
        P([(1, 2), (5, 0)]),
    ]
    # Check pairwise antisymmetry and trichotomy
    for i, a in enumerate(polys):
        for j, b in enumerate(polys):
            if i == j:
                assert a == b
                assert not (a < b or a > b)
            else:
                assert (a < b) != (a > b) or (a == b), "Ordering should be strict except for equality."


# ---------- Printing ----------

def test_print_omits_zero_terms(P, capsys):
    p = P([(3, 4), (0, 2), (5, 0)])
    print(p)
    out = capsys.readouterr().out.strip()
    assert not has_zero_terms(out), f"Printed string should not include zero terms: got {out!r}"


def test_print_general_shape_and_order(P):
    # p represents 3x^4 - 17x^2 - 3x + 5
    p = P([(3, 4), (-17, 2), (-3, 1), (5, 0)])
    s = str(p)
    # Should contain all pieces and reflect descending exponent order
    idx = [s.find("x"), s.find("x", s.find("x") + 1), s.rfind("x")]
    # Must have at least two x occurrences and in increasing index order
    assert all(i >= 0 for i in idx[:2]) and idx[0] < idx[1], "String should show terms with x in proper order."
    # Should include the constant 5 with correct sign somewhere
    assert re.search(r"(\+|\-)\s*5\b", s) or s.strip().endswith("5"), "Constant term should be visible with sign."
    # Should not contain sequences like '+ -' or double spaces around signs
    assert "+ -" not in s and "- +" not in s, "Signs should be rendered cleanly."


def test_zero_polynomial_prints_something_reasonable(P):
    z = P()
    s = str(z).strip()
    # Accept either '0' or an empty string or '0x^0' avoided. We only enforce that it's short and not a polynomial with x.
    assert "x" not in s and len(s) <= 3, "Zero polynomial should print as a simple zero-like representation."
    assert not has_zero_terms(s), "Zero polynomial string must not fabricate zero terms like '0x'."


# ---------- Mixed scenarios pulled from spec example ----------

def test_spec_example_equality(P):
    # From the spec example: 3x^4 - 17x^2 - 3x + 5
    p = P([(3, 4), (-17, 2), (-3, 1), (5, 0)])
    # Build the same polynomial in scrambled order with duplicates
    q = P([(5, 0), (1, 4), (2, 4), (-10, 2), (-7, 2), (-3, 1)])
    assert p == q


# ---------- Defensive: ensure rich comparisons all exist ----------

def test_all_rich_comparisons_exist(P):
    p = P([(1, 1)])
    q = P([(1, 0)])
    # Access all operators to ensure they are implemented
    _ = p < q
    _ = p <= q
    _ = p > q
    _ = p >= q
    _ = p == q
    _ = p != q


# ---------- Bonus: sorting should produce a total order ----------

def test_sorting_list_of_polynomials(P):
    lst = [P([(1, 0)]), P([(1, 2)]), P(), P([(1, 1)])]
    sorted_lst = sorted(lst)  # relies on __lt__
    # Highest exponent dominates, so order should be: 0, x, x^2, constant 1 or vice-versa?
    # Our ordering expects lexicographic descending by exponent when *comparing two polys*, but sorting uses ascending.
    # So expected ascending by that order: zero < 1 < x < x^2
    assert sorted_lst[0].iszero()
    assert sorted_lst[1] == P([(1, 0)])
    assert sorted_lst[2] == P([(1, 1)])
    assert sorted_lst[3] == P([(1, 2)])
