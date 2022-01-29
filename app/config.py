from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""
    PROJECT_NAME = "MTGScrap"
    PARSERS = ["mtgsale", "mtgtrade", "angrybottlegnome"]
    SEMAPHORE_COUNT = 25


config = Config()
