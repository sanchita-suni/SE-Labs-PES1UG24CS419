# L6_L7_54 — Museum Admission

Lab 6: Code and Branch Coverage

## About

A small Python module that prices museum tickets by visitor category, day and guided tour, works out group discounts and decides whether visitors may enter a busy gallery.

## Files

| File | Description |
|------|-------------|
| `museum_admission.py` | The module under test |
| `test_museum_admission.py` | Starter test file |

Keep all your Lab 6 work in this `LAB6` folder. Lab 7 will be added to this repo later.

Refer to the lab handout for instructions.

## Lab 6 results

| Test file | Tests | Line coverage | Branch coverage |
|---|---|---|---|
| `test_museum_admission.py` (starter) | 2 | 47% | 42% |
| `CodeCoverageTest_54_museum_admission.py` | 14 | 100% | 97% (missing 14->16, 16->21) |
| `BranchCoverageTest_54_museum_admission.py` | 36 | 100% | 100% |

The code coverage tests run every line, but never take the path where the day is an ordinary weekday (neither Monday nor weekend) or where no guided tour is booked. The branch coverage tests add those paths and the boundary values of each rule (age 5, group sizes 8, 15 and 20, gallery at 89% and 90%, timed slot at 90%).

```
pip install coverage pytest
cd LAB6
coverage run -m pytest CodeCoverageTest_54_museum_admission.py && coverage report -m
coverage run --branch -m pytest BranchCoverageTest_54_museum_admission.py && coverage report -m
```

Screenshots are in `screenshots/`.
