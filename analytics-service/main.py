from fastapi import FastAPI, Depends, HTTPException
import httpx
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import AnalyticsHistory  # Correction de l'import ici

# Initialisation de la base Analytics DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaveWise Analytics Service")

# Utilisation de host.docker.internal pour atteindre le Transaction Service (Port 8002)
TRANSACTION_SERVICE_URL = "http://host.docker.internal:8002"

@app.get("/analytics/report/{user_email}")
async def get_real_report(user_email: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        try:
            # Appel au Transaction Service pour récupérer les données réelles [cite: 81]
            response = await client.get(f"{TRANSACTION_SERVICE_URL}/transactions/{user_email}")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Transactions non trouvées")
            transactions = response.json()
        except Exception:
            raise HTTPException(status_code=503, detail="Le Transaction Service est hors ligne")

    if not transactions:
        return {"message": "Aucune transaction à analyser"}

    # Calcul des statistiques (Objectif 3.1) [cite: 20, 22]
    total_spent = sum(t["amount"] for t in transactions if t["type"] == "EXPENSE")
    total_income = sum(t["amount"] for t in transactions if t["type"] == "INCOME")
    savings_rate = round(((total_income - total_spent) / total_income * 100), 2) if total_income > 0 else 0

    # Sauvegarde dans Analytics DB
    report = AnalyticsHistory(user_email=user_email, total_spent=total_spent, savings_rate=savings_rate)
    db.add(report)
    db.commit()

    return {
        "user_email": user_email,
        "total_spent": total_spent,
        "total_income": total_income,
        "savings_rate_percent": savings_rate
    }