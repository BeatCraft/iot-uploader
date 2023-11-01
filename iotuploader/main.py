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
app.include_router(sensordata.router)
app.include_router(images.router)

images_dir = os.path.join(settings.data_dir, "images")
app.mount("/static/images", StaticFiles(directory=images_dir), name="images")

overlay_dir = os.path.join(settings.data_dir, "overlay-images")
app.mount("/static/overlay-images", StaticFiles(directory=overlay_dir), name="overlay-images")

