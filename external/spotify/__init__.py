import datetime

# import aiohttp
from aiohttp import ClientSession
# from sqlalchemy.ext.asyncio import AsyncSession

# import external

import models

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


__all__ = ['token', 'currently_playing']
