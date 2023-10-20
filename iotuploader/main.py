from functools import lru_cache
from fastapi import FastAPI, Depends
import logging
from . import config

logger = logging.getLogger("gunicorn.error")

app = FastAPI()


@lru_cache()
def get_settings():
    return config.Settings()


@app.get("/")
def get_root(settings: config.Settings = Depends(get_settings)):
    logger.debug(type(settings.test_number))
    return {
        "message": "hello world",
        "test_number": settings.test_number,
    }


