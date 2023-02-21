from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

from sqlalchemy.dialects.postgresql import *


class Subscription(Base):
    __tablename__ = "subscription"
    id = Column(String, primary_key=True)
    stripe_plan_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    interval = Column(String, nullable=False)
    owner_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="subscriptions")
    user_quotas = relationship("UserQuota", back_populates="subscription")
