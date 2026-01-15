#!/usr/bin/env python3
"""
Function to add a list of numbers
"""


def sum_list(numbers):
    """
    Add all numbers in a list and return the total.

    Args:
        numbers: A list of numbers (int or float)

    Returns:
        The sum of all numbers in the list

    Examples:
        >>> sum_list([1, 2, 3, 4, 5])
        15
        >>> sum_list([10, 20, 30])
        60
        >>> sum_list([1.5, 2.5, 3.0])
        7.0
    """
    total = 0
    for num in numbers:
        total += num
    return total


def sum_list_builtin(numbers):
    """
    Add all numbers in a list using Python's built-in sum() function.

    Args:
        numbers: A list of numbers (int or float)

    Returns:
        The sum of all numbers in the list

    Examples:
        >>> sum_list_builtin([1, 2, 3, 4, 5])
        15
    """
    return sum(numbers)


# Example usage
if __name__ == "__main__":
    # Test with different lists
    numbers1 = [1, 2, 3, 4, 5]
    numbers2 = [10, 20, 30, 40, 50]
    numbers3 = [1.5, 2.5, 3.5, 4.5]
    numbers4 = []  # Empty list
    numbers5 = [100]  # Single number

    print("Sum List Function Examples")
    print("=" * 50)

    print(f"\nList: {numbers1}")
    print(f"Sum (loop): {sum_list(numbers1)}")
    print(f"Sum (built-in): {sum_list_builtin(numbers1)}")

    print(f"\nList: {numbers2}")
    print(f"Sum (loop): {sum_list(numbers2)}")
    print(f"Sum (built-in): {sum_list_builtin(numbers2)}")

    print(f"\nList: {numbers3}")
    print(f"Sum (loop): {sum_list(numbers3)}")
    print(f"Sum (built-in): {sum_list_builtin(numbers3)}")

    print(f"\nList: {numbers4} (empty)")
    print(f"Sum (loop): {sum_list(numbers4)}")
    print(f"Sum (built-in): {sum_list_builtin(numbers4)}")

    print(f"\nList: {numbers5} (single element)")
    print(f"Sum (loop): {sum_list(numbers5)}")
    print(f"Sum (built-in): {sum_list_builtin(numbers5)}")

    # Interactive example
    print("\n" + "=" * 50)
    print("Try your own list!")
    print("=" * 50)
    user_input = input("\nEnter numbers separated by spaces (e.g., 1 2 3 4 5): ")

    try:
        user_numbers = [float(x) for x in user_input.split()]
        result = sum_list(user_numbers)
        print(f"\nYour list: {user_numbers}")
        print(f"Sum: {result}")
    except ValueError:
        print("Invalid input. Please enter numbers separated by spaces.")
