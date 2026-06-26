def main():
    value = int(input("Skriv ett tal: "))
    print(evaluate_value(value))

def evaluate_value(value):
    if value > 10:
        return "Value is greater than 10"
    elif value > 5:
        return "Value is greater than 5 but not above 10"
    else:
        return "Value is 5 or less"

if __name__ == "__main__":
    main()