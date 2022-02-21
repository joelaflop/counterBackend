from fastapi import APIRouter, Depends, Response, status

import crud
import database
import schemas

router = APIRouter(
    prefix="/user",
    tags=["user"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


@router.post("/")
async def post_user(user: schemas.UserCreate, response: Response, db=Depends(database.get_db)):
    user = await crud.create_user(db, user)
    response.status_code = status.HTTP_201_CREATED
    return user


@router.get("/{user_id}")
async def get_user(user_id: int, response: Response, db=Depends(database.get_db)):
    user = await crud.get_user(db, user_id)
    if user:
        return user
    response.status_code = status.HTTP_204_NO_CONTENT


@router.post("/oauth2")
async def post_oauth2(oauth2: schemas.OAuth2Create, response: Response, db=Depends(database.get_db)):
    oauth2 = await crud.create_oauth2(db, oauth2)
    if oauth2:
        response.status_code = status.HTTP_201_CREATED
        return oauth2
    response.status_code = status.HTTP_304_NOT_MODIFIED