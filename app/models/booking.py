from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
import enum
from sqlalchemy.orm import relationship
from ..core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    CONSUMED = "CONSUMED"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    carrier_user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    driver_user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), index=True)
    terminal_id = Column(PostgresUUID(as_uuid=True), ForeignKey("terminals.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, index=True)
    decided_by_operator_user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    qr_payload = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    carrier_user = relationship("User", foreign_keys=[carrier_user_id], back_populates="bookings_as_carrier")
    driver_user = relationship("User", foreign_keys=[driver_user_id], back_populates="bookings_as_driver")
    terminal = relationship("Terminal", back_populates="bookings")
    decided_by_operator = relationship("User", foreign_keys=[decided_by_operator_user_id], back_populates="bookings_decided_by")
    notifications = relationship("Notification", back_populates="related_booking")
    anomalies = relationship("Anomaly", back_populates="booking")