"""Chai Counter's tests: GitHub Actions runs them on every push (.github/workflows/cicd.yml)."""
from app import total_for


def test_two_cups():
    assert total_for(2) == 40


def test_offer_five_cups_pay_for_four():
    assert total_for(5) == 80
