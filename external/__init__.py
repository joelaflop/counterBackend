import aiohttp

from . import spotify

async def get_http_session():
    http_session = aiohttp.ClientSession()
    try:
        yield http_session
    finally:
        await http_session.close()

__all__ = ['get_http_session', 'spotify']
