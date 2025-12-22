from sqlalchemy import Column, Integer, String, Float
from database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    # Occupation : Étudiant, Jeune Actif, ou Ménage
    occupation = Column(String)
    monthly_income = Column(Float, default=0.0)
    currency_preference = Column(String, default="EUR")