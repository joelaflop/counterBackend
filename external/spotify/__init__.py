import asyncio
import aiohttp
import datetime
from collections import namedtuple

from aiohttp import ClientSession

import models
import crud
import database

spotify_accounts_url = "https://accounts.spotify.com"
spotify_api_url = "https://api.spotify.com"
spotify_client_idSecret_base64 = "MTNhYWY4OGQ2ZTUxNDRkMTlhZTYzOTY5Yzk3NmM4NjE6MjYzZjM3MmNlMDdjNGRhMjgxZjU5MzM1ZTEwNGNiN2M="


StatusResTuple = namedtuple("Res", ["status", "res"])


async def token(db, http_session: ClientSession, oauth2: models.OAuth2):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': 'Basic ' + spotify_client_idSecret_base64}
    async with http_session.post(spotify_accounts_url + "/api/token",
                                 headers=headers,
                                 data={'grant_type': 'refresh_token',
                                       'refresh_token': oauth2.refresh_token}) as resp:
        if resp.status == 200:
            res = await resp.json()
            oauth2.access_token = res['access_token']
            oauth2.expiry = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=res['expires_in'])
        else:
            pass  # TODO set some status on this oauth2
        db.add(oauth2)


async def currently_playing(db, http_session: ClientSession, oauth2: models.OAuth2) -> StatusResTuple:
    helper_res = await currently_playing_helper(http_session, oauth2)
    if helper_res.status == 401:
        await token(db, http_session, oauth2)
    helper_res = await currently_playing_helper(http_session, oauth2)
    return helper_res


async def currently_playing_helper(http_session: ClientSession, oauth2: models.OAuth2) -> StatusResTuple:
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + oauth2.access_token}
    async with http_session.get(spotify_api_url + '/v1/me/player/currently-playing', headers=headers) as resp:
        return StatusResTuple(200, await resp.json()) if resp.status == 200 else StatusResTuple(resp.status, None)


async def update_listen(db, http_session, oauth2):
    should_commit = False
    if oauth2.expiry <= datetime.datetime.now(tz=datetime.timezone.utc):
        await token(db, http_session, oauth2)
        should_commit = True
    currently_listening = await currently_playing(db, http_session, oauth2)
    if currently_listening.status == 200:
        listen = models.Listen(spotify_res=currently_listening.res, user_id=oauth2.user_id)
        prev_listen = await crud.get_prev_listen(db, oauth2)
        if listen.likely_new_listen(prev_listen):
            db.add(listen)
            should_commit = True
    if should_commit:
        await db.commit()


async def update_listens_loop():  # TODO doesn't belong here
    async with database.session_factory() as db:
        async with aiohttp.ClientSession() as http_session:
            while True:
                await asyncio.sleep(30)
                oauth2 = await crud.get_oauth2_by_user_id(db, 1)
                await update_listen(db, http_session, oauth2)


__all__ = ['token', 'currently_playing']
