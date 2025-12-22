from sqlalchemy import Column, Integer, String, Float
from database import Base

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False) # Ex: Alimentation, Divertissement
    monthly_limit = Column(Float, nullable=False)
    current_spent = Column(Float, default=0.0)