from pydantic import BaseModel
from typing import List, Dict

class CategoryBreakdown(BaseModel):
    category: str
    amount: float

class AnalyticsReport(BaseModel):
    user_email: str
    month: str
    total_spent: float
    total_income: float
    savings_rate: float
    breakdown: List[CategoryBreakdown]