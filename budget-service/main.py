from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SaveWise Budget Service")


@app.post("/budgets", response_model=schemas.BudgetResponse, status_code=status.HTTP_201_CREATED)
def set_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    db_budget = db.query(models.Budget).filter(
        models.Budget.user_email == budget.user_email,
        models.Budget.category == budget.category
    ).first()

    if db_budget:
        db_budget.monthly_limit = budget.monthly_limit
    else:
        db_budget = models.Budget(**budget.dict())
        db.add(db_budget)

    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.post("/budgets/check")
def check_budget(check: schemas.BudgetCheck, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(
        models.Budget.user_email == check.user_email,
        models.Budget.category == check.category
    ).first()

    if not budget:
        return {"status": "no_budget_set", "exceeded": False}

    new_total = budget.current_spent + check.amount
    exceeded = new_total > budget.monthly_limit

    # Mise à jour fictive pour le MVP
    if not exceeded:
        budget.current_spent = new_total
        db.commit()

    return {
        "category": budget.category,
        "limit": budget.monthly_limit,
        "new_total": new_total,
        "exceeded": exceeded,
        "alert": "Budget dépassé !" if exceeded else "OK"  # Base pour le Notification Service
    }


@app.get("/budgets/{user_email}")
def get_budgets(user_email: str, db: Session = Depends(get_db)):
    return db.query(models.Budget).filter(models.Budget.user_email == user_email).all()