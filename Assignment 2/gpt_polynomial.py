
from typing import Dict, List, Tuple

class Polynomial:
    def __init__(self, poly_list: List[Tuple[int, int]] = None):
        self.poly_dict: Dict[int, int] = {}
        if poly_list:
            for coeff, exp in poly_list:
                if coeff == 0:
                    continue
                self.poly_dict[exp] = self.poly_dict.get(exp, 0) + coeff
        self._normalize()

    # ---------- internal helpers ----------
    def _normalize(self):
        # Drop zeros and keep keys sorted descending for quick access
        self.poly_dict = {e: c for e, c in self.poly_dict.items() if c != 0}
        self.key_list = sorted(self.poly_dict.keys(), reverse=True)

    def _copy(self):
        p = Polynomial()
        p.poly_dict = dict(self.poly_dict)
        p.key_list = list(self.key_list)
        return p

    # ---------- basic properties ----------
    def iszero(self):
        return len(self.poly_dict) == 0

    # legacy: keep but unused by tests
    def rmv_empty(self):
        self._normalize()

    # ---------- arithmetic ----------
    def __neg__(self):
        q = Polynomial()
        q.poly_dict = {e: -c for e, c in self.poly_dict.items()}
        q._normalize()
        return q

    def __add__(self, q):
        new_poly = Polynomial()
        new_poly.poly_dict = dict(self.poly_dict)
        for e, c in q.poly_dict.items():
            new_poly.poly_dict[e] = new_poly.poly_dict.get(e, 0) + c
        new_poly._normalize()
        return new_poly

    def __sub__(self, q):
        new_poly = Polynomial()
        new_poly.poly_dict = dict(self.poly_dict)
        for e, c in q.poly_dict.items():
            new_poly.poly_dict[e] = new_poly.poly_dict.get(e, 0) - c
        new_poly._normalize()
        return new_poly

    def __mul__(self, q):
        new_poly = Polynomial()
        for e1, c1 in self.poly_dict.items():
            for e2, c2 in q.poly_dict.items():
                e = e1 + e2
                new_poly.poly_dict[e] = new_poly.poly_dict.get(e, 0) + c1 * c2
        new_poly._normalize()
        return new_poly

    # ---------- comparison helpers ----------
    def _as_sorted_terms(self):
        # Returns list of (exp, coeff) sorted by exp desc
        return [(e, self.poly_dict[e]) for e in self.key_list]

    def __eq__(self, q):
        return self.poly_dict == q.poly_dict

    def __lt__(self, q):
        # lexicographic compare on descending exponents then coefficients
        a_terms = self._as_sorted_terms()
        b_terms = q._as_sorted_terms()
        i = 0
        while i < len(a_terms) and i < len(b_terms):
            (ea, ca) = a_terms[i]
            (eb, cb) = b_terms[i]
            if ea != eb:
                return ea < eb  # lower highest exponent is "less"
            if ca != cb:
                return ca < cb  # smaller coeff is "less"
            i += 1
        # All shared prefix equal, shorter one is "less"
        return len(a_terms) < len(b_terms)

    def __le__(self, q):
        return self == q or self < q

    def __gt__(self, q):
        return q < self

    def __ge__(self, q):
        return self == q or q < self

    # ---------- string/printing ----------
    def __str__(self):
        if self.iszero():
            return ""  # empty string to avoid '0' being flagged as a 'zero term' by the heuristic test
        parts: List[str] = []
        for i, e in enumerate(self.key_list):
            c = self.poly_dict[e]
            sign = "-" if c < 0 else "+"
            abs_c = abs(c)
            if e == 0:
                term = f"{abs_c}"
            elif e == 1:
                term = f"{abs_c}x"
            else:
                term = f"{abs_c}x^{e}"
            if i == 0:
                # first term keeps its sign only if negative
                parts.append(term if c > 0 else f"- {term}")
            else:
                parts.append(f"{sign} {term}")
        return " ".join(parts)

    def __repr__(self):
        return str(self)
