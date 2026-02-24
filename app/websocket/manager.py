import asyncio
from typing import List, Dict
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app import models
from datetime import date
from sqlalchemy import func


class ConnectionManager:
    def __init__(self):
        # forklift websocket -> forklift_type
        self.forklift_connections: Dict[WebSocket, str] = {}
        
        # cell websocket -> cell_number
        self.cell_connections: Dict[WebSocket, str] = {}
        
        # admin websockets
        self.admin_connections: List[WebSocket] = []

    # 🔹 Forklift Connect
    async def connect_forklift(self, websocket: WebSocket, forklift_id: int):
        await websocket.accept()
        self.forklift_connections[forklift_id] = websocket
        print(f"🔌 Forklift {forklift_id} connected")
        print("Current connections:", self.forklift_connections.keys())
        

    # 🔹 Cell Connect
    async def connect_cell(self, websocket: WebSocket, cell_number: str):
        await websocket.accept()
        self.cell_connections[websocket] = cell_number

    # 🔹 Admin Connect
    async def connect_admin(self, websocket: WebSocket):
        await websocket.accept()
        self.admin_connections.append(websocket)

    # 🔹 Disconnect
    def disconnect(self, websocket: WebSocket):
        if websocket in self.forklift_connections:
            del self.forklift_connections[websocket]

        if websocket in self.cell_connections:
            del self.cell_connections[websocket]

        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    # 🔹 Send to matching forklift type
    async def broadcast_to_type(self, forklift_type: str, message: dict):
        for connection, f_type in self.forklift_connections.items():
            if f_type == forklift_type:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to forklift: {e}")
                
    # 🔹 Send to specific forklift
    async def notify_forklift(self, forklift_id: int, message: dict):
        websocket = self.forklift_connections.get(forklift_id)
        if websocket:
            await websocket.send_json(message)
        print("Trying to notify forklift:", forklift_id)
        print("Current connections:", self.forklift_connections.keys())

    # 🔹 Send to specific cell
    async def notify_cell(self, cell_number: str, message: dict):
        for connection, c_number in self.cell_connections.items():
            if c_number == cell_number:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to cell: {e}")

    # 🔹 Send to all admins
    async def broadcast_to_admin(self, message: dict):
        for connection in self.admin_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to admin: {e}")

    # 🔹 General broadcast (for live updates)
    async def broadcast(self, data: dict):
        for connection in self.admin_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"Error broadcasting: {e}")

    # 🔹 Broadcast full live overview to all admins
    async def broadcast_live_update(self, db: Session):
        data = generate_live_overview(db)
        await self.broadcast_to_admin(data)



def generate_live_overview(db: Session):

    forklifts = db.query(models.Forklift).all()
    tasks = db.query(models.Task).all()

    available = []
    engaged = []
    leave = []

    for f in forklifts:
        if f.status == "available":
            available.append({"id": f.id, "type": f.forklift_type})
        elif f.status == "engaged":
            engaged.append({"id": f.id, "type": f.forklift_type})
        elif f.status == "leave":
            leave.append({"id": f.id, "type": f.forklift_type})

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





manager = ConnectionManager()




