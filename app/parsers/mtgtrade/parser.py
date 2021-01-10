import asyncio
from decimal import Decimal
from urllib.parse import quote_plus

from app.models import BaseParser, Offer, Seller, tag_strip


class Parser(BaseParser):
    _DOMAIN = "https://mtgtrade.net"
    _SEARCH = "/search/?query={}"

    CURRENCY_CODE = "RUB"

    def __parse_vertical_table(self, table):
        result = []
        
        name = tag_strip(table.select_one("a.catalog-title"))
        if not self._allow_art and "Art Card" in name:
            return {}

        for row in table.select(".search-card tbody tr"):
            amount = int(tag_strip(row.select_one(".sale-count")))
            if not (amount or self._allow_empty):
                continue

            last_seller = row.select_one(".trader-name a") or last_seller
            try:
                result.append(
                    {
                        "card_name": name,
                        "language": row.select_one(".card-properties .lang-item")
                        .attrs["title"]
                        .lower(),
                        "is_foil": row.select_one("img .foil") is not None,
                        "condition": tag_strip(
                            row.select_one(".card-properties .js-card-quality-tooltip")
                        ),
                        "link": self._get_full_url(self._SEARCH.format(quote_plus(name))),
                        "price": Decimal(tag_strip(row.select_one(".catalog-rate-price"))),
                        "amount": amount,
                        "seller": Seller(
                            name=tag_strip(last_seller),
                            link=self._get_full_url(last_seller.attrs["href"]),
                            source="MTGTrade",
                        ),
                    }
                )
            except (AttributeError, TypeError) as e:
                print(e)
                continue

        return result

    async def parse_card_offers(self, card):
        result = []
        page = await self._get_offers_page(card)
        for table in page.select(".search-item"):
            for row in self.__parse_vertical_table(table):
                result.append(Offer(**row, currency_code=self.CURRENCY_CODE))
        return {card: result}
