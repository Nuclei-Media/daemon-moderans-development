from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

from sqlalchemy.dialects.postgresql import *


class UserQuota(Base):
    __tablename__ = "user_quota"
    id = Column(Integer, primary_key=True)
    subscription_id = Column(String, ForeignKey("subscription.id"), nullable=False)
    owner_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="user_quota")
    file_storage = Column(Integer, nullable=False)
    currently_hosted_file_count = Column(Integer, nullable=True)
    subscription = relationship("Subscription", back_populates="user_quotas")
