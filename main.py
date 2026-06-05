from fastapi import FastAPI
import ValueTest3

app = FastAPI()

@app.get("/evaluate/{value}")
def evaluate(value: int):
    return {
        "value": value,
        "result": ValueTest3.evaluate_value(value),
        "even": ValueTest3.is_even(value),
        "category": ValueTest3.categorize(value)
    }