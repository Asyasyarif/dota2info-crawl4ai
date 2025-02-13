from sqlalchemy import Column, String, Boolean, DateTime, Integer
from app.database.database import Base
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.ai.uuid_helpers import uuid7

class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name = Column(String(255), nullable=False)
    email = Column(String, nullable=True, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_activated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    steamid = Column(String, nullable=True, unique=True)
    communityvisibilitystate = Column(Integer)
    profilestate = Column(Integer)
    personaname = Column(String(255))
    commentpermission = Column(Integer)
    profileurl = Column(String)
    avatar = Column(String)
    avatarmedium = Column(String)
    avatarfull = Column(String)
    avatarhash = Column(String)
    lastlogoff = Column(Integer)
    personastate = Column(Integer)
    realname = Column(String(255))
    primaryclanid = Column(String)
    timecreated = Column(Integer)
    personastateflags = Column(Integer)
    loccountrycode = Column(String(2))
    locstatecode = Column(String(2))
    loccityid = Column(Integer)
    
    history_match = relationship("HistoryMatch", back_populates="user")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_activated": self.is_activated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "steamid": self.steamid,
            "communityvisibilitystate": self.communityvisibilitystate,
            "profilestate": self.profilestate,
            "personaname": self.personaname,
            "commentpermission": self.commentpermission,
            "profileurl": self.profileurl,
            "avatar": self.avatar,
            "avatarmedium": self.avatarmedium,
            "avatarfull": self.avatarfull,
            "avatarhash": self.avatarhash,
            "lastlogoff": self.lastlogoff,
            "personastate": self.personastate,
            "realname": self.realname,
            "primaryclanid": self.primaryclanid,
            "timecreated": self.timecreated,
            "personastateflags": self.personastateflags,
            "loccountrycode": self.loccountrycode,
            "locstatecode": self.locstatecode,
            "loccityid": self.loccityid
        }