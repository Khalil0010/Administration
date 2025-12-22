from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SaveWise Transaction Service")


# Logique de catégorisation automatique simple pour le MVP
def auto_categorize(description: str):
    desc = description.lower()
    if "carrefour" in desc or "super" in desc or "achat" in desc:
        return "Alimentation"
    if "loyer" in desc or "rent" in desc:
        return "Logement"
    if "netflix" in desc or "cinéma" in desc or "spotify" in desc:
        return "Divertissement"
    if "salaire" in desc or "virement" in desc:
        return "Revenus"
    return "Divers"


@app.post("/transactions", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Application de la catégorisation automatique
    category = auto_categorize(transaction.description)

    new_transaction = models.Transaction(
        **transaction.dict(),
        category=category
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@app.get("/transactions/{user_email}")
def get_user_transactions(user_email: str, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.user_email == user_email).all()
    return transactions