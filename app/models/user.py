from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from ..core.database import Base


class UserRole(Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    CARRIER = "CARRIER"
    DRIVER = "DRIVER"


class User(Base):
    __tablename__ = "users"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    operator_profile = relationship("OperatorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    carrier_profile = relationship("CarrierProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    driver_profile = relationship("DriverProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    bookings_as_carrier = relationship("Booking", foreign_keys='Booking.carrier_user_id', back_populates="carrier_user")
    bookings_as_driver = relationship("Booking", foreign_keys='Booking.driver_user_id', back_populates="driver_user")
    bookings_decided_by = relationship("Booking", foreign_keys='Booking.decided_by_operator_user_id', back_populates="decided_by_operator")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor_user")
    chat_sessions = relationship("ChatSession", back_populates="user")