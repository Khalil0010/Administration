from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas, auth_utils

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SaveWise Auth Service")


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserAuth).filter(models.UserAuth.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà enregistré.")

    new_user = models.UserAuth(
        email=user.email,
        hashed_password=auth_utils.get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "Utilisateur créé avec succès"}


@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # 3. Validate Credentials [cite: 96]
    user = db.query(models.UserAuth).filter(models.UserAuth.email == user_credentials.email).first()
    if not user or not auth_utils.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants incorrects")

    # 5. Generate JWT Token [cite: 98]
    access_token = auth_utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/verify-token")
def verify_token(token: str):
    try:
        payload = auth_utils.jwt.decode(token, auth_utils.settings.SECRET_KEY,
                                        algorithms=[auth_utils.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"email": email, "status": "active"}
    except auth_utils.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")