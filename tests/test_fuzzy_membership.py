"""
Gate 3 – Tests for Fuzzy Membership Definitions

Checks that:
  - All expected linguistic terms are present.
  - Universes are correctly defined.
"""

from app.control.membership import (
    create_error_antecedent,
    create_humidity_antecedent,
    create_fan_consequent,
)


def test_error_membership_terms_exist():
    error = create_error_antecedent()
    terms = set(error.terms.keys())
    expected = {"NL", "NS", "ZE", "PS", "PL"}
    assert expected.issubset(terms), f"Missing error terms: {expected - terms}"


def test_humidity_membership_terms_exist():
    humidity = create_humidity_antecedent()
    terms = set(humidity.terms.keys())
    expected = {"Dry", "Ideal", "Humid"}
    assert expected.issubset(terms), f"Missing humidity terms: {expected - terms}"


def test_fan_membership_terms_exist():
    fan = create_fan_consequent()
    terms = set(fan.terms.keys())
    expected = {"Off", "Low", "Medium", "High"}
    assert expected.issubset(terms), f"Missing fan terms: {expected - terms}"


def test_error_universe_range():
    error = create_error_antecedent()
    assert error.universe.min() <= -10.0 + 1e-9
    assert error.universe.max() >= 10.0 - 1e-9


def test_humidity_universe_range():
    humidity = create_humidity_antecedent()
    assert humidity.universe.min() <= 0.0
    assert humidity.universe.max() >= 100.0


def test_fan_universe_range():
    fan = create_fan_consequent()
    assert fan.universe.min() <= 0.0
    assert fan.universe.max() >= 100.0
