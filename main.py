from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, User, Todo
from schemas import UserSignup, UserLogin, TaskCreate, TaskUpdate
from auth_utils import hash_password, verify_password
from auth_jwt import create_token
from auth_dependency import get_current_user

from soil import get_soil_data
from weather_service import get_weather


app = FastAPI()

Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 🔐 AUTH
# =========================

@app.post("/signup")
def signup(data: UserSignup, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
    )

    db.add(user)
    db.commit()

    return {"message": "User created successfully"}


@app.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "id": user.id,
        "name": user.name
    })

    return {"token": token}


@app.get("/me")
def get_me(user=Depends(get_current_user)):
    return user


# =========================
# 📝 TASK ROUTES
# =========================

# ➤ Add task
@app.post("/tasks")
def add_task(data: TaskCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):

    task = Todo(
        user_id=user["id"],
        text=data.text,
        status="to do"
    )

    db.add(task)
    db.commit()

    return {"message": "Task added"}


# ➤ Get tasks
@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):

    tasks = db.query(Todo).filter(Todo.user_id == user["id"]).all()

    return [
        {"id": t.id, "text": t.text, "status": t.status}
        for t in tasks
    ]


# ➤ Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    task = db.query(Todo).filter(
        Todo.id == task_id,
        Todo.user_id == user["id"]
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Deleted"}


# ➤ Update task status
@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):

    task = db.query(Todo).filter(
        Todo.id == task_id,
        Todo.user_id == user["id"]
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = data.status
    db.commit()

    return {"message": "Updated"}


# =========================
# 🌱 EXISTING ROUTES
# =========================

@app.get("/")
def root():
    return {"message": "API working"}


@app.get("/data")
def get_data(
    lat: float,
    lon: float,
    crop: str,
    season: str,
    stage: str,
    irrigation: str
):
    soil_data = get_soil_data(lat, lon)
    if "error" in soil_data:
        return soil_data

    weather = get_weather(lat, lon)
    if "error" in weather:
        return weather

    return {
        **soil_data,
        **weather,
        "Crop_Type": crop,
        "Crop_Growth_Stage": stage,
        "Season": season,
        "Irrigation_Type": irrigation
    }