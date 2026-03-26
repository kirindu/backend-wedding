from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.database import ping_database
from config.database import client

# ── Catalog / Dropdown routes ──────────────────────────────────────────────
from routes.dept_routes import router as dept_router
from routes.direction_routes import router as direction_router
from routes.roadcondition_routes import router as roadcondition_router
from routes.supervisor_routes import router as supervisor_router
from routes.truck_routes import router as truck_router
from routes.typeincident_routes import router as typeincident_router
from routes.weathercondition_routes import router as weathercondition_router
from routes.safetypersonnotified_routes import router as safetypersonnotified_router
from routes.whodidyousendthepictureto_routes import router as whodidyousendthepictureto_router

# ── Auth / Users ───────────────────────────────────────────────────────────
from routes.employee_routes import router as employee_router
from routes.user_routes import router as user_router

# ── Core / Form sections ───────────────────────────────────────────────────
from routes.generalinformation_routes import router as generalinformation_router
from routes.duringtheincident_routes import router as duringtheincident_router
from routes.incidentdetail_routes import router as incidentdetail_router
from routes.employeesignature_routes import router as employeesignature_router
from routes.supervisornote_routes import router as supervisornote_router

# ── Proxy Media ──────────────────────────────────────────────────────────────────
from routes.media_routes import router as media_router


# ── Utils ──────────────────────────────────────────────────────────────────
from routes.email_routes import router as email_router




@asynccontextmanager
async def lifespan(application: FastAPI):
    await ping_database()
    yield


app = FastAPI(lifespan=lifespan)

# ── CORS ───────────────────────────────────────────────────────────────────
origins = [
    "https://www.acedisposal.com",
    "https://safetyapp.kizunadata.cloud",
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

# Utils
app.include_router(email_router,                    prefix="/api/utils",               tags=["Email"])

# Catalog / Dropdowns
app.include_router(dept_router,                     prefix="/api/depts",               tags=["Depts"])
app.include_router(direction_router,                prefix="/api/directions",          tags=["Directions"])
app.include_router(roadcondition_router,            prefix="/api/roadconditions",      tags=["Road Conditions"])
app.include_router(supervisor_router,               prefix="/api/supervisors",         tags=["Supervisors"])
app.include_router(truck_router,                    prefix="/api/trucks",              tags=["Trucks"])
app.include_router(typeincident_router,             prefix="/api/typeincidents",       tags=["Type of Incidents"])
app.include_router(weathercondition_router,         prefix="/api/weatherconditions",   tags=["Weather Conditions"])

app.include_router(safetypersonnotified_router,     prefix="/api/safetypersonsnotified", tags=["Safety Persons Notified"])
app.include_router(whodidyousendthepictureto_router,prefix="/api/whodidyousendthepictureto", tags=["Who Did You Send The Picture To"])

# Auth / Users
app.include_router(employee_router,                 prefix="/api/employees",           tags=["Employees"])
app.include_router(user_router,                     prefix="/api/users",               tags=["Users"])

# Core / Form sections
app.include_router(generalinformation_router,       prefix="/api/generalinformations", tags=["General Information"])
app.include_router(duringtheincident_router,        prefix="/api/duringtheincidents",  tags=["During The Incident"])
app.include_router(incidentdetail_router,           prefix="/api/incidentdetails",     tags=["Incident Details"])
app.include_router(employeesignature_router,        prefix="/api/employeesignatures",  tags=["Employee Signatures"])
app.include_router(supervisornote_router,           prefix="/api/supervisornotes",     tags=["Supervisor Notes"])

# Proxy Media
app.include_router(media_router,                    prefix="/api/media",               tags=["Media"])

@app.get("/")
async def root():
    return {"message": "Welcome to ACE Safety API!"}