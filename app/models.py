from sqlalchemy import Column, Integer, String, DateTime, ForeignKey , Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))
    role = Column(String(20))  # admin / forklift


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    task_timeout_minutes = Column(Integer, default=5)


class Forklift(Base):
    __tablename__ = "forklifts"

    id = Column(Integer, primary_key=True, index=True)
    forklift_type = Column(String(50), nullable=False)
    status = Column(String(50), default="available")  # available, engaged, leave
    leave_comment = Column(String(255), nullable=True)
    device_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Cell(Base):
    __tablename__ = "cells"

    id = Column(Integer, primary_key=True, index=True)
    cell_number = Column(String(50), unique=True, nullable=False)
    operator_name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    forklift_type = Column(String(50), nullable=False)
    cell_number = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")  # pending, assigned, completed
    assigned_forklift = Column(Integer, ForeignKey("forklifts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    forklift = relationship("Forklift")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True)
    mode = Column(String(20))  # "cell" or "forklift"
    forklift_type = Column(String(50), nullable=True)
    cell_number = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)

class ForkliftType(Base):
    __tablename__ = "forklift_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    active = Column(Boolean, default=True)

class LeaveReason(Base):
    __tablename__ = "leave_reasons"

    id = Column(Integer, primary_key=True, index=True)
    reason = Column(String(100), unique=True)
    active = Column(Boolean, default=True)


