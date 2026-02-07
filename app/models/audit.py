from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from ..core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(PostgresUUID(as_uuid=True))
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    actor_user = relationship("User", back_populates="audit_logs")