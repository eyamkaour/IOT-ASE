from fastapi import APIRouter, HTTPException
from auth.storage import USERS
from auth.company_service import get_or_create_company
from security.email_check import is_email_safe
from src.security.email_check import is_email_safe
router = APIRouter()

@router.post("/signup")
def signup(email: str, password: str, company_name: str):
    if not is_email_safe(email):
        raise HTTPException(400, "Suspicious email")

    if email in USERS:
        raise HTTPException(400, "User already exists")

    company_id = get_or_create_company(company_name)

    USERS[email] = {
        "password": password,   # hash en vrai projet
        "role": "admin",        # premier user = admin
        "company_id": company_id
    }

    return {"message": "Account created", "company_id": company_id}
