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
from .util import make_safe_path, image_dir, image_filename
from .defs import DataType
from .sensors import load_sensor
from . import th02
from . import ep

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.post("/upload/sensordata", status_code=201)
async def post_upload_sensordata(req: Request, db: Session = Depends(get_db)):
    timestamp = datetime.datetime.now()

    upload = Upload(
        remote_addr = req.client.host,
        data_type = int(DataType.SENSOR_DATA),
        timestamp = timestamp,
    )

    db.add(upload)
    db.flush()

    logger.info(f"upload sensordata {upload.id} {upload.remote_addr}")

    req_data = (await req.body()).decode()
    reader = csv.reader(io.StringIO(req_data))
    for row in reader:
        try:
            logger.debug(row)

            sensor = load_sensor(db, row[0])
            if not sensor:
                logger.error(f"unknown sensor {row[0]}")
                continue

            row_timestamp = row[3]
            if not row_timestamp:
                row_timestamp = timestamp

            data = SensorData(
                upload_id = upload.id,
                sensor_name = row[0],
                sensor_type = sensor.sensor_type,
                data = float(row[1]),
                note = row[2],
                timestamp = row_timestamp,
            )
            db.add(data)

            #if data.sensor_type in ["EP01", "EP02", "EP03"]:
            #    ep.calculate(db, data)

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

    req_data = await req.body()
    pil_img = PIL.Image.open(io.BytesIO(req_data))

    # image name

    suffix = ""
    if pil_img.format == "JPEG":
        suffix = ".jpg"
    elif pil_img.format == "PNG":
        suffix = ".png"

    img_name = image_filename(timestamp, image.id, suffix)

    # image file

    img_dir = image_dir(camera_id, timestamp)
    img_file = os.path.join(img_dir, img_name)

    local_img_dir = os.path.join(settings.data_dir, img_dir)
    if not os.path.exists(local_img_dir):
        os.makedirs(local_img_dir);

    local_img_file = os.path.join(local_img_dir, img_name)

    # save

    logger.debug(f"save image {img_file}")
    with open(local_img_file, 'wb') as out_file:
        out_file.write(req_data)

    image.name = img_name
    image.file = img_file

    # read sensordata

    sensor = load_sensor(db, n)

    try:
        if sensor and sensor.sensor_type == "TH02":
            # digital_meter (temp,humd)
            th02.read_numbers(db, pil_img, image)

        #elif sensor and sensor.sensor_type == "GS01":
        #    # digital_meter (gas)
        #    th02.read_numbers(db, pil_img, image)

    except:
        logger.exception("images/upload read_numbers error")

    db.commit()

    return upload.id

