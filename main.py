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
# SHARED CSS
# -----------------------------
STYLE = """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding: 40px 16px;
        }
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 40px;
            width: 100%;
            max-width: 500px;
        }
        h2 {
            font-size: 1.6rem;
            color: #1a1a2e;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #6b7280;
            font-size: 0.95rem;
            margin-bottom: 28px;
        }
        .btn-group {
            display: flex;
            gap: 12px;
            margin: 24px 0;
        }
        .btn {
            flex: 1;
            padding: 16px 8px;
            font-size: 1.4rem;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.15s;
            text-align: center;
        }
        .btn:hover { border-color: #2563eb; background: #eff6ff; }
        .btn.selected { border-color: #2563eb; background: #2563eb; color: white; }
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
            margin-top: 8px;
        }
        .submit-btn:hover { background: #1d4ed8; }
        .submit-btn:disabled { background: #93c5fd; cursor: not-allowed; }
        .result-value {
            font-size: 3rem;
            text-align: center;
            margin: 16px 0 8px;
        }
        .result-text {
            font-size: 1.2rem;
            color: #374151;
            text-align: center;
            margin-bottom: 28px;
        }
        .stats {
            background: #f9fafb;
            border-radius: 8px;
            padding: 16px;
            display: flex;
            justify-content: space-around;
            margin-bottom: 28px;
        }
        .stat { text-align: center; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: #2563eb; }
        .stat-label { font-size: 0.8rem; color: #6b7280; margin-top: 2px; }
        .links { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
        .link {
            color: #2563eb;
            text-decoration: none;
            font-size: 0.9rem;
            padding: 8px 16px;
            border: 1px solid #2563eb;
            border-radius: 6px;
            transition: all 0.15s;
        }
        .link:hover { background: #2563eb; color: white; }
        .reset-link {
            color: #9ca3af;
            text-decoration: none;
            font-size: 0.8rem;
            display: block;
            text-align: center;
            margin-top: 20px;
        }
        .reset-link:hover { color: #ef4444; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th { background: #f9fafb; color: #6b7280; font-size: 0.8rem; text-transform: uppercase; padding: 10px 12px; text-align: left; }
        td { padding: 12px; border-top: 1px solid #f3f4f6; font-size: 0.95rem; }
        tr:hover td { background: #f9fafb; }
    </style>
"""


# -----------------------------
# ENDPOINTS
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "API with PostgreSQL is running",
        "endpoints": ["/evaluate/{value}", "/logs", "/logs/view", "/form", "/rebecka", "/rebecka/view", "/rebecka/reset", "/rebecka/debug"]
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
    <html><head><title>Loggar</title>{STYLE}</head>
    <body>
    <div class="card" style="max-width:700px">
    <h2>Loggade värden</h2>
    <p class="subtitle">Alla körningar sparade i databasen</p>
    <table>
        <tr><th>ID</th><th>Värde</th><th>Resultat</th><th>Tid</th></tr>
        {rows}
    </table>
    </div>
    </body></html>
    """
    return html


@app.get("/form", response_class=HTMLResponse)
def show_form():
    html = f"""
    <html><head><title>Testa ett värde</title>{STYLE}</head>
    <body>
    <div class="card">
    <h2>Testa ett värde</h2>
    <p class="subtitle">Ange ett heltal och se vad logiken svarar</p>
    <form method="post" action="/form/submit">
        <input type="number" name="value" placeholder="Skriv ett heltal" required
            style="width:100%;padding:12px;border:2px solid #e5e7eb;border-radius:8px;font-size:1rem;margin-bottom:12px;">
        <button type="submit" class="submit-btn">Skicka</button>
    </form>
    </div>
    </body></html>
    """
    return html


@app.post("/form/submit", response_class=HTMLResponse)
def submit_form(value: int = Form(...)):
    result = ValueTest1.evaluate_value(value)
    save_log(value, result)

    html = f"""
    <html><head><title>Resultat</title>{STYLE}</head>
    <body>
    <div class="card">
    <h2>Resultat</h2>
    <p class="subtitle">Värde utvärderat och sparat</p>
    <div class="result-value">{value}</div>
    <div class="result-text">{result}</div>
    <div class="links">
        <a href="/form" class="link">⬅ Testa igen</a>
        <a href="/logs/view" class="link">📋 Visa loggar</a>
    </div>
    </div>
    </body></html>
    """
    return html


@app.get("/rebecka", response_class=HTMLResponse)
def rebecka_form():
    html = f"""
    <html>
    <head><title>Hur söt är Rebecka?</title>{STYLE}</head>
    <body>
    <div class="card">
        <h2>Hur söt är Rebecka?</h2>
        <p class="subtitle">Välj ett betyg från 1 till 5 och skicka in din röst</p>
        <form method="post" action="/rebecka/submit">
            <input type="hidden" name="value" id="hiddenValue">
            <div class="btn-group">
                <button type="button" class="btn" onclick="select(1)">😐<br><small>1</small></button>
                <button type="button" class="btn" onclick="select(2)">🙂<br><small>2</small></button>
                <button type="button" class="btn" onclick="select(3)">😊<br><small>3</small></button>
                <button type="button" class="btn" onclick="select(4)">😍<br><small>4</small></button>
                <button type="button" class="btn" onclick="select(5)">🥰<br><small>5</small></button>
            </div>
            <button type="submit" class="submit-btn" id="submitBtn" disabled>Välj ett betyg</button>
        </form>
        <div class="links" style="margin-top:24px">
            <a href="/rebecka/view" class="link">📊 Visa resultat</a>
        </div>
    </div>
    <script>
        function select(val) {{
            document.getElementById('hiddenValue').value = val;
            document.querySelectorAll('.btn').forEach((b, i) => {{
                b.classList.toggle('selected', i + 1 === val);
            }});
            const btn = document.getElementById('submitBtn');
            btn.disabled = false;
            btn.textContent = 'Skicka röst';
        }}
    </script>
    </body>
    </html>
    """
    return html


@app.post("/rebecka/submit", response_class=HTMLResponse)
def rebecka_submit(value: int = Form(...)):
    result = SweetTest1.evaluate_value(value)
    save_sweet(value, result)

    stars = "⭐" * value

    html = f"""
    <html><head><title>Tack för din röst!</title>{STYLE}</head>
    <body>
    <div class="card">
        <h2>Tack för din röst!</h2>
        <p class="subtitle">Din röst har sparats</p>
        <div class="result-value">{stars}</div>
        <div class="result-text">{result}</div>
        <div class="links">
            <a href="/rebecka" class="link">⬅ Rösta igen</a>
            <a href="/rebecka/view" class="link">📊 Visa resultat</a>
        </div>
    </div>
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
        {STYLE}
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
    <div class="card">
        <h2>Hur söt är Rebecka?</h2>
        <p class="subtitle">Sammanställning av alla röster</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Antal röster</div>
            </div>
            <div class="stat">
                <div class="stat-value">{average}</div>
                <div class="stat-label">Snittbetyg</div>
            </div>
            <div class="stat">
                <div class="stat-value">/ 5</div>
                <div class="stat-label">Max betyg</div>
            </div>
        </div>
        <canvas id="chart" height="200"></canvas>
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
                        borderRadius: 6,
                    }}]
                }},
                options: {{
                    scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }},
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
        </script>
        <div class="links" style="margin-top:28px">
            <a href="/rebecka" class="link">⬅ Rösta</a>
        </div>
        <a href="/rebecka/reset" class="reset-link">Nollställ omröstningen</a>
    </div>
    </body>
    </html>
    """
    return html


@app.get("/rebecka/reset", response_class=HTMLResponse)
def rebecka_reset():
    db = SessionLocal()
    db.query(SweetEntry).delete()
    db.commit()
    db.close()

    html = f"""
    <html><head><title>Nollställd</title>{STYLE}</head>
    <body>
    <div class="card" style="text-align:center">
        <h2>✅ Omröstningen är nollställd!</h2>
        <p class="subtitle" style="margin-bottom:28px">All data har raderats från databasen</p>
        <div class="links">
            <a href="/rebecka" class="link">⬅ Starta om</a>
            <a href="/rebecka/view" class="link">📊 Visa resultat</a>
        </div>
    </div>
    </body></html>
    """
    return html


@app.get("/rebecka/debug")
def rebecka_debug():
    db = SessionLocal()
    entries = db.query(SweetEntry).all()
    db.close()
    return {"count": len(entries), "entries": [{"id": e.id, "value": e.value, "result": e.result} for e in entries]}