from fastapi import FastAPI
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import ValueTest1  # din logikmodul

app = FastAPI()

# -----------------------------
# DATABASE SETUP
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
    result = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

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
        "endpoints": ["/evaluate/{value}", "/logs"]
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