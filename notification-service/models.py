from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    message = Column(String, nullable=False)
    # Type d'alerte : Budget, Épargne ou Système
    alert_type = Column(String, default="GENERAL")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)