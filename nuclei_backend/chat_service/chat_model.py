from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

from sqlalchemy.dialects.postgresql import *
from sqlalchemy.dialects.postgresql import ARRAY
import uuid


class ChatRooms(Base):
    __tablename__ = "chat_rooms"

    room_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    room_name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner = relationship("User", back_populates="chat_rooms")
    members = Column(ARRAY(String))


# class ChatMessagesRecords(Base):
#     ...
