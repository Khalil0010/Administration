from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class SavingGoal(Base):
    __tablename__ = "saving_goals"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False) # Ex: "Nouvel Ordinateur"
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)