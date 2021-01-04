import argparse
import asyncio
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps

from .models import get_static, get_tasks_from_parsers, merge_list_dictionaries


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
    _ProactorBasePipeTransport.__del__
)


def create_argparser():
    parser = argparse.ArgumentParser(description="Initiate MTGscrap")
    parser.add_argument(
        "--html",
        action="store_true",
        help="write search result to HTML report file, default=False",
    )
    return parser


async def parse_offers():
    offers = await asyncio.gather(*get_tasks_from_parsers())
    result = merge_list_dictionaries(*offers)

    for card in result:
        result[card].sort(key=lambda x: x.price)

    return result


if __name__ == "__main__":
    parser = create_argparser()
    args = parser.parse_args()

    result = asyncio.run(parse_offers())

    if args.html:
        import jinja2
        import pathlib
        from time import time
        from os.path import dirname, abspath, join

        template_loader = jinja2.FileSystemLoader(searchpath=get_static("reports"))
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("search.html")
        output = template.render(offers=result)

        output_file_name = join(
            dirname(dirname(__file__)), f"report_MTGscrap_{int(time())}.html"
        )
        with open(output_file_name, "w") as file:
            file.write(output)

        print(f"Result: {abspath(output_file_name)}")
    else:
        from pprint import pprint

        for card in result:
            for offer in result[card]:
                pprint(offer.__dict__)
