import logging
import os
import os.path

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from . import sensordata
from . import images

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/tools/test", status_code=200)
async def get_test():
    return "tools test"

