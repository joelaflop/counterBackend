import datetime
from pydantic import BaseModel

from models.models import ApiName, TokenType


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    firstLoginDate: None | datetime.datetime


class User(UserBase):
    id: int
    firstname: str
    lastname: str
    lastLoginDate: datetime.datetime
    numLogins: int
    timezone: str
    lastUpdatedDate: datetime.datetime

    class Config:
        orm_mode = True


class OAuth2Base(BaseModel):
    tokenType: TokenType
    apiName: ApiName
    userId: int


class OAuth2Create(OAuth2Base):
    accessToken: str
    refreshToken: str
    receivedDate: datetime.datetime
    expiryDate: datetime.datetime


class OAuth2(OAuth2Create):
    id: int
    lastUpdatedDate: datetime.datetime


class ListenCreate(BaseModel):
    userId: int
    recorded: datetime.datetime
    apiName: str
    apiId: str
    api_timestamp: int
    duration: int
    title: str
    album: str
    artists: str


class Listen(ListenCreate):
    id: int
    lastUpdatedDate: datetime.datetime
