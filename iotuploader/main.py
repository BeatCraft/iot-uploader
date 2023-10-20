from fastapi import FastAPI, Depends
import logging

from .config import Settings, get_settings

logger = logging.getLogger("gunicorn.error")

app = FastAPI()


@app.get("/")
def get_root(settings: Settings = Depends(get_settings)):
    return {
        "message": "hello world",
    }


