from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import ValueTest1
import SweetTest1

app = FastAPI()

# -----------------------------
# DATABASE SETUP (DELAYED INIT)
# -----------------------------
engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)
Base = declarative_base()


class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
    result = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SweetEntry(Base):
    __tablename__ = "sweet_entries"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
    result = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


def get_engine():
    url = os.getenv("DATABASE_URL")
    print("DEBUG_DATABASE_URL:", url)

    if not url:
        raise RuntimeError("DATABASE_URL is missing or empty!")

    return create_engine(url)


@app.on_event("startup")
def startup_event():
    global engine
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


# -----------------------------
# HELPERS
# -----------------------------
def save_log(value: int, result: str):
    db = SessionLocal()
    entry = LogEntry(value=value, result=result)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    db.close()
    return entry


def save_sweet(value: int, result: str):
    db = SessionLocal()
    entry = SweetEntry(value=value, result=result)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    db.close()
    return entry


# -----------------------------
# ENDPOINTS
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "API with PostgreSQL is running",
        "endpoints": ["/evaluate/{value}", "/logs", "/logs/view", "/form", "/rebecka", "/rebecka/view"]
    }


@app.get("/evaluate/{value}")
def evaluate(value: int):
    result = ValueTest1.evaluate_value(value)
    entry = save_log(value, result)
    return {
        "value": value,
        "result": result,
        "timestamp": entry.timestamp.isoformat()
    }


@app.get("/logs")
def get_logs():
    db = SessionLocal()
    entries = db.query(LogEntry).order_by(LogEntry.id.desc()).all()
    db.close()

    return {
        "count": len(entries),
        "logs": [
            {
                "id": e.id,
                "value": e.value,
                "result": e.result,
                "timestamp": e.timestamp.isoformat()
            }
            for e in entries
        ]
    }


@app.get("/logs/view", response_class=HTMLResponse)
def view_logs():
    db = SessionLocal()
    entries = db.query(LogEntry).order_by(LogEntry.id.desc()).all()
    db.close()

    rows = "".join(
        f"<tr><td>{e.id}</td><td>{e.value}</td><td>{e.result}</td><td>{e.timestamp.isoformat()}</td></tr>"
        for e in entries
    )

    html = f"""
    <html><head><title>Loggar</title></head>
    <body>
    <h2>Loggade värden</h2>
    <table border="1" cellpadding="8">
        <tr><th>ID</th><th>Värde</th><th>Resultat</th><th>Tid</th></tr>
        {rows}
    </table>
    </body></html>
    """
    return html


@app.get("/form", response_class=HTMLResponse)
def show_form():
    html = """
    <html><head><title>Testa ett värde</title></head>
    <body>
    <h2>Slå in ett värde</h2>
    <form method="post" action="/form/submit">
        <input type="number" name="value" placeholder="Skriv ett heltal" required>
        <button type="submit">Skicka</button>
    </form>
    </body></html>
    """
    return html


@app.post("/form/submit", response_class=HTMLResponse)
def submit_form(value: int = Form(...)):
    result = ValueTest1.evaluate_value(value)
    save_log(value, result)

    html = f"""
    <html><head><title>Resultat</title></head>
    <body>
    <h2>Resultat</h2>
    <p><strong>Värde:</strong> {value}</p>
    <p><strong>Utfall:</strong> {result}</p>
    <br>
    <a href="/form">⬅ Testa ett nytt värde</a> &nbsp;|&nbsp;
    <a href="/logs/view">📋 Visa alla loggar</a>
    </body></html>
    """
    return html


@app.get("/rebecka", response_class=HTMLResponse)
def rebecka_form():
    html = """
    <html><head><title>Hur söt är Rebecka?</title></head>
    <body>
    <h2>Hur söt är Rebecka? 🥰</h2>
    <form method="post" action="/rebecka/submit">
        <p>Välj ett värde mellan 1 och 5:</p>
        <input type="number" name="value" min="1" max="5" placeholder="1-5" required>
        <button type="submit">Skicka</button>
    </form>
    <br>
    <a href="/rebecka/view">📊 Visa resultat</a>
    </body></html>
    """
    return html


@app.post("/rebecka/submit", response_class=HTMLResponse)
def rebecka_submit(value: int = Form(...)):
    result = SweetTest1.evaluate_value(value)
    save_sweet(value, result)

    html = f"""
    <html><head><title>Resultat</title></head>
    <body>
    <h2>Resultat 🥰</h2>
    <p><strong>Din röst:</strong> {value} av 5</p>
    <p><strong>Utfall:</strong> {result}</p>
    <br>
    <a href="/rebecka">⬅ Rösta igen</a> &nbsp;|&nbsp;
    <a href="/rebecka/view">📊 Visa alla röster</a>
    </body></html>
    """
    return html


@app.get("/rebecka/view", response_class=HTMLResponse)
def rebecka_view():
    db = SessionLocal()
    entries = db.query(SweetEntry).all()
    db.close()

    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for e in entries:
        if e.value in counts:
            counts[e.value] += 1

    total = len(entries)
    average = round(sum(e.value for e in entries) / total, 2) if total > 0 else 0

    labels = ["1 😐", "2 🙂", "3 😊", "4 😍", "5 🥰"]
    values = [counts[i] for i in range(1, 6)]

    html = f"""
    <html>
    <head>
        <title>Hur söt är Rebecka?</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
    <h2>Hur söt är Rebecka? 🥰</h2>
    <p><strong>Antal röster:</strong> {total} &nbsp;|&nbsp; <strong>Snitt:</strong> {average} / 5</p>
    <canvas id="chart" width="400" height="300"></canvas>
    <script>
        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: 'Antal röster',
                    data: {values},
                    backgroundColor: ['#f87171','#fb923c','#facc15','#4ade80','#f472b6'],
                }}]
            }},
            options: {{
                scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
    </script>
    <br><br>
    <a href="/rebecka">⬅ Rösta</a>
    </body>
    </html>
    """
    return html