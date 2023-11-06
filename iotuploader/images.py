import datetime
import os
import sys
import logging
from io import BytesIO
from PIL import Image

from fastapi import Request, Depends, APIRouter, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import get_settings
from .models import UploadImage, SensorData
from .database import get_db
from .util import make_safe_path, image_dir, image_path
from . import th02


logger = logging.getLogger("gunicorn.error")

settings = get_settings()

router = APIRouter()
templates = Jinja2Templates(directory=settings.templates_dir)


@router.post('/images/upload/{camera_id}')
async def images_upload(
        req: Request,
        camera_id:str = None,
        t:str = None,
        n:str = None,
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()

    db_file = UploadImage(
        device_id = camera_id,
        name = "",
        path = "",
        thumbnail_path = "",
        size = 0,
        timestamp = timestamp,
    )
    db.add(db_file)
    db.flush()

    data = await req.body()
    data_len = len(data)
    img = Image.open(BytesIO(data))

    # file_name

    suffix = ""
    if img.format == "JPEG":
        suffix = ".jpg"
    elif img.format == "PNG":
        suffix = ".png"

    file_name = timestamp.strftime('%Y%m%d_%H%M%S%f_') + str(db_file.id) + suffix

    # file_path

    img_dir = image_dir(camera_id, timestamp)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir);

    file_path = image_path(camera_id, timestamp, db_file.id, suffix)

    # save

    logger.debug(f"save image {file_path} {data_len} bytes")
    with open(file_path, 'wb') as out_file:
        out_file.write(data)

    db_file.name = file_name
    db_file.path = f"/upload/{file_name}"
    db_file.size = data_len

    # scan sensordata

    try:
        if t and n and t == "TH02":
            # digital_meter (temp,humd)
            th02.scan(db, img, camera_id, t, n, db_file.id, file_path, timestamp)
    except:
        logger.exception("images/upload scan error")

    db.commit()

    return db_file.id

