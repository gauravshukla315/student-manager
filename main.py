from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import json
import os

app = FastAPI(title="Student Manager API")

DATA_FILE = "students.json"

# ---------- helpers ----------

def load_students():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_students(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------- models ----------

class Student(BaseModel):
    name: str
    standard: str
    description: Optional[str] = ""
    marks: Optional[float] = 0.0

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    standard: Optional[str] = None
    description: Optional[str] = None
    marks: Optional[float] = None

# ---------- routes ----------

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/students")
def get_all_students():
    students = load_students()
    return {"students": [{"id": k, **v} for k, v in students.items()]}

@app.get("/students/{student_id}")
def get_student(student_id: str):
    students = load_students()
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student_id, **students[student_id]}

@app.post("/students/{student_id}", status_code=201)
def add_student(student_id: str, student: Student):
    students = load_students()
    if student_id in students:
        raise HTTPException(status_code=409, detail="Student ID already exists")
    students[student_id] = student.dict()
    save_students(students)
    return {"message": "Student added", "id": student_id, **student.dict()}

@app.put("/students/{student_id}")
def update_student(student_id: str, update: StudentUpdate):
    students = load_students()
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in update.dict(exclude_none=True).items():
        students[student_id][field] = value
    save_students(students)
    return {"message": "Student updated", "id": student_id, **students[student_id]}

@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    students = load_students()
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]
    save_students(students)
    return {"message": "Student deleted", "id": student_id}

# ---------- serve static ----------
app.mount("/static", StaticFiles(directory="static"), name="static")
