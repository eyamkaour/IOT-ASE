
from fastapi import APIRouter, HTTPException , Depends  ,Form
from security.jwt_auth import create_token
from security.email_check import is_email_safe
from security.rate_limit import rate_limiter

router = APIRouter()

# Simulation base utilisateurs (pour demo)
USERS_DB = {
    "user@test.com": {
        "password": "1234",  # DEMO ONLY
        "role": "user"
    },
    "admin@test.com": {
        "password": "admin",
        "role": "admin"
    }
}

@router.post("/login" , dependencies=[Depends(rate_limiter)])
def login(email: str = Form(...), password: str = Form(...)):
    # 1. Vérification email
    if not is_email_safe(email):
        raise HTTPException(status_code=400, detail="Suspicious email detected")

    user = USERS_DB.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Création token JWT
    token = create_token(email, [user["role"]])

    return {"access_token": token}
