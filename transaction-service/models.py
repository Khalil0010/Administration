from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False) # Lien logique avec User/Auth
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False) # Ex: Alimentation, Loyer, Divertissement
    description = Column(String)
    type = Column(String) # "EXPENSE" ou "INCOME"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)