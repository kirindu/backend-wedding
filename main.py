from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.database import ping_database
from config.database import client

from routes.user_routes import router as user_router
from routes.driver_routes import router as driver_router
# from routes.route_routes import router as route_router
from routes.truck_routes import router as truck_router
# from routes.coversheet_routes import router as coversheet_router

@asynccontextmanager
async def lifespan(application: FastAPI):
    await ping_database()
    yield
    

app = FastAPI(lifespan=lifespan)

app.include_router(driver_router, prefix="/drivers", tags=["Drivers"])
app.include_router(user_router, prefix="/users", tags=["Users"])
# app.include_router(route_router, prefix="/routes", tags=["Routes"])
app.include_router(truck_router, prefix="/trucks", tags=["Trucks"])
# app.include_router(coversheet_router, prefix="/coversheets", tags=["Coversheets"])



@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with MongoDB and Motor!"}