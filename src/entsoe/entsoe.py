from typing import Optional
import aiohttp
import asyncio

from lxml import etree

import datetime

from .consts import DAY_AHEAD_DOCUMENT, DATE_FORMAT
from .xmlreader import day_ahead_price_list


class Price:
    def __init__(self, begin, end, price_orig, price_target=None) -> None:
        self.begin = begin
        self.end = end
        self.price_orig = price_orig
        self.price_target = price_target


class EntsoeDayAhead:
    def __init__(
        self,
        access_token,
        area,
        currency="auto",
        session=None,
        url="https://transparency.entsoe.eu/api",
    ) -> None:
        self.access_token = access_token
        self.area = area
        self.currency = currency
        self.url = url
        self.session = session if session is not None else aiohttp.ClientSession()

        self.original_currency = None
        self.measurement_unit = None
        self.start = None
        self.end = None
        self.resolution = None

        self.prices = []

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
            self.update_state(day_ahead_price_list(res))

    def update_state(self, state_dict):
        self.original_currency = state_dict["currency"]
        self.measurement_unit = state_dict["measurement_unit"]
        self.start = state_dict["start"]
        self.end = state_dict["end"]
        self.resolution = state_dict["resolution"]

        self.points = [
            Price(p["start"], p["end"], p["amount"]) for p in state_dict["points"]
        ]
        self.points.sort(key=lambda p: p.begin)
