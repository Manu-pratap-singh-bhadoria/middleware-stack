from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

EMAIL = "24f2006760@ds.study.iitm.ac.in"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-t5m8rb.example.com",
        "https://exam.sanand.workers.dev",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],  # Important for browser access
)

RATE_LIMIT = 10
WINDOW = 10  # seconds

clients = {}


@app.middleware("http")
async def request_context_and_rate_limit(request: Request, call_next):
    # Request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    # Client ID for rate limiting
    client_id = request.headers.get("X-Client-Id", "anonymous")
    now = time.time()

    if client_id not in clients:
        clients[client_id] = []

    # Keep only requests within the last WINDOW seconds
    clients[client_id] = [
        t for t in clients[client_id]
        if now - t < WINDOW
    ]

    # Rate limit: max 10 requests per 10 seconds
    if len(clients[client_id]) >= RATE_LIMIT:
        response = JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )
        response.headers["X-Request-ID"] = request_id
        return response

    clients[client_id].append(now)

    response = await call_next(request)

    # Echo request ID in every response
    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/ping")
async def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }


@app.get("/")
async def root():
    return {
        "status": "ok"
    }