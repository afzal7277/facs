import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models
from app.services.assignment_engine import assign_forklift
from app.websocket.manager import manager


async def timeout_worker():

    print("\n✅ Timeout worker started successfully!\n")

    while True:
        try:
            await asyncio.sleep(30)

            db = SessionLocal()

            try:
                config = db.query(models.SystemConfig).first()
                if not config:
                    continue

                timeout_minutes = config.task_timeout_minutes

                timeout_threshold = datetime.utcnow() - timedelta(
                    minutes=timeout_minutes
                )

                expired_tasks = db.query(models.Task).filter(
                    models.Task.status == "assigned",
                    models.Task.assigned_at < timeout_threshold
                ).all()

                for task in expired_tasks:

                    old_forklift_id = task.assigned_forklift

                    forklift = db.query(models.Forklift).filter(
                        models.Forklift.id == old_forklift_id
                    ).first()

                    if forklift:
                        forklift.status = "available"

                    task.status = "pending"
                    task.assigned_forklift = None
                    task.assigned_at = None

                    db.commit()

                    # 🔥 Notify OLD forklift to clear UI
                    if old_forklift_id:
                        await manager.notify_forklift(
                            old_forklift_id,
                            {
                                "event": "task_removed",
                                "task_id": task.id
                            }
                        )

                    # 🔁 Try reassign
                    await assign_forklift(db, task)

                # 🔥 Correct call
                await manager.broadcast_live_update(db)

            finally:
                db.close()

        except asyncio.CancelledError:
            print("\n⚠️ Timeout worker cancelled\n")
            break

        except Exception as e:
            print(f"\n❌ Error in timeout_worker: {e}\n")
            await asyncio.sleep(5)