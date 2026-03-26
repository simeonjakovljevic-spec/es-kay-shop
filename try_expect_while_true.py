while True:
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        result = num1 + num2
        print(f"Addition result: {result}")
        break
    except ValueError:
        print("Invalid input. Please enter numbers.")
