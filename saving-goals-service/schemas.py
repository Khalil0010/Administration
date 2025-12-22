from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SavingGoalBase(BaseModel):
    user_email: str
    name: str
    target_amount: float
    deadline: Optional[datetime] = None

class SavingGoalCreate(SavingGoalBase):
    pass

class SavingGoalUpdate(BaseModel):
    amount_to_add: float

class SavingGoalResponse(SavingGoalBase):
    id: int
    current_amount: float
    progress_percentage: float # Calculé dynamiquement
    created_at: datetime
    class Config:
        from_attributes = True