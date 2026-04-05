import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from colorama import Fore, Style, init

load_dotenv() # Cargamos variables de entorno

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URI)
database  = client[DB_NAME]


async def ping_database():
    try:
        await client.admin.command('ping')
        print(Fore.GREEN + "✅ Successfully connected to MongoDB on Dokploy!")
    except Exception as e:
        print(Fore.RED + f"❌ Failed to connect to MongoDB: {e}")

guess_collection = database.guesses
