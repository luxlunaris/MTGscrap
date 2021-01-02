import argparse
import asyncio
import importlib
import os
from pprint import pprint
from time import time

PARSERS = [
    'mtgsale',
    'mtgtrade'
]

CARDS_PATH = os.path.join(os.path.dirname(__file__), 'cards.txt')


def create_argparser():
    parser = argparse.ArgumentParser(description='Initiate MTGscrap')
    parser.add_argument(
        '--html',
        action='store_true',
        help='write search result to HTML report file, default=False'
    )
    return parser


if __name__ == '__main__':
    parser = create_argparser()
    args = parser.parse_args()
    
    with open(CARDS_PATH, 'r') as file:
        cards = file.read().splitlines()
    
    loop = asyncio.get_event_loop()

    try:
        result = {}
        for parser in PARSERS:
            parser = importlib.import_module(f'parsers.{parser}.parser').Parser()
            offers = loop.run_until_complete(parser.parse_offers(cards))
            
            for card in offers:
                if card in result:
                    result[card] += offers[card]
                else:
                    result[card] = offers[card]
    finally:
        loop.close()
        for card in result:
            result[card].sort(key=lambda x:x.price)
    
    if args.html:
        import jinja2
        template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.join(os.path.dirname(__file__), 'reports')
        )
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('search.html')
        output = template.render(offers=result)
        
        output_file_name = os.path.join(
            os.path.dirname(__file__),
            f'report_MTGscrap_{int(time())}.html'
        )
        with open(output_file_name,'w') as file:
            file.write(output)
        print(f'Result: {os.path.abspath(output_file_name)}')
    else:
        for card in result:
            for offer in card:
                pprint(offer.__dict__)
