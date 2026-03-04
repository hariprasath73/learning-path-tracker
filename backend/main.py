from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "learning")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


class Phase(BaseModel):
    name: str


class Task(BaseModel):
    phase_id: int
    title: str


@app.get("/phases")
def get_phases():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM phases;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"id": r[0], "name": r[1]} for r in rows]


@app.post("/phases")
def create_phase(phase: Phase):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO phases (name) VALUES (%s);", (phase.name,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Phase created"}


@app.get("/tasks/{phase_id}")
def get_tasks(phase_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, completed FROM tasks WHERE phase_id = %s;",
        (phase_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"id": r[0], "title": r[1], "completed": r[2]}
        for r in rows
    ]


@app.post("/tasks")
def create_task(task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (phase_id, title, completed) VALUES (%s, %s, %s);",
        (task.phase_id, task.title, False)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Task created"}


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET completed = TRUE WHERE id = %s;",
        (task_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Task marked complete"}
