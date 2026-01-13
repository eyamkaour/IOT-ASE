from http.client import HTTPException
import time
from fastapi import Form

REQUESTS = {}
MAX_REQUESTS = 10
WINDOW = 60

def rate_limiter(email: str = Form(...)):
    """Limite de requêtes pour un utilisateur par email"""
    now = time.time()
    REQUESTS.setdefault(email, [])
    REQUESTS[email] = [t for t in REQUESTS[email] if now - t < WINDOW]

    if len(REQUESTS[email]) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")

    REQUESTS[email].append(now)
    return True
def allow_request(user_id):
    now = time.time()
    REQUESTS.setdefault(user_id, [])
    REQUESTS[user_id] = [t for t in REQUESTS[user_id] if now - t < WINDOW]

    if len(REQUESTS[user_id]) >= MAX_REQUESTS:
        return False

    REQUESTS[user_id].append(now)
    return True