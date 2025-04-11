#!/usr/bin/env python3

def hello_world():
    print("Hello, World!")

def add(a, b):
    # Add two numbers
    return a + b

def multiply(a, b):
    # Multiply two numbers
    return a * b

def main():
    hello_world()
    result1 = add(5, 3)
    result2 = multiply(4, 2)
    print(f"Addition result: {result1}")
    print(f"Multiplication result: {result2}")

if __name__ == "__main__":
    main()
