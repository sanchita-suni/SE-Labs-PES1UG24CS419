import re
from datetime import date

MAX_AGE = 120
_AGE_PATTERN = re.compile(r"[0-9]+")
_DATE_PATTERN = re.compile(r"([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})")


def format_visitor_name(name):
    """
    Formats a full name as 'Surname, Given names' for the ticket.
    Returns None if name is not a string or has no words.
    """
    if not isinstance(name, str):
        return None
    parts = name.split()
    if not parts:
        return None
    surname = parts[-1].title()
    given = ' '.join(parts[:-1]).title()
    # A single-word name has no given names, so no trailing comma
    return f"{surname}, {given}" if given else surname


def parse_group_ages(text):
    """
    Parses space-separated ages into a list of ints.
    Returns None if text is not a string, is empty, or any value is not a
    whole number from 0 to MAX_AGE.
    """
    if not isinstance(text, str):
        return None
    values = text.split()
    if not values:
        return None
    ages = []
    for value in values:
        # Only plain ASCII digits: rejects '-5', '1.5', '²' and other
        # characters that str.isdigit() or int() would treat differently
        if not _AGE_PATTERN.fullmatch(value):
            return None
        age = int(value)
        if age > MAX_AGE:
            return None
        ages.append(age)
    return ages


def parse_visit_date(text):
    """
    Parses a YYYY-MM-DD date into a (year, month, day) tuple.
    Returns None if text is not a string or not a real calendar date.
    """
    if not isinstance(text, str):
        return None
    match = _DATE_PATTERN.fullmatch(text.strip())
    if not match:
        return None
    year, month, day = (int(part) for part in match.groups())
    try:
        date(year, month, day)  # rejects 2026-02-30, month 13, year 0
    except ValueError:
        return None
    return year, month, day


def main():
    print("==== Running format_visitor_name ====")
    value = input("Enter a visitor's full name (e.g. asha rao): ")
    result = format_visitor_name(value)
    print("Name on ticket:", result if result is not None else "Invalid name, please enter at least one word.")

    print("\n==== Running parse_group_ages ====")
    value = input("Enter the ages in the group separated by spaces (e.g. 34 12 70): ")
    result = parse_group_ages(value)
    print("Group ages:", result if result is not None else f"Invalid ages, use whole numbers from 0 to {MAX_AGE}.")

    print("\n==== Running parse_visit_date ====")
    value = input("Enter the visit date as YYYY-MM-DD (e.g. 2026-11-05): ")
    result = parse_visit_date(value)
    print("Visit date (year, month, day):", result if result is not None else "Invalid date, use a real date as YYYY-MM-DD.")


if __name__ == "__main__":
    main()
