from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from fastapi import HTTPException
from app.services.assignment_engine import assign_forklift
from app.websocket.manager import manager


router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=schemas.ForkliftResponse)
def register_forklift(forklift: schemas.ForkliftCreate, db: Session = Depends(get_db)):

    new_forklift = models.Forklift(
        forklift_type=forklift.forklift_type,
        device_id=forklift.device_id,
        status="available"
    )

    db.add(new_forklift)
    db.commit()
    db.refresh(new_forklift)

    return new_forklift


@router.get("/")
def get_all_forklifts(db: Session = Depends(get_db)):
    forklifts = db.query(models.Forklift).all()
    return forklifts

@router.get("/by-device/{device_id}")
def get_forklift_by_device(device_id: str, db: Session = Depends(get_db)):

    forklift = db.query(models.Forklift).filter(
        models.Forklift.device_id == device_id
    ).first()

    if not forklift:
        return {"error": "Forklift not found"}

    return forklift

@router.put("/status/{forklift_id}")
async def update_status(
    forklift_id: int,
    status: str,
    leave_comment: str | None = None,
    db: Session = Depends(get_db)
):
    forklift = db.query(models.Forklift).filter(
        models.Forklift.id == forklift_id
    ).first()

    if not forklift:
        return {"error": "Forklift not found"}

    # 🔥 BLOCK break while engaged
    if forklift.status == "engaged" and status == "leave":
        return {"error": "Cannot go on break while engaged"}

    # 🔥 BLOCK available if task still assigned
    active_task = db.query(models.Task).filter(
        models.Task.assigned_forklift == forklift.id,
        models.Task.status == "assigned"
    ).first()

    if active_task and status == "available":
        return {"error": "Complete task before setting available"}

    forklift.status = status

    if status == "leave":
        forklift.leave_comment = leave_comment
    else:
        forklift.leave_comment = None

    db.commit()

    await manager.broadcast_live_update(db)

    return {"message": "Status updated"}


# @router.put("/status/{forklift_id}")
# async def update_status(
#     forklift_id: int,
#     status: str,
#     leave_comment: str | None = None,
#     db: Session = Depends(get_db)
# ):
#     forklift = db.query(models.Forklift).filter(
#         models.Forklift.id == forklift_id
#     ).first()

#     if not forklift:
#         return {"error": "Forklift not found"}

#     # 🔥 BLOCK break if currently engaged
#     if forklift.status == "engaged" and status == "leave":
#         return {
#             "error": "Cannot go on break while engaged"
#         }

#     forklift.status = status

#     if status == "leave":
#         forklift.leave_comment = leave_comment
#     else:
#         forklift.leave_comment = None

#     db.commit()

#     await broadcast_live_update(db)

#     return {"message": "Status updated"}



# @router.put("/status/{forklift_id}")
# async def update_status(
#     forklift_id: int,
#     status: str,
#     leave_comment: str = None,
#     db: Session = Depends(get_db)
# ):

#     forklift = db.query(models.Forklift).filter(
#         models.Forklift.id == forklift_id
#     ).first()

#     if not forklift:
#         return {"error": "Forklift not found"}

#     forklift.status = status
#     forklift.leave_comment = leave_comment

#     # 🔥 IF forklift goes leave while having active task
#     if status == "leave":

#         active_task = db.query(models.Task).filter(
#             models.Task.assigned_forklift == forklift_id,
#             models.Task.status == "assigned"
#         ).first()

#         if active_task:

#             # Reset task
#             active_task.status = "pending"
#             active_task.assigned_forklift = None

#             db.commit()

#             # 🔥 Re-run assignment
#             from app.services.assignment_engine import assign_forklift
#             await assign_forklift(db, active_task)

#     db.commit()

#     # Broadcast to admin dashboard

#     await manager.broadcast_to_admin({
#         "event": "refresh_dashboard"})

#     return {"message": "Status updated"}
