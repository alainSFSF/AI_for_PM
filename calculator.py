# Simple Calculator - Performs basic arithmetic operations on integers

import math

print("Welcome to the Simple Calculator!")
print("Type 'q' or 'quit' at any time to exit.\n")

while True:
    # Get operation choice from user
    print("Select operation:")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division (with quotient and remainder)")
    print("5. Square Root")
    operation = input("Enter your choice (1, 2, 3, 4, or 5): ").strip().lower()

    # Check if user wants to quit
    if operation == 'q' or operation == 'quit':
        print("Thank you for using the calculator. Goodbye!")
        break

    # Validate operation choice
    if operation not in ['1', '2', '3', '4', '5']:
        print("Invalid choice. Please select 1, 2, 3, 4, or 5.\n")
        continue

    # For square root, only need one number
    if operation == "5":
        num_input = input("Enter an integer: ").strip().lower()
        if num_input == 'q' or num_input == 'quit':
            print("Thank you for using the calculator. Goodbye!")
            break

        try:
            num = int(num_input)
        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")
            continue
    else:
        # Get first integer from user
        num1_input = input("Enter the first integer: ").strip().lower()
        if num1_input == 'q' or num1_input == 'quit':
            print("Thank you for using the calculator. Goodbye!")
            break

        try:
            num1 = int(num1_input)
        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")
            continue

        # Get second integer from user
        num2_input = input("Enter the second integer: ").strip().lower()
        if num2_input == 'q' or num2_input == 'quit':
            print("Thank you for using the calculator. Goodbye!")
            break

        try:
            num2 = int(num2_input)
        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")
            continue

    # Perform the selected operation
    if operation == "1":
        result = num1 + num2
        print(f"The sum of {num1} and {num2} is: {result}")
    elif operation == "2":
        result = num1 - num2
        print(f"The difference of {num1} and {num2} is: {result}")
    elif operation == "3":
        result = num1 * num2
        print(f"The product of {num1} and {num2} is: {result}")
    elif operation == "4":
        if num2 == 0:
            print("Error: Division by zero is not allowed.")
        else:
            quotient = num1 // num2
            remainder = num1 % num2
            print(f"{num1} divided by {num2} is: {quotient} with remainder {remainder}")
    elif operation == "5":
        if num < 0:
            print("Error: Cannot calculate the square root of a negative number.")
        else:
            result = math.sqrt(num)
            print(f"The square root of {num} is: {result}")

    print()  # Add blank line for readability
