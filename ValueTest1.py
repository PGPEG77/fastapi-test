def evaluate_value(value: int) -> str:
    if value > 10:
        return "Value is greater than 10"
    elif value > 5:
        return "Value is greater than 5 but not above 10"
    else:
        return "Value is 5 or less"