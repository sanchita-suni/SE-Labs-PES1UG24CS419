from hypothesis import given, strategies as st
from museum_admission_parser import format_visitor_name, parse_group_ages, parse_visit_date


@given(st.text() | st.none())
def test_format_visitor_name_no_crash(s):
    try:
        result = format_visitor_name(s)
    except Exception as e:
        assert False, f"format_visitor_name crashed on {s!r}: {type(e).__name__}: {e}"
    # Valid input gives a string, invalid input gives None
    assert result is None or isinstance(result, str)


@given(st.text() | st.none())
def test_parse_group_ages_no_crash(s):
    try:
        result = parse_group_ages(s)
    except Exception as e:
        assert False, f"parse_group_ages crashed on {s!r}: {type(e).__name__}: {e}"
    # Valid input gives a list of whole-number ages, invalid input gives None
    assert result is None or all(isinstance(age, int) and age >= 0 for age in result)


@given(st.text() | st.none())
def test_parse_visit_date_no_crash(s):
    try:
        result = parse_visit_date(s)
    except Exception as e:
        assert False, f"parse_visit_date crashed on {s!r}: {type(e).__name__}: {e}"
    # Valid input gives a (year, month, day) tuple, invalid input gives None
    assert result is None or (isinstance(result, tuple) and len(result) == 3)
