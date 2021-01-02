import asyncio

from decimal import Decimal
from parsers.base import BaseParser, Offer, Seller

class Parser(BaseParser):
    _DOMAIN = 'https://mtgsale.ru'
    _SEARCH = '/home/search-results?Name={}'
    
    CURRENCY_CODE = 'RUB'

    def parse_vertical_table(self, table):
        result = []
        for row in table.select('.ctclass'):
            result.append(
                {
                    'card_name': row.select_one('a.tnamec').text,
                    'language': row.select_one('.lang i').attrs['title'],
                    'is_foil': row.select_one('.foil').text == 'Фойл',
                    'condition': row.select_one('.sost span').text,
                    'link': self._get_full_url(row.select_one('a.tnamec').attrs['href']),
                    'price': Decimal(row.select_one('.pprice').text.split()[0]),
                    'amount': int(row.select_one('.colvo').text.split()[0])
                }
            )
        return result

    async def _parse_card_offers(self, card):
        seller = Seller('MTGSale', self._DOMAIN)
        page = await self._get_offers_page(card)
        return [
            Offer(
                **row, 
                currency_code=self.CURRENCY_CODE, 
                seller=seller
            ) for row in self.parse_vertical_table(
                page.select_one('#taba')
            )
        ]
