def factorial(n):
    """
    Calculates the factorial of a non-negative integer n.

    The factorial of n is the product of all positive integers less than or equal to n.
    It is denoted as n! and is defined as:
    0! = 1
    n! = n * (n-1) * (n-2) * ... * 3 * 2 * 1

    Args:
        n (int): The non-negative integer to calculate the factorial of.

    Returns:
        int: The factorial of n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers")

    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
