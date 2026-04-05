from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.database import ping_database
from config.database import client


# ── Core / Form sections ───────────────────────────────────────────────────

from routes.guess_routes import router as guess_router




@asynccontextmanager
async def lifespan(application: FastAPI):
    await ping_database()
    yield


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# ── CORS ───────────────────────────────────────────────────────────────────
origins = [
    "https://weddingapp.kizunadata.cloud",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3500",
    "http://127.0.0.1:3500",
    "http://[::1]:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response

# ── Routes ─────────────────────────────────────────────────────────────────



# Core / Form sections

app.include_router(guess_router,                    prefix="/api/guesses",             tags=["Guesses   "])

@app.get("/")
async def root():
    return {"message": "Welcome to Wedding API!"}        