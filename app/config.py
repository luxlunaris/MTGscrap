import os
from datetime import datetime
from pydantic import BaseSettings


class Config(BaseSettings):
    PROJECT_NAME = "MTGScrap"
    PARSERS = ["mtgsale", "mtgtrade", "angrybottlegnome"]


config = Config()