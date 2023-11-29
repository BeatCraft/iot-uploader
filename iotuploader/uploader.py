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
from .util import make_safe_path, image_dir
from .defs import DataType
from . import th02

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.post("/upload/sensordata", status_code=200)
async def post_upload_sensordata(req: Request, db: Session = Depends(get_db)):
    timestamp = datetime.datetime.now()

    upload = Upload(
        remote_addr = req.client.host,
        data_type = DataType.SENSOR_DATA,
        timestamp = timestamp,
    )

    db.add(upload)
    db.flush()

    logger.debug(f"upload sensordata {upload.id} {upload.remote_addr}")

    req_data = (await req.body()).decode()
    reader = csv.reader(io.StringIO(req_data))
    for row in reader:
        try:
            logger.debug(row)

            row_timestamp = row[3]
            if not row_timestamp:
                row_timestamp = timestamp

            data = SensorData(
                upload_id = upload.id,
                sensor_type = row[0],
                sensor_name = row[1],
                data = float(row[2]),
                note = row[3],
                timestamp = row_timestamp,
            )
            db.add(data)

        except:
            logger.exception(f"parse error: {row}")

    db.commit()
    return upload.id


@app.post('/upload/images/{camera_id}')
async def post_upload_images(
        req: Request,
        camera_id:str,
        t:str = None,
        n:str = None,
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()

    upload = Upload(
        remote_addr = req.client.host,
        data_type = DataType.IMAGE,
        timestamp = timestamp,
    )

    db.add(upload)
    db.flush()

    logger.debug(f"upload image {upload.id} {upload.remote_addr}")

    image = Image(
        upload_id = upload.id,
        camera_id = camera_id,
        sensor_type = t,
        sensor_name = n,
        name = "",
        file = "",
        timestamp = timestamp,
    )
    db.add(image)
    db.flush()

    req_data = await req.body()
    pil_img = PIL.Image.open(io.BytesIO(req_data))

    # file_name

    suffix = ""
    if pil_img.format == "JPEG":
        suffix = ".jpg"
    elif pil_img.format == "PNG":
        suffix = ".png"

    file_name = timestamp.strftime('%Y%m%d_%H%M%S%f_')\
                + str(image.id)\
                + suffix

    # file_path

    img_dir = image_dir(camera_id, timestamp)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir);

    file_path = os.path.join(img_dir, file_name)

    # save

    logger.debug(f"save image {file_path}")
    with open(file_path, 'wb') as out_file:
        out_file.write(req_data)

    image.name = file_name
    image.file = file_path

    # scan sensordata

    try:
        if t and n and t == "TH02":
            # digital_meter (temp,humd)
            th02.scan(db, pil_img, image)
    except:
        logger.exception("images/upload scan error")

    db.commit()

    return image.id

