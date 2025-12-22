from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SaveWise Saving Goals Service")


@app.post("/goals", response_model=schemas.SavingGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(goal: schemas.SavingGoalCreate, db: Session = Depends(get_db)):
    new_goal = models.SavingGoal(**goal.dict())
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    # Calcul de la progression initiale
    new_goal.progress_percentage = 0.0
    return new_goal


@app.patch("/goals/{goal_id}/add-savings", response_model=schemas.SavingGoalResponse)
def add_savings(goal_id: int, update: schemas.SavingGoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(models.SavingGoal).filter(models.SavingGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")

    goal.current_amount += update.amount_to_add
    db.commit()
    db.refresh(goal)

    # Calcul dynamique de la progression
    goal.progress_percentage = min((goal.current_amount / goal.target_amount) * 100, 100.0)
    return goal


@app.get("/goals/{user_email}")
def list_goals(user_email: str, db: Session = Depends(get_db)):
    goals = db.query(models.SavingGoal).filter(models.SavingGoal.user_email == user_email).all()
    for goal in goals:
        goal.progress_percentage = min((goal.current_amount / goal.target_amount) * 100, 100.0)
    return goals