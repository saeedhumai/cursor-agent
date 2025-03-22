def add(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a and return the result."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the result."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b and return the result."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


# TODO: Implement multiply and divide functions

if __name__ == "__main__":
    print(f"1 + 2 = {add(1, 2)}")
    print(f"5 - 3 = {subtract(5, 3)}")
    print(f"2 * 3 = {multiply(2, 3)}")
    print(f"6 / 3 = {divide(6, 3)}")
