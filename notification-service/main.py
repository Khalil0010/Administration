from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SaveWise Notification Service")


@app.post("/notifications", response_model=schemas.NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notif: schemas.NotificationCreate, db: Session = Depends(get_db)):
    # Simule l'envoi d'une alerte (Mail/Push) et enregistre en base
    new_notif = models.Notification(**notif.dict())
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)

    # Log administratif pour la supervision (Objectif 3.2)
    print(f"[ALERTE] Envoyée à {notif.user_email} : {notif.message}")
    return new_notif


@app.get("/notifications/{user_email}")
def get_user_notifications(user_email: str, db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(models.Notification.user_email == user_email).all()