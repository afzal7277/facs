from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Device

router = APIRouter(prefix="/devices")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register device
@router.post("/register")
def register_device(data: dict, db: Session = Depends(get_db)):

    existing = db.query(Device).filter(
        Device.device_id == data["device_id"]
    ).first()

    if existing:
        return existing

    new_device = Device(
        device_id=data["device_id"],
        mode="cell",  # default
        forklift_type=None,
        cell_number=None
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device


# Get all devices (Admin)
@router.get("/")
def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()


# Update device configuration
@router.put("/{device_id}")
def update_device(device_id: str, data: dict,
                  db: Session = Depends(get_db)):

    device = db.query(Device).filter(
        Device.device_id == device_id
    ).first()

    if not device:
        return {"error": "Device not found"}

    device.mode = data.get("mode", device.mode)
    device.forklift_type = data.get(
        "forklift_type", device.forklift_type)
    device.cell_number = data.get(
        "cell_number", device.cell_number)

    db.commit()
    db.refresh(device)

    return device

@router.get("/{device_id}")
def get_device(device_id: str,
               db: Session = Depends(get_db)):

    device = db.query(Device).filter(
        Device.device_id == device_id
    ).first()

    return device
