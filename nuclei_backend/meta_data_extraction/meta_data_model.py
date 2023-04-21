from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

from sqlalchemy.dialects.postgresql import *


class UserMetaData(Base):
    __tablename__ = "user_meta_data"
    id = Column(Integer, primary_key=True)
    user_quota_id = Column(Integer, ForeignKey("user_quota.id"), nullable=False)
    owner = relationship("User", back_populates="user_meta_data")
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    user_quota = relationship("UserQuota", back_populates="user_meta_data")
