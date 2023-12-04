import logging
import os
import os.path
import math
import datetime
import io

from typing import Optional
from fastapi import FastAPI, Depends, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from .config import get_settings
from .database import get_db
from .models import Sensor, SensorData
from .sensors import import_sensors_csv

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory=settings.templates_dir)

images_dir = os.path.join(settings.data_dir, "images")
app.mount("/tools/static/images", StaticFiles(directory=images_dir), name="images")

overlay_dir = os.path.join(settings.data_dir, "overlay-images")
app.mount("/tools/static/overlay-images", StaticFiles(directory=overlay_dir), name="overlay-images")


@app.get("/tools/test", status_code=200)
async def get_test():
    return "tools test"


@app.get("/tools/", response_class=HTMLResponse)
async def get_index(req: Request):
    ctx = {
        "request": req,
        "title": "iot-uploader-tools",
    }
    return templates.TemplateResponse("index.html", ctx)


@app.get("/tools/sensors", response_class=HTMLResponse)
async def get_sensors(
        req: Request,
        page: int = 1,
        size: int = 20,
        db: Session = Depends(get_db)):

    count = db.scalar(select(func.count("*")).select_from(Sensor))
    total_page = math.ceil(count / size)

    st = select(Sensor)\
            .order_by(Sensor.id.desc())\
            .offset((page-1) * size)\
            .limit(size)
    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "Sensors",
        "sensors": data,
        "page": page,
        "total_page": total_page,
    }
    return templates.TemplateResponse("sensors.html", ctx)


@app.post("/tools/sensors", response_class=HTMLResponse)
async def post_sensors(
        req: Request,
        file: UploadFile = File(None),
        db: Session = Depends(get_db)):

    form = await req.form()
    upload_file = form["file"]
    upload_io = io.StringIO((await upload_file.read()).decode())

    if upload_file:
        logger.debug(upload_file.filename)
        import_sensors_csv(db, upload_io)

    return await get_sensors(req, 1, 20, db)


@app.get("/tools/sensordata", response_class=HTMLResponse)
async def get_sensordata(
        req: Request,
        page: int = 1,
        size: int = 20,
        db: Session = Depends(get_db)):

    count = db.scalar(select(func.count("*")).select_from(SensorData))
    total_page = math.ceil(count / size)

    st = select(SensorData)\
            .order_by(SensorData.id.desc())\
            .offset((page-1) * size)\
            .limit(size)
    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "SensorData",
        "sensor_data": data,
        "page": page,
        "total_page": total_page,
    }
    return templates.TemplateResponse("sensordata.html", ctx)

