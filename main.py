from fastapi import FastAPI
import asyncio

import external
import routes

app = FastAPI()

app.include_router(routes.v1router)


@app.on_event("startup")
async def startup_event1():
    asyncio.create_task(external.spotify.update_listens_loop())

