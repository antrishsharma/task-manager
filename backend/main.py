import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


class TaskIn(BaseModel):
    title: str


@app.get("/")
def home():
    return {"message": "Task Manager API is running"}


@app.get("/tasks")
def get_tasks():
    with get_db() as conn:
        return conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()


@app.post("/tasks")
def add_task(task: TaskIn):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
            (task.title,),
        )
        return cur.fetchone()


@app.put("/tasks/{task_id}/done")
def mark_done(task_id: int):
    with get_db() as conn:
        cur = conn.execute("UPDATE tasks SET done = true WHERE id = %s", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task marked as done"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}