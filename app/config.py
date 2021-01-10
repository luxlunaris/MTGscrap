import os
import asyncio
from datetime import datetime
from pydantic import BaseSettings


class Config(BaseSettings):
    PROJECT_NAME = "MTGScrap"
    PARSERS = ["mtgsale", "mtgtrade", "angrybottlegnome"]
    SEMAPHORE_COUNT = 25


config = Config()