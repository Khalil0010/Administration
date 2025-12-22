from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    occupation: str # "Étudiant", "Jeune Actif", "Ménage"
    monthly_income: float
    currency_preference: Optional[str] = "EUR"

class UserProfileCreate(UserProfileBase):
    email: EmailStr

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    currency_preference: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True