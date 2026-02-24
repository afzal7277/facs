from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import tasks, forklifts, cells
from app.database import engine
from app import models
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.manager import manager, generate_live_overview
from app.routes import admin, auth, device, forklift_type, leave_reason, cells
from app.services.timeout_engine import timeout_worker
import asyncio
from app.database import SessionLocal
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("\n" + "="*50)
    print("🚀 FACS BACKEND STARTING")
    print("="*50 + "\n")
    
    print("Starting timeout worker...")
    timeout_task = asyncio.create_task(timeout_worker())
    print("✅ Timeout worker task created\n")
    
    yield
    
    # Shutdown code
    print("\n" + "="*50)
    print("🛑 FACS BACKEND SHUTTING DOWN")
    print("="*50 + "\n")
    
    timeout_task.cancel()
    try:
        await timeout_task
    except asyncio.CancelledError:
        print("✅ Timeout worker cancelled gracefully\n")


app = FastAPI(title="FACS - Forklift Automation Call System", lifespan=lifespan)
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(forklifts.router, prefix="/forklifts", tags=["Forklifts"])
app.include_router(cells.router)
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(device.router)
app.include_router(forklift_type.router)
app.include_router(leave_reason.router)



@app.get("/")
def root():
    return {"message": "FACS Backend Running 🚜"}


async def _keepalive(websocket: WebSocket, interval: int = 60):
    """Send a lightweight ping message at regular intervals to keep the
    connection active (helps when proxies or load‑balancers drop idle
    sockets).
    """
    try:
        while True:
            await asyncio.sleep(interval)
            await websocket.send_json({"event": "ping"})
    except Exception:
        # connection probably closed
        return
    
@app.websocket("/ws/forklift/{forklift_id}")
async def forklift_ws(websocket: WebSocket, forklift_id: int):
    await manager.connect_forklift(websocket, forklift_id)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)

# @app.websocket("/ws/forklift/{forklift_id}")
# async def forklift_websocket(websocket: WebSocket, forklift_id: int):
#     # Get forklift type from database
#     db = SessionLocal()
#     forklift = db.query(models.Forklift).filter(models.Forklift.id == forklift_id).first()
#     db.close()
    
#     if not forklift:
#         await websocket.close(code=1008, reason="Forklift not found")
#         return
    
#     await manager.connect_forklift(websocket, forklift.forklift_type)

#     data = generate_live_overview(SessionLocal())
#     await websocket.send_json(data)

#     # if there are tasks already assigned to this forklift, notify it
#     db2 = SessionLocal()
#     assigned = db2.query(models.Task).filter(
#         models.Task.assigned_forklift == forklift_id,
#         models.Task.status == "assigned"
#     ).all()
#     for t in assigned:
#         await websocket.send_json({
#             "event": "task_assigned",
#             "task_id": t.id,
#             "cell_number": t.cell_number,
#             "assigned_forklift": t.assigned_forklift
#         })
#     db2.close()

#     # start keepalive pings
#     ping_task = asyncio.create_task(_keepalive(websocket))

#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#     finally:
#         ping_task.cancel()



@app.websocket("/ws/cell/{cell_number}")
async def cell_websocket(websocket: WebSocket, cell_number: str):
    await manager.connect_cell(websocket, cell_number)
    
    # SEND INITIAL DATA - pending tasks for this cell
    db = SessionLocal()
    pending_tasks = db.query(models.Task).filter(
        models.Task.cell_number == cell_number,
        models.Task.status == "pending"
    ).all()
    db.close()
    
    await websocket.send_json({
        "event": "pending_tasks",
        "cell_number": cell_number,
        "tasks": [
            {
                "task_id": t.id,
                "forklift_type": t.forklift_type,
                "status": t.status
            }
            for t in pending_tasks
        ]
    })

    ping_task = asyncio.create_task(_keepalive(websocket))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        ping_task.cancel()


@app.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    await manager.connect_admin(websocket)

    # SEND INITIAL DATA
    db = SessionLocal()
    data = generate_live_overview(db)
    await websocket.send_json(data)

    ping_task = asyncio.create_task(_keepalive(websocket))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        ping_task.cancel()
