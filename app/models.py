import asyncio
import importlib
import json
import os
from abc import ABC, abstractmethod
from pprint import pformat
from urllib.parse import quote_plus, urljoin

from aiohttp_retry import RetryClient, ExponentialRetry
from bs4 import BeautifulSoup


def tag_strip(tag):
    """
    :param tag: HTML tag to get clean text from
    :type tag: bs4.Tag
    :return: clean text from tag
    :rtype: str
    """
    return tag.text.strip()


def merge_list_dictionaries(*ds):
    """
    :param ds: dictionaries with list values
    :type ds: tuple
    :return: merged dictionaries with appended values
    :rtype: dict
    """
    for d2 in ds[1:]:
        for k in d2:
            if k in ds[0]:
                ds[0][k] += d2[k]
            else:
                ds[0][k] = d2[k]
    return ds[0]


def _get_coroutines_from_parsers(cards, parsers):
    """
    :param cards: names of cards to search for
    :type cards: list
    :return: coroutines for offers from given parsers
    :rtype: list
    """
    coroutines = []
    for parser in parsers:
        parser = importlib.import_module(f"app.parsers.{parser}.parser").Parser()
        coroutines += [parser.parse_card_offers(card) for card in cards]
    return coroutines


async def parse_offers(cards, parsers):
    """
    :param cards: names of cards to search for
    :type cards: list
    :param parsers: names of parsers to search from
    :type parsers: list
    :return: available offers
    :rtype: dict
    """
    offers = await asyncio.gather(*_get_coroutines_from_parsers(cards, parsers))
    result = merge_list_dictionaries(*offers)

    for card in result:
        result[card].sort(key=lambda x: x.price)

    return result


class Seller:
    """Person/shop, responsible for selling"""

    def __init__(self, name, link, source=None):
        self.name = name
        self.link = link
        self.source = source

    def __repr__(self):
        return pformat(self.__dict__)

    def to_json(self):
        """
        :return: object, converted to json
        :rtype: str
        """
        return json.dumps(dict(name=self.name, link=self.link, source=self.source))


class Offer:
    """Offer for certain card"""

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
        """
        :return: object, converted to json
        :rtype: str
        """
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

    @staticmethod
    def _to_soup(html_text):
        """
        :param html_text: HTML code of the page to parse
        :type html_text: str
        :return: data structure representing parsed HTML document 
        :rtype: BeautifulSoup
        """
        return BeautifulSoup(html_text, features="html.parser")

    def _get_full_url(self, url):
        """
        :param url: relative link
        :type url: str
        :return: absolute link
        :rtype: str
        """
        return urljoin(self._DOMAIN, url)

    async def _get_page(self, query):
        """
        :param query: relative link for given website
        :type search: str
        :return: page with result of GET request
        :rtype: BeautifulSoup
        """
        url = self._get_full_url(query)
        print(f"GET request: {url}")
        async with RetryClient(
            retry_options=ExponentialRetry(attempts=1)
        ) as client:
            async with client.get(url) as response:
                html = await response.text()
        return self._to_soup(html)

    async def _get_offers_page(self, search):
        """
        :param search: card to search on given website
        :type search: str
        :return: search page with results
        :rtype: BeautifulSoup
        """
        return await self._get_page(self._SEARCH.format(quote_plus(search)))  # pylint: disable=no-member

    @abstractmethod
    async def parse_card_offers(self, card):
        """
        :param card: card name to search offers for
        :type card: str
        :return: offers for given card
        :rtype: dict
        """
        raise NotImplementedError
