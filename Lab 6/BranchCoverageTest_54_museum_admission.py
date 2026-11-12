"""Branch coverage tests for museum_admission.py.

Goal: every decision (if / elif / else, and/not conditions) evaluates to
both True and False at least once, plus the boundary values of each rule.
Run:
    coverage run --branch -m pytest BranchCoverageTest_54_museum_admission.py
    coverage report -m
"""
import pytest
from museum_admission import ticket_price, group_discount, gallery_entry


# ---------- ticket_price ----------

def test_unknown_category_raises():
    with pytest.raises(ValueError, match="unknown category"):
        ticket_price("vip", 30, "tuesday", False)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        ticket_price("adult", -1, "tuesday", False)


def test_age_zero_is_free():
    assert ticket_price("adult", 0, "tuesday", False) == 0


def test_age_four_is_free():
    assert ticket_price("child", 4, "saturday", True) == 0


def test_age_five_pays():
    # boundary: age < 5 is False at exactly 5
    assert ticket_price("child", 5, "tuesday", False) == 100


@pytest.mark.parametrize(
    "category, expected",
    [("adult", 300), ("student", 150), ("child", 100), ("senior", 200)],
)
def test_weekday_without_tour_is_base_price(category, expected):
    # day is neither Monday nor weekend, no guided tour: both False branches
    assert ticket_price(category, 30, "wednesday", False) == expected


def test_monday_halves_price_without_tour():
    assert ticket_price("adult", 30, "monday", False) == 150


def test_monday_odd_price_uses_floor_division():
    assert ticket_price("student", 20, "monday", False) == 75


def test_saturday_surcharge_without_tour():
    assert ticket_price("adult", 30, "saturday", False) == 350


def test_sunday_surcharge_without_tour():
    assert ticket_price("child", 8, "sunday", False) == 150


def test_student_guided_tour_adds_fifty():
    assert ticket_price("student", 20, "tuesday", True) == 200


def test_non_student_guided_tour_adds_hundred():
    assert ticket_price("adult", 30, "tuesday", True) == 400


def test_student_monday_with_guided_tour():
    assert ticket_price("student", 20, "monday", True) == 125


def test_senior_sunday_with_guided_tour():
    assert ticket_price("senior", 65, "sunday", True) == 350


def test_day_is_case_sensitive():
    # "Monday" is not "monday", so no discount is applied
    assert ticket_price("adult", 30, "Monday", False) == 300


# ---------- group_discount ----------

@pytest.mark.parametrize("size", [0, -3])
def test_invalid_group_size_raises(size):
    with pytest.raises(ValueError, match="invalid group size"):
        group_discount(size, False)


@pytest.mark.parametrize(
    "size, expected",
    [(1, 25), (19, 25), (20, 40), (45, 40)],
)
def test_school_groups(size, expected):
    # is_school True, with both sides of the size >= 20 boundary
    assert group_discount(size, True) == expected


@pytest.mark.parametrize(
    "size, expected",
    [(1, 0), (7, 0), (8, 10), (14, 10), (15, 20), (30, 20)],
)
def test_public_groups(size, expected):
    # is_school False, with both sides of the 8 and 15 boundaries
    assert group_discount(size, False) == expected


# ---------- gallery_entry ----------

def test_gallery_at_capacity_waits():
    assert gallery_entry(100, 100, True) == "wait"


def test_gallery_over_capacity_waits():
    assert gallery_entry(120, 100, False) == "wait"


def test_gallery_at_ninety_percent_without_slot_queues():
    # boundary: 90 * 10 >= 100 * 9
    assert gallery_entry(90, 100, False) == "queue"


def test_gallery_at_ninety_percent_with_slot_enters():
    # first condition True, has_timed_slot makes the whole check False
    assert gallery_entry(90, 100, True) == "enter"


def test_gallery_just_below_ninety_percent_enters():
    # first condition False even without a timed slot
    assert gallery_entry(89, 100, False) == "enter"


def test_empty_gallery_enters():
    assert gallery_entry(0, 50, False) == "enter"
