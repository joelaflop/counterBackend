import asyncio
import aiohttp
import datetime

from aiohttp import ClientSession

import models
import crud
import database

spotify_accounts_url = "https://accounts.spotify.com"
spotify_api_url = "https://api.spotify.com"
spotify_client_idSecret_base64 = "MTNhYWY4OGQ2ZTUxNDRkMTlhZTYzOTY5Yzk3NmM4NjE6MjYzZjM3MmNlMDdjNGRhMjgxZjU5MzM1ZTEwNGNiN2M="

# TODO close this session when done


async def token(http_session: ClientSession, oauth2: models.OAuth2):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': 'Basic ' + spotify_client_idSecret_base64}
    async with http_session.post(spotify_accounts_url + "/api/token",
                                 headers=headers,
                                 data={'grant_type': 'refresh_token',
                                       'refresh_token': oauth2.refresh_token}) as resp:
        # todo handled bad responses
        return await resp.json()


# TODO: handled 401 with helper function
async def currently_playing(http_session: ClientSession, oauth2: models.OAuth2):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + oauth2.access_token}
    async with http_session.get(spotify_api_url + '/v1/me/player/currently-playing',
                                headers=headers) as resp:
        if resp.status == 204:
            return None
        elif resp.status == 401:
            pass
        # todo handled other bad responses
        return await resp.json()


async def update_listen(db, http_session, oauth2):  # TODO break into multiple functions
    should_commit = False
    if oauth2.expiry <= datetime.datetime.now(datetime.timezone.utc):
        spotify_res = await token(http_session, oauth2)
        oauth2.access_token = spotify_res['access_token']
        oauth2.expiry = datetime.datetime.now() + datetime.timedelta(seconds=spotify_res['expires_in'])
        db.add(oauth2)
        should_commit = True
    spotify_res = await currently_playing(http_session, oauth2)
    if spotify_res is not None:
        listen = models.Listen(spotify_res=spotify_res, user_id=oauth2.user_id)
        prev_listen = await crud.get_prev_listen(db, oauth2)
        if not listen.likely_the_same(prev_listen):
            db.add(listen)
            should_commit = True
    if should_commit:
        await db.commit()


async def update_listens_loop():  # TODO doesn't belong here
    async with database.session_factory() as db:
        async with aiohttp.ClientSession() as http_session:
            while True:
                try:
                    oauth2 = await crud.get_oauth2_by_user_id(db, 1)
                    await update_listen(db, http_session, oauth2)
                except Exception as e:
                    print(e)
                finally:
                    await asyncio.sleep(30)

__all__ = ['token', 'currently_playing']
