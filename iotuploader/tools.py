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
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from .config import get_settings
from .database import get_db
from .models import Upload, Sensor, SensorData, Image, ElParameter
from .storage import get_storage
from .sensors import import_sensors_csv
from .auth import auth
from . import readingsetting

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory=settings.templates_dir)

app.mount("/tools/static", StaticFiles(directory=settings.static_dir), name="static")

app.include_router(readingsetting.router)


def js_version():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


@app.get("/tools/", response_class=HTMLResponse)
async def get_index(req: Request, username: str = Depends(auth)):
    ctx = {
        "request": req,
        "title": "iot-uploader-tools",
    }
    return templates.TemplateResponse("index.html", ctx)


@app.get("/tools/uploads", response_class=HTMLResponse)
async def get_uploads(
        req: Request,
        page: int = 1,
        size: int = 20,
        id: int = None,
        remote_addr: str = None,
        data_type: int = None,
        db: Session = Depends(get_db)):

    st_count = select(func.count("*")).select_from(Upload)

    st = select(Upload)\
            .order_by(Upload.id.desc())\
            .offset((page-1) * size)\
            .limit(size)

    if id is not None:
        st_count = st_count.where(Upload.id == id)
        st = st.where(Upload.id == id)

    if remote_addr is not None:
        st_count = st_count.where(Upload.remote_addr == remote_addr)
        st = st.where(Upload.remote_addr == remote_addr)

    if data_type is not None:
        st_count = st_count.where(Upload.data_type == data_type)
        st = st.where(Upload.data_type == data_type)

    count = db.scalar(st_count)
    total_page = math.ceil(count / size)

    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "Uploads",
        "uploads": data,
        "page": page,
        "total_page": total_page,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("uploads.html", ctx)


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
        "js_version": js_version(),
    }
    return templates.TemplateResponse("sensors.html", ctx)


@app.post("/tools/sensors")
async def post_sensors(
        req: Request,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    req_data = await req.json()
    sensors_csv = io.StringIO(req_data.get("sensors_csv"))
    import_sensors_csv(db, sensors_csv)
    return ""


@app.get("/tools/sensordata", response_class=HTMLResponse)
async def get_sensordata(
        req: Request,
        page: int = 1,
        size: int = 20,
        upload_id: int = None,
        sensor_name: str = None,
        sensor_type: str = None,
        note: str = None,
        timestamp: str = None,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st_count = select(func.count("*")).select_from(SensorData)

    st = select(SensorData)\
            .order_by(SensorData.id.desc())\
            .offset((page-1) * size)\
            .limit(size)

    if upload_id is not None:
        st_count = st_count.where(SensorData.upload_id == upload_id)
        st = st.where(SensorData.upload_id == upload_id)

    if sensor_name is not None:
        st_count = st_count.where(SensorData.sensor_name == sensor_name)
        st = st.where(SensorData.sensor_name == sensor_name)

    if sensor_type is not None:
        st_count = st_count.where(SensorData.sensor_type == sensor_type)
        st = st.where(SensorData.sensor_type == sensor_type)

    if note is not None:
        st_count = st_count.where(SensorData.note == note)
        st = st.where(SensorData.note == note)

    if timestamp is not None:
        st_count = st_count.where(SensorData.timestamp.like(f"{timestamp}%"))
        st = st.where(SensorData.timestamp.like(f"{timestamp}%"))

    count = db.scalar(st_count)
    total_page = math.ceil(count / size)

    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "SensorData",
        "sensor_data": data,
        "page": page,
        "total_page": total_page,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("sensordata.html", ctx)


@app.get("/tools/images", response_class=HTMLResponse)
async def get_images(
        req: Request,
        page: int = 1,
        size: int = 10,
        upload_id: int = None,
        camera_id: str = None,
        sensor_name: str = None,
        timestamp: str = None,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st_count = select(func.count("*")).select_from(Image)

    st = select(Image)\
            .order_by(Image.id.desc())\
            .offset((page-1) * size)\
            .limit(size)

    if upload_id is not None:
        st_count = st_count.where(Image.upload_id == upload_id)
        st = st.where(Image.upload_id == upload_id)

    if camera_id is not None:
        st_count = st_count.where(Image.camera_id == camera_id)
        st = st.where(Image.camera_id == camera_id)

    if sensor_name is not None:
        st_count = st_count.where(Image.sensor_name == sensor_name)
        st = st.where(Image.sensor_name == sensor_name)

    if timestamp is not None:
        st_count = st_count.where(Image.timestamp.like(f"{timestamp}%"))
        st = st.where(Image.timestamp.like(f"{timestamp}%"))

    count = db.scalar(st_count)
    total_page = math.ceil(count / size)

    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "Images",
        "images": data,
        "page": page,
        "total_page": total_page,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("images.html", ctx)


@app.get("/tools/images/{image_id}", response_class=StreamingResponse)
async def get_image_file(
        req: Request,
        image_id: int,
        overlay: int = 0,
        download: int = 0,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    storage = get_storage()
    image = db.scalar(select(Image).where(Image.id == image_id))

    if overlay:
        img_data = storage.load_data(image.overlay_file)
    else:
        img_data = storage.load_data(image.file)

    headers = {}
    if download:
        headers['Content-Disposition'] = 'attachment; filename=' + image.name

    return StreamingResponse(
        io.BytesIO(img_data),
        headers = headers,
    )


@app.get("/tools/elparameters", response_class=HTMLResponse)
async def get_elparameters(
        req: Request,
        page: int = 1,
        size: int = 20,
        sensor_name: str = None,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st_count = select(func.count("*")).select_from(ElParameter)

    st = select(ElParameter)\
            .order_by(ElParameter.id.desc())\
            .offset((page-1) * size)\
            .limit(size)

    if sensor_name is not None:
        st_count = st_count.where(ElParameter.sensor_name == sensor_name)
        st = st.where(ElParameter.sensor_name == sensor_name)

    count = db.scalar(st_count)
    total_page = math.ceil(count / size)

    data = db.scalars(st).all()

    ctx = {
        "request": req,
        "title": "ElParameters",
        "el_parameters": data,
        "page": page,
        "total_page": total_page,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("elparameters.html", ctx)


@app.get("/tools/rawdata", response_class=HTMLResponse)
async def get_rawdata(
        req: Request,
        page: int = 1,
        size: int = 20,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    storage = get_storage()
    all_files = storage.list_files("raw-data")

    count = len(all_files)
    total_page = math.ceil(count / size)

    offset = (page - 1) * size
    files = all_files[offset:offset + size]

    ctx = {
        "request": req,
        "title": "RawData",
        "files": files,
        "page": page,
        "total_page": total_page,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("rawdata.html", ctx)


@app.get("/tools/rawdata/{filename}", response_class=StreamingResponse)
async def get_rawdata_file(
        req: Request,
        filename: str,
        download: int = 0,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    storage = get_storage()

    path = os.path.join("raw-data", filename)
    raw_data = storage.load_data(path)

    headers = {}
    if download:
        headers['Content-Disposition'] = 'attachment; filename=' + filename

    return StreamingResponse(
        io.BytesIO(raw_data),
        headers = headers,
    )

