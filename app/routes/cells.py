from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from sqlalchemy import Boolean

router = APIRouter(prefix="/cells", tags=["Cells"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create Cell
@router.post("/", response_model=schemas.CellResponse)
def create_cell(cell: schemas.CellCreate,
                db: Session = Depends(get_db)):

    new_cell = models.Cell(
        cell_number=cell.cell_number,
        operator_name=cell.operator_name,
        active=True
    )

    db.add(new_cell)
    db.commit()
    db.refresh(new_cell)

    return new_cell


# Get All Active Cells
@router.get("/")
def get_all_cells(db: Session = Depends(get_db)):
    return db.query(models.Cell).filter(
        models.Cell.active == True
    ).all()



# Activate / Deactivate Cell
@router.put("/{cell_id}")
def update_cell(cell_id: int,
                data: dict,
                db: Session = Depends(get_db)):

    cell = db.query(models.Cell).filter(
        models.Cell.id == cell_id
    ).first()

    if not cell:
        return {"error": "Cell not found"}

    cell.active = data.get("active", cell.active)

    db.commit()
    db.refresh(cell)

    return cell
