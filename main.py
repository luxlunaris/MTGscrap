
import asyncio
import importlib
import os 

PARSERS = [
    'mtgsale'
]

CARDS_PATH = os.path.join(os.path.dirname(__file__), 'cards.txt')

if __name__ == '__main__':
    for parser in PARSERS:
        parser = importlib.import_module(f'parsers.{parser}.parser').Parser()
        loop = asyncio.get_event_loop()
        with open(CARDS_PATH, 'r') as file:
            cards = file.readlines()
        try:
            result = loop.run_until_complete(parser.parse_offers(cards))
            for offer in result:
                print(offer.to_json())
        finally:
            loop.close()
