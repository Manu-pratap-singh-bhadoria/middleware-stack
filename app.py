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
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

RATE_LIMIT = 10
WINDOW = 10

clients = {}


@app.middleware("http")
async def middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    # Rate-limit ONLY GET /ping
    if request.method == "GET" and request.url.path == "/ping":
        client_id = request.headers.get("X-Client-Id")

        if client_id is not None:
            now = time.monotonic()

            bucket = clients.setdefault(client_id, [])

            bucket[:] = [t for t in bucket if now - t < WINDOW]

            if len(bucket) >= RATE_LIMIT:
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                )
                response.headers["X-Request-ID"] = request_id
                return response

            bucket.append(now)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/ping")
async def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.state.request_id,
    }


@app.get("/")
async def root():
    return {"status": "ok"}