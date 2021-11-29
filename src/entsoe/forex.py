import aiohttp

from abc import abstractmethod, ABC


class Forex(ABC):
    def __init__(self, session) -> None:
        super().__init__()
        self._session = session if session is not None else aiohttp.ClientSession()

    @abstractmethod
    async def get_rate(self, base, currency):
        pass


class NorgesBankForex(Forex):
    async def get_rate(self, base="EUR", currency="NOK"):
        if currency != "NOK":
            raise ValueError("Norges bank only converts to NOK")

        async with self._session.get(
            f"https://data.norges-bank.no/api/data/EXR/B.{base.upper()}.NOK.SP",
            params={
                "detail": "dataonly",
                "lastNObservations": 1,
                "format": "sdmx-json",
            },
        ) as resp:
            res = await resp.json()

            return {
                "NOK": float(
                    res["data"]["dataSets"][0]["series"]["0:0:0:0"]["observations"][
                        "0"
                    ][0]
                )
            }


class ExchangeRateForex(Forex):
    def __init__(
        self, access_token, api_url="http://api.exchangeratesapi.io/v1/", session=None
    ) -> None:
        super().__init__(session)
        self._access_token = access_token
        self._api_url = api_url

    async def get_rate(self, base="EUR", currency="NOK"):
        symbols = [currency, base]

        async with self._session.get(
            f"{self._api_url}latest",
            params={
                "access_key": self._access_token,
                "symbols": ",".join(symbols),
            },
        ) as resp:
            res = await resp.json()

            base_rate = res["rates"][base]

            rates = {
                cur: rate / base_rate
                for cur, rate in res["rates"].items()
                if cur.lower() != base.lower()
            }

            return rates
