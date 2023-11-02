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
from .util import make_safe_path
from . import th02


logger = logging.getLogger("gunicorn.error")

settings = get_settings()

router = APIRouter()
templates = Jinja2Templates(directory=settings.templates_dir)


@router.post('/images/upload/{device_id}')
async def images_upload(
        req: Request,
        device_id:str = None,
        t:str = None,
        n:str = None,
        db: Session = Depends(get_db)):

    timestamp = datetime.datetime.now()

    db_file = UploadImage(
        device_id = device_id,
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

    safe_id = make_safe_path(device_id)
    img_dir = os.path.join(settings.data_dir, "images", safe_id,  timestamp.strftime('%Y%m%d'))
    if not os.path.exists(img_dir):
        os.makedirs(img_dir);

    file_path = os.path.join(img_dir, file_name)

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
            th02.scan(db, img, device_id, t, n, db_file.id, file_path, timestamp)
    except:
        logger.exception("images/upload scan error")

    db.commit()

    return db_file.id

