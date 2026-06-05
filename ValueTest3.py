def evaluate_value(value):
    if value > 10:
        return "Value is greater than 10"
    elif value > 5:
        return "Value is greater than 5 but not above 10"
    else:
        return "Value is 5 or less"


def is_even(value):
    return value % 2 == 0


def categorize(value):
    if value < 0:
        return "Negative number"
    elif value == 0:
        return "Zero"
    elif value < 10:
        return "Small positive number"
    else:
        return "Large positive number"


def main():
    value = int(input("Skriv ett tal: "))

    print("Resultat från evaluate_value:", evaluate_value(value))
    print("Är talet jämnt?:", is_even(value))
    print("Kategori:", categorize(value))


if __name__ == "__main__":
    main()