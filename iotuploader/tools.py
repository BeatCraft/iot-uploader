import logging
import os
import os.path
import math
import datetime
import io
import secrets

from typing import Optional
from fastapi import FastAPI, Depends, Request, File, UploadFile, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
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


REALM = "Tools"
security = HTTPBasic(realm=REALM)

def auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.tools_user)
    correct_password = secrets.compare_digest(credentials.password, settings.tools_pass)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth error",
            headers={"WWW-Authenticate": f"Basic realm={REALM}"}
        )

    return credentials.username


@app.get("/tools/", response_class=HTMLResponse)
async def get_index(req: Request, username: str = Depends(auth)):
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
        sensor_type: str = None,
        sensor_name: str = None,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st_count = select(func.count("*")).select_from(Sensor)

    st = select(Sensor)\
            .order_by(Sensor.id.desc())\
            .offset((page-1) * size)\
            .limit(size)

    if sensor_name is not None:
        st_count = st_count.where(Sensor.sensor_name == sensor_name)
        st = st.where(Sensor.sensor_name == sensor_name)

    if sensor_type is not None:
        st_count = st_count.where(Sensor.sensor_type == sensor_type)
        st = st.where(Sensor.sensor_type == sensor_type)

    count = db.scalar(st_count)
    total_page = math.ceil(count / size)

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
        page: int = 1,
        size: int = 20,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    form = await req.form()
    upload_file = form["file"]
    upload_io = io.StringIO((await upload_file.read()).decode())

    if upload_file:
        logger.debug(upload_file.filename)
        import_sensors_csv(db, upload_io)

    return await get_sensors(req, page, size, db)


@app.get("/tools/sensordata", response_class=HTMLResponse)
async def get_sensordata(
        req: Request,
        page: int = 1,
        size: int = 20,
        sensor_name: str = None,
        sensor_type: str = None,
        note: str = None,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    #count = db.scalar(select(func.count("*")).select_from(SensorData))
    #total_page = math.ceil(count / size)

    st_count = select(func.count("*")).select_from(SensorData)

    st = select(SensorData)\
            .order_by(SensorData.id.desc())\
            .offset((page-1) * size)\
            .limit(size)

    if sensor_name is not None:
        st_count = st_count.where(SensorData.sensor_name == sensor_name)
        st = st.where(SensorData.sensor_name == sensor_name)

    if sensor_type is not None:
        st_count = st_count.where(SensorData.sensor_type == sensor_type)
        st = st.where(SensorData.sensor_type == sensor_type)

    if note is not None:
        st_count = st_count.where(SensorData.note == note)
        st = st.where(SensorData.note == note)

    count = db.scalar(st_count)
    total_page = math.ceil(count / size)

    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "SensorData",
        "sensor_data": data,
        "page": page,
        "total_page": total_page,
    }
    return templates.TemplateResponse("sensordata.html", ctx)

