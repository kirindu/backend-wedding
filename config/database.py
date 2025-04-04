import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv() # Cargamos variables de entorno

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URI)
database  = client[DB_NAME]


async def ping_database():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")


trucks_collection = database.trucks
drivers_collection = database.drivers
users_collection = database.users
routes_collection = database.routes
coversheets_collection = database.coversheets