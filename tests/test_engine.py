"""Tests for the calculation engine."""

from src.calculator.engine import evaluate, set_trig_mode, is_deg_mode


def setup_function():
    set_trig_mode(True)


def test_basic_arithmetic():
    assert evaluate("1+2") == "3"
    assert evaluate("10-4") == "6"
    assert evaluate("3×4") == "12"
    assert evaluate("10÷2") == "5"
    assert evaluate("5+3×2") == "11"


def test_decimal():
    assert evaluate("0.5+0.5") == "1"
    assert evaluate("0.1+0.2") == "0.3"


def test_parentheses():
    assert evaluate("(1+2)×3") == "9"
    assert evaluate("10-(3+2)") == "5"


def test_trig():
    assert evaluate("sin(0)") == "0"
    assert evaluate("sin(90)") == "1"
    assert evaluate("cos(180)") == "-1"


def test_inverse_trig():
    assert evaluate("asin(0)") == "0"
    assert evaluate("asin(1)") == "90"
    assert evaluate("acos(1)") == "0"
    assert evaluate("atan(1)") == "45"


def test_rad_mode():
    set_trig_mode(False)
    try:
        assert evaluate("sin(0)") == "0"
        from math import pi
        assert evaluate(f"sin({pi}/2)") == "1"
        assert evaluate("asin(1)") == "1.570796327"  # pi/2
    finally:
        set_trig_mode(True)


def test_sqrt():
    assert evaluate("sqrt(9)") == "3"
    assert evaluate("sqrt(2)") == "1.414213562"


def test_power():
    assert evaluate("3**2") == "9"
    assert evaluate("2**3") == "8"


def test_constants():
    assert evaluate("π") == "3.141592654"
    assert evaluate("pi") == "3.141592654"
    assert evaluate("e") == "2.718281828"


def test_log():
    assert evaluate("log(100)") == "2"
    assert evaluate("ln(1)") == "0"


def test_errors():
    assert evaluate("1/0") == "Error"
    assert evaluate("") == ""
