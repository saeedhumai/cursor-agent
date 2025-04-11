def divide(a, b):
    """
    Divide two numbers.
    
    Parameters:
    a (int): The numerator.
    b (int): The denominator.
    
    Returns:
    float: The result of the division.
    
    Raises:
    ValueError: If the denominator is zero.
    TypeError: If inputs are not integers.
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError('Inputs must be integers')
    if b == 0:
        raise ValueError('Division by zero is not allowed')
    return a / b