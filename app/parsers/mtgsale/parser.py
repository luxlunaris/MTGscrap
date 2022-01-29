import asyncio
from decimal import Decimal

from app.models import BaseParser, Offer, Seller, tag_strip


class Parser(BaseParser):
    """Extraction and transformation rules for source mtgsale.ru"""

    _DOMAIN = "https://mtgsale.ru"
    _SEARCH = "/home/search-results?Name={}"

    CURRENCY_CODE = "RUB"

    def _parse_vertical_table(self, table):
        result = []
        for row in table.select(".ctclass"):
            card_name = tag_strip(row.select_one("a.tnamec"))
            if not self._allow_art and "Art Card" in card_name:
                continue

            amount = int(row.select_one(".colvo").text.split()[0])
            if not (amount or self._allow_empty):
                continue

            try:
                result.append(
                    {
                        "card_name": card_name,
                        "language": row.select_one(".lang i").attrs["title"].lower(),
                        "is_foil": tag_strip(row.select_one(".foil")) == "Фойл",
                        "condition": tag_strip(row.select_one(".sost span")),
                        "link": self._get_full_url(
                            row.select_one("a.tnamec").attrs["href"]
                        ),
                        "price": Decimal(row.select_one(".pprice").text.split()[0]),
                        "amount": amount,
                    }
                )
            except (AttributeError, TypeError) as e:
                print(e)
                continue

        return result

    async def parse_card_offers(self, card):
        """Extracts information from given page and transforms it"""
        seller = Seller(name="MTGSale", link=self._DOMAIN)
        page = await self._get_offers_page(card)
        return {
            card: [
                Offer(**row, currency_code=self.CURRENCY_CODE, seller=seller)
                for row in self._parse_vertical_table(page.select_one("#taba"))
            ]
        }
