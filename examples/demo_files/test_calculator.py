import calculator


def test_add():
    assert calculator.add(1, 2) == 3
    assert calculator.add(-1, 1) == 0
    assert calculator.add(0, 0) == 0


def test_subtract():
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(-1, 1) == -2
    assert calculator.subtract(0, 0) == 0


def test_multiply():
    assert calculator.multiply(2, 3) == 6
    assert calculator.multiply(-1, 1) == -1
    assert calculator.multiply(0, 5) == 0


def test_divide():
    assert calculator.divide(6, 3) == 2
    assert calculator.divide(-6, 2) == -3
    assert calculator.divide(5, 2) == 2.5
    try:
        calculator.divide(5, 0)
        assert False, "Expected ZeroDivisionError"
    except ZeroDivisionError:
        pass


if __name__ == "__main__":
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
    print("All tests passed!")
