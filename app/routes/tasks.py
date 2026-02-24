from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from datetime import datetime
from app.websocket.manager import manager
from sqlalchemy import and_
import asyncio



router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/create", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):

    # 1️⃣ Create task as pending
    new_task = models.Task(
        forklift_type=task.forklift_type.strip(),
        cell_number=task.cell_number,
        status="pending",
        created_at=datetime.utcnow()
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 2️⃣ Find available forklift
    available_forklift = db.query(models.Forklift).filter(
        and_(
            models.Forklift.status == "available",
            models.Forklift.forklift_type.ilike(task.forklift_type.strip())
        )
    ).first()

    # 3️⃣ Assign if found
    if available_forklift:

        new_task.status = "assigned"
        new_task.assigned_forklift = available_forklift.id
        new_task.assigned_at = datetime.utcnow()

        available_forklift.status = "engaged"

        db.commit()
        db.refresh(new_task)

        print(f"✅ Task {new_task.id} assigned to forklift {available_forklift.id}")

        # 🔥 Notify ONLY assigned forklift
        await manager.notify_forklift(
            available_forklift.id,
            {
                "event": "new_task",
                "task_id": new_task.id,
                "cell_number": new_task.cell_number
            }
        )

        # 🔹 Notify cell
        await manager.notify_cell(
            task.cell_number,
            {
                "event": "task_assigned",
                "task_id": new_task.id,
                "assigned_forklift": available_forklift.id
            }
        )

    else:
        print("⚠ No available forklift found")

        await manager.notify_cell(
            task.cell_number,
            {
                "event": "pending_task",
                "task_id": new_task.id,
                "forklift_type": task.forklift_type
            }
        )

    # 🔹 Update admin dashboard
    await manager.broadcast_live_update(db)

    return new_task


@router.get("/")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks


@router.put("/complete/{task_id}")
async def complete_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        return {"error": "Task not found"}

    forklift = db.query(models.Forklift).filter(
        models.Forklift.id == task.assigned_forklift
    ).first()

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    if forklift:
        forklift.status = "available"

    db.commit()


    await manager.broadcast_live_update(db)

    return {"message": "Task completed"}
