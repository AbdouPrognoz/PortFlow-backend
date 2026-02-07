from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Float, Enum, ForeignKey, UUID, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from ..core.database import Base
from .user import UserRole


class CarrierStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class DriverStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class OperatorProfile(Base):
    __tablename__ = "operator_profiles"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    gender = Column(String(20))
    birth_date = Column(Date)
    terminal_id = Column(PostgresUUID(as_uuid=True), ForeignKey("terminals.id"))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="operator_profile")
    terminal = relationship("Terminal", back_populates="operators")


class CarrierProfile(Base):
    __tablename__ = "carrier_profiles"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    gender = Column(String(20))
    birth_date = Column(Date)
    company_name = Column(String(255))
    status = Column(Enum(CarrierStatus), nullable=False)
    proof_document_url = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="carrier_profile")
    drivers = relationship("DriverProfile", back_populates="carrier_user")


class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    carrier_user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    gender = Column(String(20))
    birth_date = Column(Date)
    truck_number = Column(String(50))
    truck_plate = Column(String(50))
    driving_license_url = Column(Text)
    status = Column(Enum(DriverStatus), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="driver_profile")
    carrier_user = relationship("User", foreign_keys=[carrier_user_id], back_populates="drivers")