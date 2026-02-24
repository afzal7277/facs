from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from app.database import SessionLocal
from app import models
from app.models import Task, Forklift

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app import models

@router.get("/config")
def get_config(db: Session = Depends(get_db)):

    config = db.query(models.SystemConfig).first()
    return config


@router.put("/config")
def update_config(timeout_minutes: int,
                  db: Session = Depends(get_db)):

    config = db.query(models.SystemConfig).first()

    if not config:
        config = models.SystemConfig(
            task_timeout_minutes=timeout_minutes
        )
        db.add(config)
    else:
        config.task_timeout_minutes = timeout_minutes

    db.commit()
    return {"message": "Config updated"}



@router.get("/completed-today")
def completed_today(db: Session = Depends(get_db)):

    today = datetime.utcnow().date()

    tasks = db.query(Task).filter(
        Task.status == "completed",
        extract("day", Task.completed_at) == today.day,
        extract("month", Task.completed_at) == today.month,
        extract("year", Task.completed_at) == today.year
    ).all()

    return tasks

@router.get("/completed-month")
def completed_month(db: Session = Depends(get_db)):

    now = datetime.utcnow()

    tasks = db.query(Task).filter(
        Task.status == "completed",
        extract("month", Task.completed_at) == now.month,
        extract("year", Task.completed_at) == now.year
    ).all()

    return tasks

@router.get("/completed-previous-month")
def completed_previous_month(db: Session = Depends(get_db)):

    now = datetime.utcnow()
    prev_month = now.month - 1 or 12
    year = now.year if now.month != 1 else now.year - 1

    tasks = db.query(Task).filter(
        Task.status == "completed",
        extract("month", Task.completed_at) == prev_month,
        extract("year", Task.completed_at) == year
    ).all()

    return tasks

@router.get("/forklifts")
def get_all_forklifts(db: Session = Depends(get_db)):
    return db.query(Forklift).all()

@router.get("/cells")
def get_active_cells(db: Session = Depends(get_db)):

    cells = db.query(Task.cell_number).distinct().all()
    return [c[0] for c in cells]


@router.get("/overview")
def admin_overview(db: Session = Depends(get_db)):

    # Forklift counts
    available = db.query(models.Forklift).filter(
        models.Forklift.status == "available"
    ).count()

    engaged = db.query(models.Forklift).filter(
        models.Forklift.status == "engaged"
    ).count()

    leave = db.query(models.Forklift).filter(
        models.Forklift.status == "leave"
    ).count()

    # Task counts
    pending = db.query(models.Task).filter(
        models.Task.status == "pending"
    ).count()

    assigned = db.query(models.Task).filter(
        models.Task.status == "assigned"
    ).count()

    today = date.today()

    completed_today = db.query(models.Task).filter(
        models.Task.status == "completed",
        func.date(models.Task.completed_at) == today
    ).count()

    # Active cells (cells with pending or assigned tasks)
    active_cells = db.query(models.Task.cell_number).filter(
        models.Task.status.in_(["pending", "assigned"])
    ).distinct().count()

    return {
        "forklifts": {
            "available": available,
            "engaged": engaged,
            "leave": leave
        },
        "tasks": {
            "pending": pending,
            "assigned": assigned,
            "completed_today": completed_today
        },
        "cells": {
            "active": active_cells
        }
    }


@router.get("/live-overview")
def live_overview(db: Session = Depends(get_db)):

    forklifts = db.query(models.Forklift).all()
    tasks = db.query(models.Task).all()

    available = []
    engaged = []
    leave = []

    for f in forklifts:
        if f.status == "available":
            available.append({
                "id": f.id,
                "type": f.forklift_type
            })
        elif f.status == "engaged":
            engaged.append({
                "id": f.id,
                "type": f.forklift_type
            })
        elif f.status == "leave":
            leave.append({
                "id": f.id,
                "type": f.forklift_type
            })

    pending_cells = list(
        set([
            t.cell_number
            for t in tasks
            if t.status == "pending"
        ])
    )

    assigned_tasks = [
        {
            "task_id": t.id,
            "forklift": t.assigned_forklift,
            "cell": t.cell_number
        }
        for t in tasks
        if t.status == "assigned"
    ]

    return {
        "forklifts": {
            "available": available,
            "engaged": engaged,
            "leave": leave
        },
        "cells": {
            "pending": pending_cells
        },
        "tasks": {
            "assigned": assigned_tasks
        }
    }
