from pydantic import BaseModel
from typing import Optional



class UserLogin(BaseModel):
    username: str
    password: str


class ForkliftCreate(BaseModel):
    forklift_type: str
    device_id: str


class ForkliftResponse(BaseModel):
    id: int
    forklift_type: str
    status: str
    leave_comment: Optional[str]

    class Config:
        orm_mode = True

class CellCreate(BaseModel):
    cell_number: str
    operator_name: str


class CellResponse(BaseModel):
    id: int
    cell_number: str
    operator_name: str

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    forklift_type: str
    cell_number: str


class TaskResponse(BaseModel):
    id: int
    forklift_type: str
    cell_number: str
    status: str
    assigned_forklift: int | None

    class Config:
        orm_mode = True


class ForkliftTypeCreate(BaseModel):
    name: str


class LeaveReasonCreate(BaseModel):
    reason: str
