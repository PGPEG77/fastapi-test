from fastapi import FastAPI
import ValueTest1

app = FastAPI()

@app.get("/evaluate/{value}")
def evaluate(value: int):
    return {
        "value": value,
        "result": ValueTest1.evaluate_value(value),
        "even": ValueTest1.is_even(value),
        "category": ValueTest1.categorize(value)
    }