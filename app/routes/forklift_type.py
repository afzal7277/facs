from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ForkliftType
from app.schemas import ForkliftTypeCreate


router = APIRouter(prefix="/forklift-types", tags=["Forklift Types"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get All Active types
@router.get("/")
def get_types(db: Session = Depends(get_db)):
    return db.query(ForkliftType).filter(
        ForkliftType.active == True
    ).all()



# Create new type

@router.post("/")
def create_type(data: ForkliftTypeCreate,
                db: Session = Depends(get_db)):

    new_type = ForkliftType(
        name=data.name
    )

    db.add(new_type)
    db.commit()
    db.refresh(new_type)

    return new_type



# Activate / Deactivate type
@router.put("/{type_id}")
def update_type(type_id: int, data: dict,
                db: Session = Depends(get_db)):

    type_obj = db.query(ForkliftType).filter(
        ForkliftType.id == type_id
    ).first()

    if not type_obj:
        return {"error": "Type not found"}

    type_obj.active = data.get(
        "active", type_obj.active)

    db.commit()
    db.refresh(type_obj)

    return type_obj
