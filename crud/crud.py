from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import models
import schemas


async def get_user(db: AsyncSession, user_id: int):
    results = await db.execute(select(models.User).where(models.User.id == user_id))
    return results.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str):
    results = await db.execute(select(models.User).where(models.User.username == username))
    return results.scalars().first()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    existing_user = await get_user_by_username(db, user.username)
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Duplicate username")
    db_user = models.User(username=user.username, password=user.password, first_login=user.firstLoginDate)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_oauth2_by_access_token(db: AsyncSession, access_token: str):
    results = await db.execute(select(models.OAuth2).where(models.OAuth2.access_token == access_token))
    return results.scalars().first()


async def get_oauth2_by_user_id(db: AsyncSession, user_id: int) -> models.OAuth2 | None:
    results = await db.execute(select(models.OAuth2).where(models.OAuth2.user_id == user_id))
    return results.scalars().first()


async def create_oauth2(db: AsyncSession, oauth2: schemas.OAuth2Create):
    existing_user = await get_user(db, oauth2.userId)
    if existing_user is None:
        raise HTTPException(status_code=422, detail="user not found by user id")
    db_oauth2 = models.OAuth2(token_type=oauth2.tokenType, api_name=oauth2.apiName, access_token=oauth2.accessToken,
                              refresh_token=oauth2.refreshToken, received=oauth2.receivedDate, expiry=oauth2.expiryDate,
                              user_id=oauth2.userId)
    db.add(db_oauth2)
    await db.commit()
    await db.refresh(db_oauth2)
    return db_oauth2


async def get_prev_listen(db: AsyncSession, oauth2: models.OAuth2) -> models.Listen | None:
    results = await db.execute(
        select(models.Listen).where(models.Listen.user_id == oauth2.user_id).order_by(models.Listen.recorded.desc()))
    return results.scalars().first()


async def create_listen(db: AsyncSession, listen: schemas.ListenCreate):
    existing_user = await get_user(db, listen.userId)
    if existing_user is None:
        raise HTTPException(status_code=422, detail="user not found by user id")
    db_listen = models.Listen(user_id=listen.userId, recorderd=listen.recorded, api_name=listen.apiName,
                              api_id=listen.apiId, title=listen.title, album=listen.album, artists=listen.artists)
    db.add(db_listen)
    await db.commit()
    await db.refresh(db_listen)
    return db_listen
