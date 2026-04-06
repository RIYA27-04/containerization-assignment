from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os
import time

app = FastAPI(title="Riya Containerized App 🚀", version="1.0.0")

# 🔹 Database config (same as docker-compose)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "riyadb")
DB_USER = os.getenv("DB_USER", "riya")
DB_PASS = os.getenv("DB_PASS", "riya123")


# 🔹 DB connection retry logic
def get_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2)
    raise Exception("Database connection failed ❌")


# 🔹 Initialize DB
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
def startup_event():
    init_db()


# 🔹 Input model
class Record(BaseModel):
    name: str


# 🔹 Health check
@app.get("/")
def home():
    return {"message": "Hello Riya 🚀 API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# 🔹 Insert data
@app.post("/add")
def add_record(record: Record):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (name) VALUES (%s) RETURNING id",
        (record.name,)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Data added ✅", "id": new_id}


# 🔹 Fetch data
@app.get("/data")
def get_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM records")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "created_at": str(row[2])
        })

    return result

