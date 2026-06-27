def evaluate_value(value: int) -> str:
    if value == 1:
        return "Inte särskilt söt 😐"
    elif value == 2:
        return "Ganska söt 🙂"
    elif value == 3:
        return "Söt! 😊"
    elif value == 4:
        return "Väldigt söt! 😍"
    elif value == 5:
        return "Extremt söt!! 🥰"
    else:
        return "Ogiltigt värde – ange 1 till 5"