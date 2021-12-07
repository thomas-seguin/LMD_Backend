from typing import Optional
from fastapi import APIRouter, Body, Request, HTTPException, status, Depends, Security
from fastapi.security import (
  OAuth2PasswordBearer, 
  OAuth2PasswordRequestForm,
  SecurityScopes,
)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import pymongo
import bcrypt
import jwt
from decouple import config
from datetime import datetime, timedelta


# Only needed for dev debugging
# import ipdb

from .helper import cleanNullValues
from .models import Driver, UpdateDriver, User, UpdateUser, Token, TokenData

router = APIRouter()
# users_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/registration_api/users/token")
oauth2_scheme = OAuth2PasswordBearer(
  tokenUrl="/registration_api/token",
  scopes={"drivers": "Allows access to drivers endpoint and restricts users endpoint", "users": "Allows access to users endpoints but restricts access to drivers endpoint",},
  )

ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_current_driver(request: Request, security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
  if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
  else:
    authenticate_value = f"Bearer"

  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": authenticate_value},
  )
  try:
    payload = jwt.decode(token, config('JWT_SECRET'), algorithms=['HS256'])
    drivers_email = payload.get('sub').get('email')
    
    if drivers_email is None:
      raise credentials_exception
    token_scopes = payload.get("scopes", [])
    token_data = TokenData(email=drivers_email, scopes=token_scopes)
  except:
    raise credentials_exception
  
  for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
  
  driver = await Driver.find_by(email = token_data.email, mongodbConnection = request.app.mongodb)
  if driver is None:
    raise credentials_exception  

  return driver


async def get_current_user(request: Request, security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
  if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
  else:
    authenticate_value = f"Bearer"
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": authenticate_value},
  )

  try:
    payload = jwt.decode(token, config('JWT_SECRET'), algorithms=['HS256'])
    user_email = payload.get('sub').get('email')
    
    if user_email is None:
      raise credentials_exception
    token_scopes = payload.get("scopes", [])
    token_data = TokenData(email=user_email, scopes=token_scopes)
  except:
    raise credentials_exception
  
  for scope in security_scopes.scopes:
    if scope not in token_data.scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
  user = await User.find_by(email = token_data.email, mongodbConnection = request.app.mongodb)
  
  if user is None:
    raise credentials_exception
  
  return user

# authentication
async def authenticate_driver(email: str, password: str, request: Request):
  driver = await Driver.find_by(email = email, mongodbConnection = request.app.mongodb)
  if not driver:
    return False

  if not bcrypt.checkpw(password.encode('utf8'), driver['encryptedPassword'].encode('utf8')):
    return False

  return driver

async def authenticate_user(email: str, password: str, request: Request):
  user = await User.find_by(email = email, mongodbConnection = request.app.mongodb)
  if not user:
    return False

  if not bcrypt.checkpw(password.encode('utf8'), user['encryptedPassword'].encode('utf8')):
    return False

  return user

async def get_current_active_driver(
  current_driver: Driver = Security(get_current_driver, scopes=["drivers"])
):
  return current_driver

async def get_current_active_user(
  current_user: User = Security(get_current_user, scopes=["users"])
):
  return current_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, config('JWT_SECRET'), algorithm='HS256')
  
  return encoded_jwt


@router.post("/token", description="Generate a token which represent that the driver is logged in to the system")
async def generate_token(request: Request, security_scopes: SecurityScopes, form_data: OAuth2PasswordRequestForm = Security()):
  driver = None
  user = None

  if "drivers" in form_data.scopes:
    driver = await authenticate_driver(form_data.username, form_data.password, request)
    if not driver:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
      )
  else:
    user = await authenticate_user(form_data.username, form_data.password, request)
    if not user:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
      )

  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
        data={"sub": driver or user, "scopes": form_data.scopes},
        expires_delta=access_token_expires
    )

  return {"access_token": access_token, "token_type": "bearer"}

# this should rather pass a user object instead of a driver
@router.get("/drivers", description="Get information of all the drivers")
async def get_drivers(request: Request, driver: Driver = Depends(get_current_active_driver)):
  drivers = []
  
  cursor = request.app.mongodb["drivers"].find({})
  async for document in cursor:
    drivers.append(Driver(**document))
  
  # we can access token variable in here, so using tokens we can check if its 
  # the valid current user and then return driver based on that 
  return drivers

@router.get("/driver/{id}", description="Return the driver corrosponding to the id passed in as parameter")
async def get_driver(request: Request, id: str, driver: Driver = Depends(get_current_active_driver)):
  response = await request.app.mongodb["drivers"].find_one({"_id": id})
  if response:
    return response
  raise HTTPException(404, f"No driver with id {id} found")

@router.post("/driver", description="Create a new Driver")
async def post_driver(request: Request, driver: Driver):
  driver = jsonable_encoder(driver)
  driver['encryptedPassword'] = bcrypt.hashpw(driver['encryptedPassword'].encode('utf8'), bcrypt.gensalt()).decode('utf8')

  try:
    new_driver = await request.app.mongodb["drivers"].insert_one(driver)
    created_driver = await request.app.mongodb["drivers"].find_one({"_id": new_driver.inserted_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_driver)
  except pymongo.errors.DuplicateKeyError as err:
    raise HTTPException(404, f"{err}")

@router.put("/driver/{id}", description="Update a drivers record")
async def update_driver(id: str, request: Request, driver: UpdateDriver = Body(...), depends: Driver = Depends(get_current_active_driver)):
  
  driver = cleanNullValues(driver.dict(), None)
  # driver = {k: v for k, v in driver.dict().items() if v is not None and v}
  if len(driver) >= 1:
    update_result = await request.app.mongodb["drivers"].update_one(
      {"_id": id}, {"$set": driver}
    )

    if update_result.modified_count == 1:
        updated_driver = await request.app.mongodb["drivers"].find_one({"_id": id})
        if (update_driver) is not None:
          return updated_driver

    existing_driver = await request.app.mongodb["drivers"].find_one({"_id": id})
    if (existing_driver) is not None:
      return existing_driver

  raise HTTPException(status_code=404, detail=f"Driver {id} not found")


@router.delete("/driver/{id}", description="Delete a driver")
async def delete_driver(id: str, request: Request, driver: Driver = Depends(get_current_active_driver)):
    delete_result = await request.app.mongodb["drivers"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Driver {id} not found")

@router.get("/drivers/me", description='Read information about the current logged in driver')
async def current_driver(driver: Driver = Depends(get_current_active_driver)):
  return driver



# User routes

@router.get("/users", description="Get information about all the users")
async def get_users(request: Request, user: User = Depends(get_current_active_user)):
  users = []

  cursor = request.app.mongodb["users"].find({})
  print(cursor)
  async for document in cursor:
    users.append(User(**document))
  return users

@router.post("/user", description="Create a new User")
async def post_user(request: Request, user: User):
  user = jsonable_encoder(user)

  user['encryptedPassword'] = bcrypt.hashpw(user['encryptedPassword'].encode('utf8'), bcrypt.gensalt()).decode('utf8')

  try:
    new_user = await request.app.mongodb["users"].insert_one(user)
    created_user = await request.app.mongodb["users"].find_one({"_id": new_user.inserted_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)
  except pymongo.errors.DuplicateKeyError as err:
    raise HTTPException(404, f"{err}")
  
@router.get("/user/{id}", description="Return the user corrosponding to the id passed in as parameter")
async def get_user(request: Request, id: str, depends: User = Depends(get_current_active_user)):
  response = await request.app.mongodb["users"].find_one({"_id": id})
  if response:
    return response
  raise HTTPException(404, f"No user with id {id} found")

@router.put("/user/{id}", description="Update a drivers record")
async def update_user(id: str, request: Request, user: UpdateUser = Body(...), depends: User = Depends(get_current_active_user)):
  user = cleanNullValues(user.dict(), None)

  if len(user) >= 1:
    update_result = await request.app.mongodb["users"].update_one(
      {"_id": id}, {"$set": user, "$currentDate": {"lastModified": True}}
    )

    if update_result.modified_count == 1:
        updated_user = await request.app.mongodb["users"].find_one({"_id": id})
        if (update_user) is not None:
          return updated_user

    existing_user = await request.app.mongodb["users"].find_one({"_id": id})
    if (existing_user) is not None:
      return existing_user

  raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.delete("/user/{id}", description="Delete a User")
async def delete_user(id: str, request: Request, depends: User = Depends(get_current_active_user)):
    delete_result = await request.app.mongodb["users"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.get("/users/me", description='get current logged in user')
async def current_user(user: User = Depends(get_current_active_user)):
    return user
