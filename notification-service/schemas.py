from pydantic import BaseModel, EmailStr
from datetime import datetime

class NotificationCreate(BaseModel):
    user_email: EmailStr
    message: str
    alert_type: str = "GENERAL"

class NotificationResponse(BaseModel):
    id: int
    user_email: EmailStr
    message: str
    alert_type: str
    timestamp: datetime
    class Config:
        from_attributes = True