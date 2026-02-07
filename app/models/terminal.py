from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from ..core.database import Base


class TerminalStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class Terminal(Base):
    __tablename__ = "terminals"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    status = Column(Enum(TerminalStatus), nullable=False)
    max_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    coord_x = Column(Float, nullable=False)
    coord_y = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    operators = relationship("OperatorProfile", back_populates="terminal")
    bookings = relationship("Booking", back_populates="terminal")
    anomalies = relationship("Anomaly", back_populates="terminal")


# Add the relationship to the booking model after defining both models
def add_terminal_relationships():
    from .booking import Booking
    from .anomaly import Anomaly
    Terminal.bookings = relationship("Booking", back_populates="terminal")
    Terminal.anomalies = relationship("Anomaly", back_populates="terminal")