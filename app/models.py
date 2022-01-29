import asyncio
import importlib
import json
from abc import ABC, abstractmethod
from pprint import pformat
from urllib.parse import quote_plus, urljoin
from typing import List

from aiohttp_retry import RetryClient, ExponentialRetry
from bs4 import BeautifulSoup
from pydantic import BaseModel  # pylint: disable=no-name-in-module


def tag_strip(tag):
    """Takes text from tag and returns it stripped from whitespace"""
    return tag.text.strip()


def merge_list_dictionaries(*dictionaries):
    """Merges dictionary list values from given dictionaries"""
    for addendum in dictionaries[1:]:
        for key in addendum:
            if key in dictionaries[0]:
                dictionaries[0][key] += addendum[key]
            else:
                dictionaries[0][key] = addendum[key]
    return dictionaries[0]


def _get_coroutines_from_parsers(cards, parsers, semaphore, allow_empty, allow_art):
    """Gathers coroutines from allowed parsers"""
    coroutines = []
    for parser in parsers:
        parser = importlib.import_module(f"app.parsers.{parser}.parser").Parser(
            allow_empty, allow_art, semaphore
        )
        coroutines += [parser.parse_card_offers(card) for card in cards]
    return coroutines


def is_valid_payload(payload):
    """Validates search query size"""
    if (
        len(payload["cards"]) < 1
        or len(payload["cards"]) > 15
        or any(not card.strip() or len(card) < 3 for card in payload["cards"])
    ):
        return False
    return True


async def parse_offers(cards, parsers, semaphore, allow_empty=True, allow_art=True):
    """Gathers offers and parses them"""
    result = await asyncio.gather(
        *_get_coroutines_from_parsers(
            cards, parsers, semaphore, allow_empty, allow_art
        ),
        return_exceptions=True,
    )

    offers = []
    for item in result:
        if type(item) is not dict:
            print(f"During work of parsers the exception happened: {item}")
        else:
            offers.append(item)

    result = merge_list_dictionaries(*offers)

    for card in result:
        result[card].sort(key=lambda x: x.price)

    return result


class SearchJSON(BaseModel):
    """JSON for search request"""

    cards: List[str]
    allow_empty: bool
    allow_art: bool


class Seller:
    """Person/shop, responsible for selling"""

    def __init__(self, name, link, source=None):
        self.name = name
        self.link = link
        self.source = source

    def __repr__(self):
        return pformat(self.__dict__)

    def to_json(self):
        """Turns object to json"""
        return json.dumps(dict(name=self.name, link=self.link, source=self.source))


class Offer:
    """Offer of certain card"""

    def __init__(
        self,
        card_name,
        language,
        is_foil,
        condition,
        link,
        price,
        currency_code,
        amount,
        seller,
    ):
        self.card_name = card_name
        self.language = language
        self.is_foil = is_foil
        self.condition = condition
        self.link = link
        self.price = price
        self.currency_code = currency_code
        self.amount = amount
        self.seller = seller

    def to_json(self):
        """Turns object to json"""
        return json.dumps(
            dict(
                card_name=self.card_name,
                language=self.language,
                is_foil=self.is_foil,
                condition=self.condition,
                link=self.link,
                price=self.price,
                currency_code=self.currency_code,
                amount=self.amount,
                seller={
                    "name": self.seller.name,
                    "link": self.seller.link,
                    "source": self.seller.source,
                },
            ),
            default=str,
        )


class BaseParser(ABC):
    """Abstract parser to derivate from"""

    _DOMAIN = NotImplemented
    _SEARCH = NotImplemented

    CURRENCY_CODE = NotImplemented

    def __init__(self, allow_empty, allow_art, semaphore):
        self._allow_empty = allow_empty
        self._allow_art = allow_art
        self._semaphore = semaphore

    @staticmethod
    def _to_soup(html_text):
        return BeautifulSoup(html_text, features="html.parser")

    def _get_full_url(self, postfix):
        return urljoin(self._DOMAIN, postfix)

    async def _get_page(self, query):
        url = self._get_full_url(query)
        print(f"GET request: {url}")
        async with self._semaphore:
            async with RetryClient(
                retry_options=ExponentialRetry(attempts=3)
            ) as client:
                async with client.get(url) as response:
                    html = await response.text()
        return self._to_soup(html)

    async def _get_offers_page(self, search):
        return await self._get_page(
            self._SEARCH.format(quote_plus(search))
        )  # pylint: disable=no-member

    @abstractmethod
    async def parse_card_offers(self, card, allow_empty, allow_art):
        """Extracts information from given page and transforms it"""
        raise NotImplementedError
