def main():
    value = int(input("Skriv ett tal: "))

    if value > 10:
        print("Value is greater than 10")
    elif value > 5:
        print("Value is greater than 5 but not above 10")
    else:
        print("Value is 5 or less")

if __name__ == "__main__":
    main()