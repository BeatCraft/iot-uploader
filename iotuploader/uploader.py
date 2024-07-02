import logging
import os
import os.path
import datetime
import csv
import io

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
import PIL

from .config import get_settings
from .database import get_db
from .models import Upload, SensorData, Image, UploadCount
from .storage import get_storage
from .defs import DataType
from .sensors import load_sensor
from . import th02
from . import gs01
from . import ep

settings = get_settings()
settings.skip_image_upload = [s.strip() for s in settings.skip_image_upload.split(',')]
settings.skip_sensordata_upload = [s.strip() for s in settings.skip_sensordata_upload.split(',')]

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
    sensor_names = set()

    if settings.enable_raw_data:
        raw_file = storage.make_raw_data_path("sensordata", timestamp)
        logger.info(f"save raw_data {raw_file}")
        storage.save_data(raw_file, raw_data)

    if settings.fix_sensor_null_bug:
        if raw_data[0] == 0x0:
            raw_data = raw_data[1:]

    if settings.fix_sensor_last_null_bug:
        if raw_data[-1] == 0x0:
            raw_data = raw_data[:-1]

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

            if row[0] in settings.skip_sensordata_upload:
                logger.info(f"SKIP: upload_sensordata {row[0]}")
                if settings.enable_upload_counts:
                    sensor_names.add(row[0])
                continue

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

            if settings.enable_upload_counts:
                sensor_names.add(sensor_data.sensor_name)

        except:
            logger.exception(f"data error: {row}")

    if settings.enable_upload_counts:
        try:
            _update_upload_counts(db, list(sensor_names), timestamp)
        except:
            logger.exception(f"upload_count error")

    db.commit()
    return upload.id


@app.post('/upload/images/{camera_id}', status_code=201)
async def post_upload_images(
        req: Request,
        camera_id:str,
        n:str = None,
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()

    if n in settings.skip_image_upload:
        logger.info(f"SKIP: upload_image {n}")
        if settings.enable_upload_counts:
            try:
                _update_upload_counts(db, [n], timestamp)
                db.commit()
            except:
                logger.exception(f"upload_count error")
        return -1

    raw_data = await req.body()
    storage = get_storage()

    if settings.enable_raw_data:
        raw_file = storage.make_raw_data_path("image", timestamp)
        logger.info(f"save raw_data {raw_file}")
        storage.save_data(raw_file, raw_data)

    if settings.fix_sensor_null_bug:
        if raw_data[0] == 0x0:
            raw_data = raw_data[1:]

    if settings.fix_sensor_last_null_bug:
        if raw_data[-1] == 0x0:
            raw_data = raw_data[:-1]

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

    if settings.enable_reading_meter:
        try:
            sensor = load_sensor(db, n)
            if sensor and sensor.sensor_type == "TH02":
                # digital_meter (temp,humd)
                th02.read_numbers(db, pil_img, image)

            elif sensor and sensor.sensor_type == "GS01":
                # digital_meter (gas)
                gs01.read_numbers(db, pil_img, image)

        except:
            logger.exception("images/upload read_numbers error")

    if settings.enable_upload_counts:
        try:
            _update_upload_counts(db, [image.sensor_name], timestamp)
        except:
            logger.exception(f"upload_count error")

    db.commit()

    return upload.id


@app.get("/upload/healthcheck")
async def get_upload_healthcheck(req: Request):
    return ""


@app.post("/upload/healthcheck")
async def post_upload_healthcheck(req: Request):
    return ""


def _update_upload_counts(db, sensors, timestamp):
    date = timestamp.date()
    hour = timestamp.hour

    for sensor_name in sensors:
        logger.debug(f"update upload_count {sensor_name}")

        st = select(UploadCount)\
                .where(UploadCount.sensor_name == sensor_name)\
                .where(UploadCount.date == date)\
                .where(UploadCount.hour == hour)\
                .with_for_update()
        upload_count = db.scalar(st)

        if not upload_count:
            upload_count = UploadCount(
                sensor_name = sensor_name,
                date = date,
                hour = hour,
                count = 0
            )
            db.add(upload_count)

        upload_count.count += 1
        upload_count.timestamp = timestamp

