from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
import enum
from sqlalchemy.orm import relationship
from ..core.database import Base


class AnomalySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    severity = Column(Enum(AnomalySeverity), nullable=False)
    message = Column(Text, nullable=False)
    terminal_id = Column(PostgresUUID(as_uuid=True), ForeignKey("terminals.id"))
    booking_id = Column(PostgresUUID(as_uuid=True), ForeignKey("bookings.id"))
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    terminal = relationship("Terminal", back_populates="anomalies")
    booking = relationship("Booking", back_populates="anomalies")