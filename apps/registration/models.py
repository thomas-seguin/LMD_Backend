from typing import Optional, List
import uuid
import datetime
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
#import ipdb

class ORMConfig:
    orm_mode = True

class DriversLicence(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  number: str = Field(...)
  expiryDate: datetime.datetime = Field(...)
  photoUrl: Optional[str]

class Vehicle(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  make: str = Field(...) # Should also be Enum. For example one value of the enum should be Honda and the model will be CRV
  model: str = Field(...) # Should be changed to Enum if possible (This way it will have fixed defined value allowed)
  licensePlateNumber: str = Field(...)
  color: str = Field(...)
  storageCapacity: int = Field(...)
  insurancePolicy: Optional[str] = Field(None)

class Driver(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  email: str = Field(...)
  firstName: str = Field(...)
  lastName: str = Field(...)
  encryptedPassword: str = Field(...) # Replace this with password and re-enter password field
  phoneNumber: str = Field(min_length=10, max_length=10) # figure out a way to add a condition to only have it less than 10 char
  verified: bool = Field(False)
  publicKey: Optional[str]
  totalRequests: int = Field(0)
  driversLicence: DriversLicence 
  vehicle: Vehicle

  @classmethod
  async def find_by(cls, email: Optional[str], mongodbConnection):
    id = None
    response = None
    
    if id:
      response = await mongodbConnection["drivers"].find_one({"_id": id})
    elif email:
      response = await mongodbConnection["drivers"].find_one({"email": email})
    return response


  class Config:
    orm_mode = True

class UpdateDriversLicence(BaseModel):
  number: Optional[str]
  expiryDate: Optional[datetime.datetime]
  photoUrl: Optional[str]

class UpdateVehicle(BaseModel):
  make: Optional[str]
  model: Optional[str]
  licensePlateNumber: Optional[str]
  color: Optional[str]
  storageCapacity: Optional[int]
  insurancePolicy: Optional[str]

# need to add password and re-enter password field
class UpdateDriver(BaseModel):
  email: Optional[str]
  firstName: Optional[str]
  lastName: Optional[str]
  phoneNumber: Optional[str] = Field(min_length=10, max_length=10) 
  publicKey: Optional[str]
  totalRequests: Optional[int]
  driversLicence: Optional[UpdateDriversLicence]
  vehicle: Optional[UpdateVehicle]  

class Address(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  addressLine1: str = Field(...)
  city: str = Field(...)
  state: str = Field(...)
  country: str = Field(...)
  postalCode: str = Field(...)

class UpdateAddress(BaseModel):
  addressLine1: Optional[str]
  city: Optional[str]
  state: Optional[str]
  country: Optional[str]
  postalCode: Optional[str]

# Can be the sender or receiver 
class User(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  email: str = Field(...)
  firstName: str = Field(...)
  lastName: str = Field(...)
  encryptedPassword: str = Field(...) # Replace this with password and re-enter password field
  phoneNumber: str = Field(min_length=10, max_length=10) # figure out a way to add a condition to only have it less than 10 char
  verified: bool = Field(False)
  publicKey: Optional[str] 
  address: Address

  @classmethod
  async def find_by(cls, email: Optional[str], mongodbConnection):
    id = None
    response = None
    
    if id:
      response = await mongodbConnection["users"].find_one({"_id": id})
    elif email:
      response = await mongodbConnection["users"].find_one({"email": email})
    return response


# TODO: need to add password and re-enter password field
class UpdateUser(BaseModel):
  email: Optional[str]
  firstName: Optional[str]
  lastName: Optional[str]
  phoneNumber: Optional[str]
  publicKey: Optional[str]
  address: Optional[UpdateAddress]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
  email: Optional[str] = None
  scopes: List[str] = []