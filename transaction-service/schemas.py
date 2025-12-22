from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    user_email: str
    amount: float
    description: str
    type: str # "EXPENSE" ou "INCOME"

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    category: str
    timestamp: datetime
    class Config:
        from_attributes = True