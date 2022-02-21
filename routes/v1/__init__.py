from fastapi import APIRouter, Depends, Response, status

import crud
import database
import schemas
import external

v1router = APIRouter(
    prefix="/v1",
    tags=["v1", "latest"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


@v1router.get("/")
async def root(db=Depends(database.get_db), http_session=Depends(external.get_http_session)):
    async with database.engine.begin() as conn:
        # oauth2 = (await conn.execute(sqlalchemy.text('select * from "oauth2"'))).all()
        oauth2 = await crud.get_oauth2_by_user_id(db, 1)
        return oauth2


@v1router.post("/user")
async def post_user(user: schemas.UserCreate, response: Response, db=Depends(database.get_db)):
    user = await crud.create_user(db, user)
    response.status_code = status.HTTP_201_CREATED
    return user


@v1router.get("/user/{user_id}")
async def get_user(user_id: int, response: Response, db=Depends(database.get_db)):
    user = await crud.get_user(db, user_id)
    if user:
        return user
    response.status_code = status.HTTP_204_NO_CONTENT


@v1router.post("/oauth2")
async def post_oauth2(oauth2: schemas.OAuth2Create, response: Response, db=Depends(database.get_db)):
    oauth2 = await crud.create_oauth2(db, oauth2)
    if oauth2:
        response.status_code = status.HTTP_201_CREATED
        return oauth2
    response.status_code = status.HTTP_304_NOT_MODIFIED