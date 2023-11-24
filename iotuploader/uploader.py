import logging
import os
import os.path
import datetime
import csv
import io

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from PIL import Image

from .config import get_settings
from .database import get_db
from .models import UploadSensorData, SensorData, UploadImage
from .util import make_safe_path, image_dir
from . import th02

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.post("/upload/sensordata", status_code=200)
async def post_upload_sensordata(req: Request, db: Session = Depends(get_db)):
    timestamp = datetime.datetime.now()

    upload = UploadSensorData(
        remote_addr = req.client.host,
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
async def images_upload(
        req: Request,
        camera_id:str = None,
        t:str = None,
        n:str = None,
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()

    upload_image = UploadImage(
        camera_id = camera_id,
        sensor_type = t,
        sensor_name = n,
        name = "",
        file = "",
        timestamp = timestamp,
    )
    db.add(upload_image)
    db.flush()

    req_data = await req.body()
    img = Image.open(io.BytesIO(req_data))

    # file_name

    suffix = ""
    if img.format == "JPEG":
        suffix = ".jpg"
    elif img.format == "PNG":
        suffix = ".png"

    file_name = timestamp.strftime('%Y%m%d_%H%M%S%f_')\
                + str(upload_image.id)\
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

    upload_image.name = file_name
    upload_image.file = file_path

    # scan sensordata

    try:
        if t and n and t == "TH02":
            # digital_meter (temp,humd)
            th02.scan(db, img, upload_image)
    except:
        logger.exception("images/upload scan error")

    db.commit()

    return upload_image.id

