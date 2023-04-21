from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base, engine
from uuid import uuid4

# iterate through the table and print the column names

# subscriptions = relationship("Subscription", back_populates="owner")
# user_quotas = relationship("UserQuota", back_populates="owner")
# usermetadata = relationship("UserMetaData", back_populates="owner")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # permanent_store = relationship("PermanentStore", back_populates="user_relationship")

    data = relationship("DataStorage", back_populates="owner")
    # chat_rooms_owned = relationship("ChatRoom", back_populates="owner")
    # sent_messages = relationship("ChatMessage", back_populates="sender")
    # chat_rooms_joined = relationship("ChatRoomMembership", back_populates="user")
