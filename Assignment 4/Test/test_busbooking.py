
import re
import ast
import itertools
import random
import string
import math
import pytest

# Helper to import BusBooking from your implementation
@pytest.fixture(scope="session")
def BusBooking():
    try:
        from bus_booking import BusBooking as _BusBooking
        return _BusBooking
    except Exception as e:
        raise ImportError(
            "Could not import BusBooking from bus_booking.py. "
            "Place your class in bus_booking.py with class name `BusBooking`. "
            f"Original error: {e}"
        )

SEAT_RE = re.compile(r'^[WA](?:[1-9]|1[0-9]|20)$')

def is_window(seat):
    return isinstance(seat, str) and seat.startswith("W") and SEAT_RE.match(seat)

def is_aisle(seat):
    return isinstance(seat, str) and seat.startswith("A") and SEAT_RE.match(seat)

def is_valid_seat(seat):
    return isinstance(seat, str) and SEAT_RE.match(seat)

def seat_pool():
    return {*(f"W{i}" for i in range(1, 21)), *(f"A{i}" for i in range(1, 21))}

def in_waitlist_format(s):
    return isinstance(s, str) and s.startswith("WL-") and s[3:].isdigit() and int(s[3:]) >= 1

def make_names(n, prefix="P"):
    return [f"{prefix}{i:03d}" for i in range(1, n + 1)]

def fill_bus(b):
    ids = []
    # alternate preferences to exercise both pools
    prefs = itertools.cycle(["window", "aisle", "", "nope", "W", "A"])
    for name in make_names(40):
        bid, outcome = b.book(name, next(prefs))
        ids.append((bid, outcome))
        assert is_valid_seat(outcome)
    return ids

def test_basic_window_allocation(BusBooking):
    b = BusBooking()
    bid, seat = b.book("Alice", "window")
    assert is_window(seat), "Should allocate a window seat when available"
    assert b.status(bid) == ("Alice", seat)

def test_basic_aisle_allocation(BusBooking):
    b = BusBooking()
    bid, seat = b.book("Bob", "aisle")
    assert is_aisle(seat), "Should allocate an aisle seat when available"
    assert b.status(bid) == ("Bob", seat)

@pytest.mark.parametrize("pref", ["W", "w", "Window", "window", "A", "a", "Aisle", "aisle", None, "", "   ", "x", "no pref"])
def test_preference_parsing_and_fallback(BusBooking, pref):
    b = BusBooking()
    bids = []
    # Fill all window seats
    for i in range(20):
        bid, seat = b.book(f"Wpref{i}", "window")
        bids.append(bid)
        assert is_window(seat)
    # Next window request should fallback to any seat
    bid2, out2 = b.book("LateWindow", "window")
    assert is_valid_seat(out2) and is_aisle(out2)
    # Try various spellings and junk preferences for general robustness
    bid3, out3 = b.book("Charlie", pref)
    assert is_valid_seat(out3)

def test_allocation_when_preferred_unavailable(BusBooking):
    b = BusBooking()
    # Fill aisle seats
    for i in range(20):
        bid, seat = b.book(f"A{i}", "aisle")
        assert is_aisle(seat)
    # Request aisle, should get window instead
    bid2, out2 = b.book("Zed", "aisle")
    assert is_window(out2)

def test_waitlist_after_full(BusBooking):
    b = BusBooking()
    fill_bus(b)
    bid, outcome = b.book("WL1", "window")
    assert in_waitlist_format(outcome) and outcome == "WL-1"
    bid2, outcome2 = b.book("WL2", "aisle")
    assert in_waitlist_format(outcome2) and outcome2 == "WL-2"
    # status should reflect the same WL positions
    assert b.status(bid) == ("WL1", "WL-1")
    assert b.status(bid2) == ("WL2", "WL-2")

def test_cancel_allocated_moves_first_waiter(BusBooking):
    b = BusBooking()
    allocated = fill_bus(b)
    # Add three in WL
    wl = [b.book(n, "window")[0] for n in ["WLA", "WLB", "WLC"]]
    assert b.status(wl[0])[1] == "WL-1"
    # Cancel an allocated booking and check WL promotion
    victim_id = allocated[5][0]
    victim_seat = allocated[5][1]
    assert b.cancel(victim_id) is True
    # First waiter should get victim seat
    name, status = b.status(wl[0])
    assert name == "WLA"
    assert status == victim_seat
    # Remaining WL should move up
    assert b.status(wl[1])[1] == "WL-1"
    assert b.status(wl[2])[1] == "WL-2"

def test_cancel_waitlist_entry(BusBooking):
    b = BusBooking()
    fill_bus(b)
    wl1, _ = b.book("X", "window")
    wl2, _ = b.book("Y", "window")
    wl3, _ = b.book("Z", "window")
    assert b.cancel(wl2) is True
    # X remains WL-1, Z shifts up to WL-2
    assert b.status(wl1) == ("X", "WL-1")
    assert b.status(wl3) == ("Z", "WL-2")

def test_invalid_cancel_returns_false(BusBooking):
    b = BusBooking()
    fill_bus(b)
    assert b.cancel("does-not-exist") is False

def test_status_for_valid_ids_only(BusBooking):
    b = BusBooking()
    bid, seat = b.book("Nina", "aisle")
    assert b.status(bid) == ("Nina", seat)
    # behavior for unknown ids is not specified, so we only check known id

def test_str_sorted_by_booking_id_and_format(BusBooking):
    b = BusBooking()
    ids = []
    for nm in ["Ann", "Ben", "Cat", "Dan", "Eli"]:
        ids.append(b.book(nm, "window")[0])
    # add some WL entries as well
    for _ in range(40 - 5):
        b.book(f"F{_}", "aisle")
    extra, _ = b.book("Waiting", "")
    s = str(b)
    data = ast.literal_eval(s)
    assert isinstance(data, list)
    # each item is a triple: (booking_id, name, current_status)
    for t in data:
        assert isinstance(t, tuple) and len(t) == 3
        assert isinstance(t[0], str) and isinstance(t[1], str) and isinstance(t[2], str)
    # confirm sorted ascending by booking_id
    sorted_ids = [t[0] for t in data]
    assert sorted_ids == sorted(sorted_ids)

def test_booking_id_uniqueness_over_long_sequence(BusBooking):
    b = BusBooking()
    seen = set()
    # make more operations than seats, including cancels
    ops = 1000
    active = []
    for i in range(ops):
        if active and random.random() < 0.4:
            victim = random.choice(active)
            b.cancel(victim)
            active.remove(victim)
        else:
            name = f"U{i:04d}"
            pref = random.choice(["window", "aisle", "W", "A", "w", "a", "", "none"])
            bid, outcome = b.book(name, pref)
            assert bid not in seen, "booking_id must be unique across all customers"
            seen.add(bid)
            active.append(bid)
            # outcome is seat or WL-n
            assert is_valid_seat(outcome) or in_waitlist_format(outcome)
    # Spot check that total seats occupied does not exceed 40
    # We cannot inspect internals, but if more than 40 active have seats at once,
    # promotions would have failed. Indirect checks are covered by other tests.

def test_large_interleaved_sequence_preserves_invariants(BusBooking):
    b = BusBooking()
    ids = []
    # Fill some, create WL, cancel, repeat
    for cycle in range(5):
        # add 50 bookings per cycle
        for j in range(50):
            nm = f"C{cycle}_{j}"
            pref = ["window", "aisle", "", "W", "A"][j % 5]
            bid, out = b.book(nm, pref)
            ids.append(bid)
            assert is_valid_seat(out) or in_waitlist_format(out)
        # cancel 20 random existing bookings
        random.shuffle(ids)
        for victim in ids[:20]:
            assert b.cancel(victim) in (True, False)  # True for existing, False if already cancelled
        ids = ids[20:]
    # After all operations, check that any WL positions are well-formed and contiguous from 1
    wl_positions = []
    for bid in ids:
        st = b.status(bid)
        if st:
            name, cur = st
            if in_waitlist_format(cur):
                wl_positions.append(int(cur.split("-")[1]))
    if wl_positions:
        assert sorted(wl_positions) == list(range(1, len(wl_positions) + 1))

def test_seat_identifiers_are_within_defined_pool(BusBooking):
    b = BusBooking()
    taken = set()
    for i in range(40):
        bid, seat = b.book(f"P{i}", "window" if i % 2 == 0 else "aisle")
        assert seat in seat_pool()
        assert seat not in taken
        taken.add(seat)
    bid, out = b.book("WLAfterFull", "window")
    assert out == "WL-1"
