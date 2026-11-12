"""Code (line) coverage tests for museum_admission.py.

Goal: execute every statement in the module at least once.
Run:
    coverage run -m pytest CodeCoverageTest_54_museum_admission.py
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


def test_child_under_five_is_free():
    assert ticket_price("child", 3, "saturday", True) == 0


def test_student_monday_with_guided_tour():
    # 150 halved on Monday = 75, student tour adds 50
    assert ticket_price("student", 20, "monday", True) == 125


def test_senior_sunday_with_guided_tour():
    # 200 + 50 weekend surcharge, non-student tour adds 100
    assert ticket_price("senior", 65, "sunday", True) == 350


# ---------- group_discount ----------

def test_group_size_zero_raises():
    with pytest.raises(ValueError, match="invalid group size"):
        group_discount(0, False)


def test_large_school_group():
    assert group_discount(25, True) == 40


def test_small_school_group():
    assert group_discount(10, True) == 25


def test_large_public_group():
    assert group_discount(15, False) == 20


def test_medium_public_group():
    assert group_discount(8, False) == 10


def test_small_public_group():
    assert group_discount(4, False) == 0


# ---------- gallery_entry ----------

def test_gallery_full_must_wait():
    assert gallery_entry(100, 100, False) == "wait"


def test_gallery_nearly_full_without_slot_queues():
    assert gallery_entry(90, 100, False) == "queue"


def test_gallery_with_space_enters():
    assert gallery_entry(10, 100, False) == "enter"
