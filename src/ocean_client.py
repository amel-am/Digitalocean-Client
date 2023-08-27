from disnake import utils
from aiohttp import ClientSession
from src.yaml import ocean_token
from src.constants import RequestMethods


class DigitalOceanClient(object):
    def __init__(self):
        self._headers = {'Content-Type': 'application/json',
                         'Authorization': f'Bearer {ocean_token}'}
        self._api_url = "https://api.digitalocean.com/v2/"
        self._ratelimit = None

    @property
    def ratelimit(self):
        return self._ratelimit

    async def _request(self, method: str, link: str) -> dict:
        async with ClientSession() as session:
            async with session.request(method=method, url=link, headers=self._headers) as response:
                if response.status != 200:
                    return print(f"Something went wrong, status code is: {response.status}")
                await self._set_ratelimits(response.headers)
                return await response.json()

    async def get_keys(self) -> list:
        response = await self._request(RequestMethods.GET, f"{self._api_url}account/keys")
        return response["ssh_keys"]

    async def get_droplets(self) -> list:
        response = await self._request(RequestMethods.GET, f"{self._api_url}droplets")
        return response["droplets"]

    async def get_account(self) -> dict:
        response = await self._request(RequestMethods.GET, f"{self._api_url}account")
        return response["account"]

    async def _set_ratelimits(self, dict_: dict) -> None:
        self._ratelimit = {"ratelimit": dict_['ratelimit-limit'],
                           "ratelimit-remaining": dict_['ratelimit-remaining'],
                           "ratelimit-reset": utils.format_dt(int(dict_['ratelimit-reset']))}
