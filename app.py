from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

# Replace with your exam/login email
EMAIL = "your_email@example.com"

# Your assigned CORS origin
ALLOWED_ORIGIN = "https://app-t5m8rb.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMIT = 10
WINDOW = 10
clients = {}

@app.middleware("http")
async def middleware(request: Request, call_next):
    # Request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Rate limiting
    client_id = request.headers.get("X-Client-Id", "anonymous")
    now = time.time()

    if client_id not in clients:
        clients[client_id] = []

    clients[client_id] = [
        t for t in clients[client_id]
        if now - t < WINDOW
    ]

    if len(clients[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"X-Request-ID": request_id},
        )

    clients[client_id].append(now)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/ping")
async def ping(request: Request):
    return {
        "email": "24f2006760@ds.study.iitm.ac.in",
        "request_id": request.state.request_id
    }