from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import ValueTest1  # din logikmodul

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


# -----------------------------
# ENDPOINTS
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "API with PostgreSQL is running",
        "endpoints": ["/evaluate/{value}", "/logs", "/logs/view"]
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
