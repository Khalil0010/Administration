from sqlalchemy import Column, Integer, String
from database import Base

class UserAuth(Base):
    __tablename__ = "users_auth"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)