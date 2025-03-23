def factorial(n: int) -> int:
    """
    Calculate the factorial of a number using recursion.
    
    Args:
        n (int): A non-negative integer to calculate factorial for
        
    Returns:
        int: The factorial of n (n!)
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


# Example usage
if __name__ == "__main__":
    # Test cases
    test_numbers = [0, 1, 5, 7]
    
    for num in test_numbers:
        result = factorial(num)
        print(f"factorial({num}) = {result}")