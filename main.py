from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.database import ping_database
from config.database import client


from routes.route_routes import router as route_router
from routes.truck_routes import router as truck_router
from routes.driver_routes import router as driver_router

from routes.coversheet_routes import router as coversheet_router
from routes.sparetruckinfo_routes import router as sparetruckinfo_router
from routes.downtime_routes import router as downtime_router
from routes.load_routes import router as load_router

from routes.user_routes import router as user_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    await ping_database()
    yield
    

app = FastAPI(lifespan=lifespan)

app.include_router(route_router, prefix="/api/routes", tags=["Routes"])
app.include_router(truck_router, prefix="/api/trucks", tags=["Trucks"])
app.include_router(driver_router, prefix="/api/drivers", tags=["Drivers"])

app.include_router(coversheet_router, prefix="/api/coversheets", tags=["Coversheets"])
app.include_router(sparetruckinfo_router, prefix="/api/sparetruckinfo", tags=["SpareTruckInfo"])
app.include_router(downtime_router, prefix="/api/downtime", tags=["Downtime"])
app.include_router(load_router, prefix="/api/load", tags=["Load"])

app.include_router(user_router, prefix="/api/users", tags=["Users"])



@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with MongoDB and Motor!"}