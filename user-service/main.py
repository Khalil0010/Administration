from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas

# Création automatique des tables dans User DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaveWise User Service")


@app.post("/profiles", response_model=schemas.UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile: schemas.UserProfileCreate, db: Session = Depends(get_db)):
    db_profile = db.query(models.UserProfile).filter(models.UserProfile.email == profile.email).first()
    if db_profile:
        raise HTTPException(status_code=400, detail="Le profil pour cet email existe déjà.")

    new_profile = models.UserProfile(**profile.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@app.get("/profiles/{email}", response_model=schemas.UserProfileResponse)
def get_profile(email: str, db: Session = Depends(get_db)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.email == email).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé.")
    return profile


@app.put("/profiles/{email}", response_model=schemas.UserProfileResponse)
def update_profile(email: str, profile_update: schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    db_profile = db.query(models.UserProfile).filter(models.UserProfile.email == email).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé.")

    update_data = profile_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile