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
        print(Fore.GREEN + "✅ Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(Fore.RED + f"❌ Failed to connect to MongoDB: {e}")

depts_collection = database.depts
directions_collection = database.directions
duringTheIncidents_collection = database.duringTheIncidents
employees_collection = database.employees
employeeSignatures_collection = database.employeeSignatures
generalinformations_collection = database.generalinformations
incidentDetails_collection = database.incidentDetails
roadConditions_collection = database.roadConditions
supervisors_collection = database.supervisors
supervisorNotes_collection = database.supervisorNotes
trucks_collection = database.trucks
typeOfIncidents_collection = database.typeOfIncidents
users_collection = database.users
weatherConditions_collection = database.weatherConditions
   



