"""Abstract models for parsing"""

import asyncio
import aiohttp
import json
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Seller():
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def to_json(self):
        return json.dumps(
            dict(
                name=self.name,
                link=self.link
            )
        )


class Offer():
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
            seller
        ):
        self.card_name = card_name
        self.language = language
        self.is_foil = is_foil
        self.condition = condition
        self.link = link
        self.price = price
        self.currency_code = currency_code
        self.seller = seller

    def to_json(self):
        return json.dumps(
            dict(
                card_name=self.card_name,
                language=self.language,
                is_foil=self.is_foil,
                condition=self.condition,
                link=self.link,
                price=self.price,
                currency_code=self.currency_code,
                seller={
                    'name': self.seller.name,
                    'link': self.seller.link
                }
            ),
            default=str
        )

class BaseParser(ABC):
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
        return BeautifulSoup(html_text, features='html.parser')

    def _get_full_url(self, url):
        """
        :param url: relative link
        :type url: str
        :return: absolute link
        :rtype: str
        """
        return urljoin(self._DOMAIN, url)

    async def _get_offers_page(self, search):
        """
        :param search: card to search on given website
        :type search: str
        :return: search page with results
        :rtype: BeautifulSoup
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._get_full_url(
                    self._SEARCH.format(search)  # pylint: disable=no-member
                    )
            ) as response:
                html = await response.text()
        return self._to_soup(html)

    @abstractmethod
    async def _parse_card_offers(self, card):
        """
        :param card: card name to search offers for
        :type card: str
        :return: offers for given card
        :rtype: list
        """
        raise NotImplementedError


    async def parse_offers(self, cards):
        """
        :param cards: cards to search offers for
        :type cards: list
        :return: offers from given source
        :rtype: list
        """
        result = []
        for card in cards:
            offers = await self._parse_card_offers(card)
            result += offers
        return result
