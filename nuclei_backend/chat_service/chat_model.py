from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

from sqlalchemy.dialects.postgresql import *
from sqlalchemy.dialects.postgresql import ARRAY
import uuid


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner = relationship("User", back_populates="chat_rooms_owned")

    messages = relationship("ChatMessage", back_populates="room")
    members = relationship("ChatRoomMembership", back_populates="room")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(String, nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id"))
    sender = relationship("User", back_populates="sent_messages")
    room = relationship("ChatRoom", back_populates="messages")


class ChatRoomMembership(Base):
    __tablename__ = "chat_room_memberships"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id"), primary_key=True)
    user = relationship("User", back_populates="chat_rooms_joined")
    room = relationship("ChatRoom", back_populates="members")
