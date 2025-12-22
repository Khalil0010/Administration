from pydantic import BaseModel

class BudgetBase(BaseModel):
    user_email: str
    category: str
    monthly_limit: float

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    current_spent: float
    class Config:
        from_attributes = True

class BudgetCheck(BaseModel):
    user_email: str
    category: str
    amount: float