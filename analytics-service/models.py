from sqlalchemy import Column, Integer, String, Float
from database import Base

class AnalyticsHistory(Base):
    __tablename__ = "analytics_history"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    total_spent = Column(Float)
    savings_rate = Column(Float)