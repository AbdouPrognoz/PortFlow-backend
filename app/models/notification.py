from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
import enum
from sqlalchemy.orm import relationship
from ..core.database import Base


class NotificationType(str, enum.Enum):
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    QR_READY = "QR_READY"
    GENERIC = "GENERIC"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    related_booking_id = Column(PostgresUUID(as_uuid=True), ForeignKey("bookings.id"))
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="notifications")
    related_booking = relationship("Booking", back_populates="notifications")