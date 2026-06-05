from fastapi import FastAPI
from datetime import datetime
import ValueTest3  # din logikmodul

app = FastAPI()

LOG_FILE = "requests.log"

def log_value(value: int):
    """Loggar varje inkommande värde till en fil."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {value}\n")

@app.get("/")
def root():
    """En enkel startsida så att / inte ger 404."""
    return {"message": "API is running", "endpoints": ["/evaluate/{value}", "/logs"]}

@app.get("/evaluate/{value}")
def evaluate(value: int):
    """Tar emot ett värde, loggar det och kör din logik."""
    log_value(value)
    result = ValueTest3.evaluate_value(value)
    return {
        "value": value,
        "result": result,
        "logged": True
    }

@app.get("/logs")
def get_logs():
    """Returnerar alla loggade värden."""
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        return {"count": len(lines), "logs": lines}
    except FileNotFoundError:
        return {"count": 0, "logs": []}