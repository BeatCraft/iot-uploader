import logging
import os
import os.path

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory=settings.templates_dir)

images_dir = os.path.join(settings.data_dir, "images")
app.mount("/static/images", StaticFiles(directory=images_dir), name="images")

overlay_dir = os.path.join(settings.data_dir, "overlay-images")
app.mount("/static/overlay-images", StaticFiles(directory=overlay_dir), name="overlay-images")


@app.get("/tools/test", status_code=200)
async def get_test():
    return "tools test"


