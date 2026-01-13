from email.header import Header
import ssl


import logging
import sys
from urllib.request import Request
from colorlog import ColoredFormatter
from typing import Union
from dotenv import load_dotenv  # ← AJOUTER CETTE LIGNE
from fastapi import FastAPI ,Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import os
from security.rate_limit import rate_limiter
from routers import router 
# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.login import router as login_router

from security.jwt_auth import verify_token
from security.rbac import is_allowed
from security.request_guard import is_request_safe
from security.rate_limit import allow_request
from graph import runnable
from auth.signup import router as signup_router
from auth.login import router as login_router
from security.rbac import require_role
from security.jwt_auth import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
print("MONGO:", MONGO_URI)

print("MONGO_URL:", MONGO_URI)
# Reset the logging configuration to ensure only the new settings apply
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

handler = logging.StreamHandler()
# Configure logging to show only INFO level and higher
handler.setFormatter(ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(message)s'))
logging.basicConfig(level=logging.INFO)
# logging.disable()
app = FastAPI()
#  This part achive secure connection to your server need to be done latw
# https://medium.com/@mariovanrooij/adding-https-to-fastapi-ad5e0f9e084e#:~:text=To%20use%20HTTPS%2C%20simply%20change,.com%2Fapi%2Fendpoint%20.
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('cert.pem', keyfile='key.pem')
origins = ["*"]
# for security purpose, you might need to define certain IPs that can request a service
# origins = ["http://localhost",
#     "http://localhost:37889"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the logging module
# Configure the logging settings
    # logging.getLogger().handlers = []  # Remove any existing handlers
    # handler = logging.StreamHandler()
    # handler.setFormatter(ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(message)s'))
    # logging.getLogger().addHandler(handler)
# Configure logging to show only INFO level and higher

#turn off debugger
# logging.disable()
# class Item(BaseModel):
#     title: str
#     price: float
#     is_offer: Union[bool, None] = None

class Item(BaseModel):
    title: str
    id: int
    userId:int

class Query(BaseModel):
    text:str
    threadId:str
class QueryResponse(BaseModel):
    """Modèle de réponse"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
# ===== MODÈLES PYDANTIC =====
class QueryRequest(BaseModel):
    """Modèle de requête"""
    query: str
    thread_id: Optional[str] = "default"
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "I want to rent a car in Paris",
                "thread_id": "test-001"
            }
        }
app.include_router(login_router, prefix="/auth")
app.include_router(signup_router, prefix="/auth")
@app.post("/agent_query")
def agent_query(text: str, threadId: str, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token manquant")

    token = authorization.replace("Bearer ", "")
    # Tu dois extraire le rôle du payload JWT ici
    result = sec_agent.route_agent(token, text, requested_agent="SEARCH")
    return {"result": result}
@router.get("/secure-data")
def secure_data(user=Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user": user["email"]
    }
@router.get("/admin")
def admin_panel(
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return {"msg": "Admin access"}
@app.get("/")
def read_root():
    return {"title": "World",  "userId": 1, "id": 1}

@app.get("/iot/data")
async def get_data(request: Request):
    token = request.headers.get("Authorization").split(" ")[1]
    claims = verify_token(token)
    roles = claims.get("roles", [])
    
    if not is_allowed(roles, "iot:data", "read"):
        return {"error": "Accès interdit"}
    
    return {"data": "Voici les données IoT sécurisées"}
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    print(item.title)
    return item
    return {"item_name": item.title, "item_id": item_id}

@app.put("/query")
def query_handler(query: Query):
    print(query)
    thread = {"configurable": {"thread_id": query.threadId}}


    human_message = HumanMessage(content=query.text)
    messages = [human_message]

    result = runnable.invoke({"messages":messages}, thread)
    print(result["response"][-1])

    return  {"answer": result["response"][-1]}
    return {"item_name": item.title, "item_id": item_id}
# Ajouter cette route POST
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Traiter une requête"""
    if not runnable:
        raise HTTPException(503, "Graph non chargé")
    
    try:
        result = runnable.invoke(
            {"messages": [{"role": "user", "content": request.query}]},
            {"configurable": {"thread_id": request.thread_id}}
        )
        return QueryResponse(success=True, result=result)
    except Exception as e:
        return QueryResponse(success=False, error=str(e))


def printResults(results):
    services_name_addresses=[]
    for result in results:
        logging.info(result['Service Address'])
        logging.info(result['Service Name'])
        logging.info(result['location']['coordinates'])
        services_name_addresses.append([result['Service Name'],result['Service Address']])
    return services_name_addresses
@app.post("/agent")
async def agent_endpoint(request: Request, query: str):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Token missing")

    token = auth.split(" ")[1]
    claims = verify_token(token)

    user = claims["sub"]
    roles = claims["roles"]

    if not allow_request(user):
        raise HTTPException(429, "Too many requests")

    if not is_allowed(roles, "agent", "use"):
        raise HTTPException(403, "Access denied")

    if not is_request_safe(query):
        raise HTTPException(400, "Malicious request detected")

    return {"response": f"Agent response for: {query}"}

# while True:
        
#     user_query = input("Enter your query: ")
#     refined_user_query=user_query
#     # refined_user_query = query_refining_func(query=user_query)

#     # query_type = query_type_func(query=refined_user_query)
#     services_types, entities, addresses = query_understanding_engine(
#         query=refined_user_query)

#     # print("Query type: " + query_type)
#     print("Services types (top 3 in semantic meaning): " + str(services_types))
#     print("Entities mentioned: " + str(entities))
#     print("Addresses: " + str(addresses))