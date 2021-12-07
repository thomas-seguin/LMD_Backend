from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import SON
import uvicorn
from decouple import config
from apps.registration import models

from config import settings
#import ipdb



from apps.registration.routers import router as registration_router

# app object
app = FastAPI()

origins = ['http://localhost:8000', 'https://localhost:3000', "https://3sz5ps.deta.dev/"]   # Will be replaced by the actual production host, need to make it an ENV variable

app.add_middleware(
  CORSMiddleware, 
  allow_origins=origins,
  allow_credentials =  True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(config('DB_URL'))
    app.mongodb = app.mongodb_client[config('DB_NAME')]
    print("------------------")
    print(app.mongodb)
    
    await add_unique_index()

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(registration_router, tags=["Registration"], prefix = "/registration_api")

# Port over all these to route folder
@app.get("/")
async def read_root():
  return {"Ping": "Pong"}

async def add_unique_index():
  await app.mongodb["drivers"].create_index([("email", 1)], unique=True)
  await app.mongodb["users"].create_index([("email", 1)], unique=True)

if __name__ == "__main__":
  uvicorn.run(
      "main:app",
      host=settings.HOST,
      reload=settings.DEBUG_MODE,
      port=settings.PORT
  )