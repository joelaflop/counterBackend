import datetime
import asyncio
import aiohttp
from fastapi import FastAPI, Depends, Response, status

import models
import schemas
import database
import crud
import external

app = FastAPI()

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: requests.Request, exc: RequestValidationError):
#     print(request)
#     print(type(exc))
#     return JSONResponse({}, status_code=400)


async def update_listen(db, http_session, oauth2):  # TODO break into multiple functions
    should_commit = False
    if oauth2.expiry <= datetime.datetime.now(datetime.timezone.utc):
        spotify_res = await external.spotify.token(http_session, oauth2)
        oauth2.access_token = spotify_res['access_token']
        oauth2.expiry = datetime.datetime.now() + datetime.timedelta(seconds=spotify_res['expires_in'])
        db.add(oauth2)
        should_commit = True
    spotify_res = await external.spotify.currently_playing(http_session, oauth2)
    if spotify_res is not None:
        listen = models.Listen(spotify_res=spotify_res, user_id=oauth2.user_id)
        prev_listen = await crud.get_prev_listen(db, oauth2)
        if not listen.likely_the_same(prev_listen):
            db.add(listen)
            should_commit = True
    if should_commit:
        await db.commit()


async def update_listens_loop():
    async with database.session_factory() as db:
        async with aiohttp.ClientSession() as http_session:
            # todo use asyncio.gather
            while True:
                try:
                    oauth2 = await crud.get_oauth2_by_user_id(db, 1)
                    await update_listen(db, http_session, oauth2)
                except Exception as e:
                    print(e)
                finally:
                    await asyncio.sleep(30)


@app.on_event("startup")
async def startup_event1():
    asyncio.create_task(update_listens_loop())


@app.get("/")
async def root(db=Depends(database.get_db), http_session=Depends(external.get_http_session)):
    async with database.engine.begin() as conn:
        # oauth2 = (await conn.execute(sqlalchemy.text('select * from "oauth2"'))).all()
        oauth2 = await crud.get_oauth2_by_user_id(db, 1)
        return oauth2


@app.post("/user")
async def post_user(user: schemas.UserCreate, response: Response, db=Depends(database.get_db)):
    user = await crud.create_user(db, user)
    response.status_code = status.HTTP_201_CREATED
    return user


@app.get("/user/{user_id}")
async def get_user(user_id: int, response: Response, db=Depends(database.get_db)):
    user = await crud.get_user(db, user_id)
    if user:
        return user
    response.status_code = status.HTTP_204_NO_CONTENT


@app.post("/oauth2")
async def post_oauth2(oauth2: schemas.OAuth2Create, response: Response, db=Depends(database.get_db)):
    oauth2 = await crud.create_oauth2(db, oauth2)
    if oauth2:
        response.status_code = status.HTTP_201_CREATED
        return oauth2
    response.status_code = status.HTTP_304_NOT_MODIFIED
