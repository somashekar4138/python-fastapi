from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
import logging
from pydantic import BaseModel
from typing import Optional
import bcrypt 


# Initialize Prisma client
prisma = Prisma()

app = FastAPI(
    title="service name",
    version="0.0.1",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/swagger.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateClientDto(BaseModel):
    email: str
    name: str
    password: str
    
class UserLoginDto(BaseModel):
    email: str
    password: str
    
@app.on_event("startup")
def startup():
    logging.info("Connecting to the database...")
    prisma.connect()

@app.on_event("shutdown")
def shutdown():
    logging.info("Disconnecting from the database...")
    prisma.disconnect()

@app.get("/")
async def root():
    db = Prisma()
    db.connect()

    posts = db.user.find_many()

    db.disconnect()

    return posts

@app.post("/users")
def create_user(dto: CreateClientDto):
    try:
        password= bcrypt.hashpw(dto.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = prisma.user.create(
            data={
                "email": dto.email,
                "name": dto.name,
                "password": password
            }
        )
        return user
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/login")
def login(dto: UserLoginDto):
    try:
        user = prisma.user.find_unique(where={"email": dto.email})
        if bcrypt.checkpw(dto.password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")