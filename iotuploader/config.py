from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = ""


@lru_cache()
def get_settings():
    return Settings()

