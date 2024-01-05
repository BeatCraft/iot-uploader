import logging
import os
import os.path
import datetime
import csv
import io

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import PIL

from .config import get_settings
from .database import get_db
from .models import Upload, SensorData, Image
from .storage import get_storage
from .defs import DataType
from .sensors import load_sensor
from . import th02
from . import gs01
from . import ep

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.post("/upload/sensordata", status_code=201)
async def post_upload_sensordata(
        req: Request,
        data_format: str = "hex",
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()
    raw_data = await req.body()
    storage = get_storage()

    if settings.enable_raw_data:
        raw_file = storage.make_raw_data_path("sensordata", timestamp)
        logger.info(f"save raw_data {raw_file}")
        storage.save_data(raw_file, raw_data)

    if settings.fix_sensor_null_bug:
        if raw_data[0] == 0x0:
            raw_data = raw_data[1:]

    upload = Upload(
        remote_addr = req.client.host,
        data_type = int(DataType.SENSOR_DATA),
        timestamp = timestamp,
    )

    db.add(upload)
    db.flush()

    logger.info(f"upload sensordata {upload.id} {upload.remote_addr}")

    req_data = raw_data.decode()
    reader = csv.reader(io.StringIO(req_data))
    for row in reader:
        try:
            logger.debug(row)

            sensor = load_sensor(db, row[0])
            if not sensor:
                logger.error(f"unknown sensor {row[0]}")
                continue

            data = 0
            if data_format == "hex":
                data = int(row[1], 16)
            elif data_format == "int":
                data = int(row[1], 0)
            elif data_format == "float":
                data = float(row[1])

            row_timestamp = row[3]
            if not row_timestamp:
                row_timestamp = timestamp

            sensor_data = SensorData(
                upload_id = upload.id,
                sensor_name = row[0],
                sensor_type = sensor.sensor_type,
                data = data,
                note = row[2],
                timestamp = row_timestamp,
            )
            db.add(sensor_data)

            if sensor_data.sensor_type in ["EP01", "EP02", "EP03"]:
                ep.calculate(db, sensor_data)

        except:
            logger.exception(f"parse error: {row}")

    db.commit()
    return upload.id


@app.post('/upload/images/{camera_id}', status_code=201)
async def post_upload_images(
        req: Request,
        camera_id:str,
        n:str = None,
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()
    raw_data = await req.body()
    storage = get_storage()

    if settings.enable_raw_data:
        raw_file = storage.make_raw_data_path("image", timestamp)
        logger.info(f"save raw_data {raw_file}")
        storage.save_data(raw_file, raw_data)

    if settings.fix_sensor_null_bug:
        if raw_data[0] == 0x0:
            raw_data = raw_data[1:]

    upload = Upload(
        remote_addr = req.client.host,
        data_type = int(DataType.IMAGE),
        timestamp = timestamp,
    )

    db.add(upload)
    db.flush()

    logger.info(f"upload image {upload.id} {upload.remote_addr}")

    image = Image(
        upload_id = upload.id,
        camera_id = camera_id,
        sensor_name = n,
        name = "",
        file = "",
        timestamp = timestamp,
    )
    db.add(image)
    db.flush()

    pil_img = PIL.Image.open(io.BytesIO(raw_data))

    # image file

    suffix = ""
    if pil_img.format == "JPEG":
        suffix = ".jpg"
    elif pil_img.format == "PNG":
        suffix = ".png"

    image.name = storage.make_image_filename(image, suffix)
    image.file = storage.make_image_path(image)

    # save

    logger.debug(f"save image {image.file}")
    storage.save_data(image.file, raw_data)

    # read sensordata

    sensor = load_sensor(db, n)

    try:
        if sensor and sensor.sensor_type == "TH02":
            # digital_meter (temp,humd)
            th02.read_numbers(db, pil_img, image)

        elif sensor and sensor.sensor_type == "GS01":
            # digital_meter (gas)
            gs01.read_numbers(db, pil_img, image)

    except:
        logger.exception("images/upload read_numbers error")

    db.commit()

    return upload.id


@app.get("/upload/healthcheck")
async def get_upload_healthcheck(req: Request):
    return ""


@app.post("/upload/healthcheck")
async def post_upload_healthcheck(req: Request):
    return ""

