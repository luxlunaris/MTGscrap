import asyncio
import re
from decimal import Decimal
from urllib.parse import quote

from app.models import BaseParser, Offer, Seller, tag_strip


class Parser(BaseParser):
    """Extraction and transformation rules for source angrybottlegnome.ru"""

    _DOMAIN = "http://angrybottlegnome.ru/"
    _SEARCH = "/shop/search/{}"

    CURRENCY_CODE = "RUB"

    def _parse_offers_from_card_page(self, page):
        offers = []

        card_name = tag_strip(page.select_one("h1"))
        if not self._allow_art and "Art Card" in card_name:
            return {}

        seller = Seller(name="Angrybottlegnome", link=self._DOMAIN)
        for row in page.select(
            ".abg-card-version-instock, .abg-card-version-outofstock"
        ):
            match = re.match(
                r"(\w+), +([\w\/]+) +(\w*)\s?\((\d+).+: (\d+)\)", tag_strip(row)
            )

            amount = int(match.group(5))
            if not (amount or self._allow_empty):
                continue

            try:
                offers.append(
                    Offer(
                        card_name=card_name,
                        language=match.group(1).lower(),
                        is_foil=match.group(3) == "Фойл",
                        condition=match.group(2),
                        link=self._get_full_url(self._SEARCH.format(quote(card_name))),
                        price=Decimal(match.group(4)),
                        currency_code=self.CURRENCY_CODE,
                        amount=amount,
                        seller=seller,
                    )
                )
            except (AttributeError, TypeError) as e:
                print(e)
                continue

        return offers

    def _parse_search_table(self, table):
        links = []
        for row in table.select("tbody tr"):
            cols = row.select("td")
            if tag_strip(cols[2]) != 0:
                links.append(cols[0].select_one("a").attrs["href"])

        return links

    async def _get_offers_page(self, search):
        return await self._get_page(self._SEARCH.format(quote(search)))

    async def parse_card_offers(self, card):
        """Extracts information from given page and transforms it"""
        offers = []
        page = await self._get_offers_page(card)
        table = page.select_one("#search-results table")
        if table is None:
            return {}
        available_cards = self._parse_search_table(table)

        pages = await asyncio.gather(
            *[self._get_page(link) for link in available_cards]
        )

        for page in pages:
            offers += self._parse_offers_from_card_page(page)

        return {card: offers}
