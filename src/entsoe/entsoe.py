from typing import List, Optional
import aiohttp

import datetime

from .consts import DAY_AHEAD_DOCUMENT, DATE_FORMAT
from .xmlreader import day_ahead_price_list

from .forex import Forex


class Price:
    def __init__(
        self,
        begin: datetime.datetime,
        end: datetime.datetime,
        price_orig: float,
        rate: Optional[float] = None,
    ) -> None:
        self.begin = begin
        self.end = end
        self.price_orig = price_orig
        if rate is None:
            self.price_target = None
        else:
            self.price_target = price_orig * rate

    def __str__(self) -> str:
        return f"Price [begin={self.begin}, end={self.end}, price_orig={self.price_orig}, price_target={self.price_target}]"

    def __repr__(self) -> str:
        return self.__str__()


class EntsoeDayAhead:
    def __init__(
        self,
        access_token: str,
        area: str,
        currency: str = "auto",
        measurement_unit: str = "kWh",
        session: Optional[aiohttp.ClientSession] = None,
        url: str = "https://transparency.entsoe.eu/api",
        forex: Optional[Forex] = None,
    ) -> None:
        self.access_token = access_token
        self.area = area
        self.currency = currency
        self.url = url
        self.session = session if session is not None else aiohttp.ClientSession()
        self.forex = forex

        self.original_currency = None
        self.measurement_unit = None
        self.start = None
        self.end = None
        self.resolution = None

        if measurement_unit.lower() == "mwh":
            self.measurement_unit = "MWh"
        elif measurement_unit.lower() == "kwh":
            self.measurement_unit = "kWh"
        elif measurement_unit.lower() == "wh":
            self.measurement_unit = "Wh"

        self.prices: List[Price] = []

    def get_unit_multiplier(self, unit):
        mults = {"": 1, "k": 1e3, "m": 1e6}

        unit = unit.lower()
        self_unit = self.measurement_unit.lower()

        if not (unit.endswith("wh") and self_unit.endswith("wh")):
            raise ValueError("Both units must be multipliers of Wh")

        return mults[self_unit[0]] / mults[unit[0]]

    async def update(self, startday: Optional[datetime.datetime] = None):
        if startday is None:
            now = datetime.datetime.now()
            update_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
            if now < update_time:
                startday = now - datetime.timedelta(days=1)
            else:
                startday = now

        start_point = startday.replace(hour=23, minute=0, second=0, microsecond=0)
        start_date_str = start_point.strftime(DATE_FORMAT)
        end_point = start_point + datetime.timedelta(days=1)
        end_date_str = end_point.strftime(DATE_FORMAT)

        async with self.session.get(
            self.url,
            params={
                "securityToken": self.access_token,
                "documentType": DAY_AHEAD_DOCUMENT,
                "in_Domain": self.area,
                "out_Domain": self.area,
                "periodStart": start_date_str,
                "periodEnd": end_date_str,
            },
        ) as response:
            res = await response.read()
            await self.update_state(day_ahead_price_list(res))

    async def update_state(self, state_dict):
        self.original_currency = state_dict["currency"]
        self.start = state_dict["start"]
        self.end = state_dict["end"]
        self.resolution = state_dict["resolution"]

        if (self.original_currency != self.currency) and (self.forex is not None):
            rates = await self.forex.get_rate(self.original_currency, self.currency)
            rate = rates[self.currency]
        else:
            rate = None

        unit_mult = self.get_unit_multiplier(state_dict["measurement_unit"])
        self.points = [
            Price(p["start"], p["end"], p["amount"] * unit_mult, rate)
            for p in state_dict["points"]
        ]
        self.points.sort(key=lambda p: p.begin)
