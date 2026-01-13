import os, time, jwt

SECRET_KEY = os.getenv("JWT_SECRET", "change_me")
ALGORITHM = "HS256"

def create_token(user_id: str, roles: list[str]) -> str:
    payload = {
        "sub": user_id,      # identité utilisateur
        "roles": roles,      # rôles (user/admin)
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
