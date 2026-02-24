from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import LeaveReason
from app.schemas import LeaveReasonCreate

router = APIRouter(prefix="/leave-reasons", tags=["Leave Reasons"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_reasons(db: Session = Depends(get_db)):
    return db.query(LeaveReason).all()


@router.post("/")
def create_reason(data: LeaveReasonCreate,
                  db: Session = Depends(get_db)):

    new_reason = LeaveReason(
        reason=data.reason
    )

    db.add(new_reason)
    db.commit()
    db.refresh(new_reason)

    return new_reason


@router.put("/{reason_id}")
def update_reason(reason_id: int,
                  data: dict,
                  db: Session = Depends(get_db)):

    reason = db.query(LeaveReason).filter(
        LeaveReason.id == reason_id
    ).first()

    reason.active = data.get("active", reason.active)

    db.commit()
    db.refresh(reason)

    return reason
