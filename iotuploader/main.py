from fastapi import FastAPI, Depends
import logging

from .config import Settings, get_settings
from . import sensordata
from . import images

logger = logging.getLogger("gunicorn.error")

app = FastAPI()
app.include_router(sensordata.router)
app.include_router(images.router)


