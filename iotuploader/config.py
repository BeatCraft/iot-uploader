from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    test_number: int = 32

