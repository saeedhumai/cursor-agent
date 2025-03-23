# Factorial Calculator

A simple Python implementation of a recursive factorial calculator.

## Function Description

The `factorial(n)` function calculates the factorial of a non-negative integer using recursion.

### Usage

```python
from factorial import factorial

# Calculate factorial of 5
result = factorial(5)  # returns 120
```

### Parameters

- `n` (int): A non-negative integer

### Returns

- The factorial of n (n!)

### Exceptions

- Raises `ValueError` if n is negative

### Example Results

- factorial(0) = 1
- factorial(1) = 1
- factorial(5) = 120
- factorial(7) = 5040