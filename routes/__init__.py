from fastapi import APIRouter, Depends

import crud
import database
import external
from . import v1

v1Router = APIRouter(
    prefix="/v1",
    tags=["user"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)

v1Router.include_router(v1.router)

@v1Router.get("/")
async def root(db=Depends(database.get_db), http_session=Depends(external.get_http_session)):
    async with database.engine.begin() as conn:
        # oauth2 = (await conn.execute(sqlalchemy.text('select * from "oauth2"'))).all()
        oauth2 = await crud.get_oauth2_by_user_id(db, 1)
        return oauth2
