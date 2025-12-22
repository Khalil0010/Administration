import os

class Settings:
    PROJECT_NAME: str = "SaveWise-Auth-Service"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_12345") # À changer en prod
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Utilisation de SQLite par défaut pour le MVP, facilement switchable vers PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./auth.db")

settings = Settings()