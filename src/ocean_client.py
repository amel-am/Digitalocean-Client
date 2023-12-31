from datetime import datetime
from aiohttp import ClientSession
from .yaml import ocean_token
from .constants import RequestMethods, BASE_API_URL


class DigitalOceanClient(object):
    def __init__(self):
        self._headers = {"Content-Type": 'application/json',
                         "Authorization": f'Bearer {ocean_token}'}
        self._ratelimit_result = ""
        self._ratelimit_time = None

    @property
    def ratelimit(self):
        return self._ratelimit_result

    @property
    def limit_time(self):
        return self._ratelimit_time

    async def _request(self, method: str, path: str) -> dict:
        async with ClientSession() as session:
            async with session.request(method=method, url=f"{BASE_API_URL}/{path}", headers=self._headers) as response:
                if response.status != 200:
                    return print(f"Something went wrong, status code is: {response.status}")
                await self._set_ratelimits(response.headers)
                return await response.json()

    async def get_keys(self) -> list:
        response = await self._request(RequestMethods.GET, "account/keys")
        return response["ssh_keys"]

    async def get_droplets(self) -> list:
        response = await self._request(RequestMethods.GET, "droplets")
        return response["droplets"]

    async def get_account(self) -> dict:
        response = await self._request(RequestMethods.GET, "account")
        return response["account"]

    async def _set_ratelimits(self, dict_: dict) -> None:
        self._ratelimit_time = datetime.fromtimestamp(
            float(dict_['ratelimit-reset']))
        self._ratelimit_result = "\n".join([f"ratelimit: {dict_['ratelimit-limit']}",
                                            f"ratelimit-remaining: {dict_['ratelimit-remaining']}",
                                            f"ratelimit-reset:"])
