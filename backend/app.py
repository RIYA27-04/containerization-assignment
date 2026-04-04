from fastapi import FastAPI
import psycopg2
import time
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app = FastAPI()

# wait for db to start
time.sleep(5)

conn = psycopg2.connect(
    host="db",
    database="riyadb",
    user="riya",
    password="riya123"
)

cur = conn.cursor()

@app.get("/")
def read_root():
    return {"message": "Hello Riya 🚀"}


@app.get("/data")
def get_data():
    try:
        cur.execute("SELECT * FROM test")
        rows = cur.fetchall()

        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "name": row[1]
            })

        return {
            "message": "Data fetched successfully",
            "data": data
        }

    except Exception as e:
        conn.rollback()   # 🔥 VERY IMPORTANT
        return {"error": str(e)}