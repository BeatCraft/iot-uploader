from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = ""
    templates_dir: str = ""
    data_dir: str = ""


@lru_cache()
def get_settings():
    return Settings()

