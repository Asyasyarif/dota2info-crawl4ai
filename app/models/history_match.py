from sqlalchemy import Column, UUID, ForeignKey, DateTime, String
from app.database.database import Base
from app.ai.uuid_helpers import uuid7
from datetime import datetime
from sqlalchemy.orm import relationship


class HistoryMatch(Base):
    __tablename__ = "history_match"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    match_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("Users", back_populates="history_match")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "match_id": str(self.match_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
