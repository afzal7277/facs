from datetime import datetime
from app.websocket.manager import manager
from app import models


async def assign_forklift(db, task):

    print("TASK TYPE:", task.forklift_type)

    forklifts = db.query(models.Forklift).all()
    for f in forklifts:
        print("FORKLIFT:", f.id, f.forklift_type, f.status)

    
    available_forklift = db.query(models.Forklift).filter(
        models.Forklift.forklift_type.ilike(task.forklift_type.strip()),
        models.Forklift.status == "available"
    ).first()
    

    # available_forklift = db.query(models.Forklift).filter(
    #     models.Forklift.forklift_type == task.forklift_type,
    #     models.Forklift.status == "available"
    # ).first()

    if not available_forklift:
        return task

    # 🔹 Assign task
    task.status = "assigned"
    task.assigned_forklift = available_forklift.id
    task.assigned_at = datetime.utcnow()

    available_forklift.status = "engaged"

    db.commit()

    # 🔥 Notify ONLY assigned forklift
    await manager.notify_forklift(
        available_forklift.id,
        {
            "event": "new_task",
            "task_id": task.id,
            "cell_number": task.cell_number
        }
    )

    # 🔹 Notify specific cell
    await manager.notify_cell(
        task.cell_number,
        {
            "event": "task_assigned",
            "task_id": task.id,
            "assigned_forklift": task.assigned_forklift
        }
    )

    # 🔹 Notify admin
    await manager.broadcast_to_admin(
        {
            "event": "task_update",
            "task_id": task.id,
            "status": task.status
        }
    )

    return task
