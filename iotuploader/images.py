import datetime
import os
import sys
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from fastapi import Request, Depends, APIRouter, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from digitalmeter import reader

from .config import get_settings
from .models import UploadImage, SensorData
from .database import get_db
from .digitalmeter import meter_rect_path, meter_wifc_path
from .util import make_safe_path


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
            scan_digital_meter(db, img, device_id, t, n,
                               db_file.id, file_path, timestamp)
    except:
        logger.exception("images/upload digital_meter error")

    db.commit()

    return db_file.id

def scan_digital_meter(
        db,
        img,
        camera_id,
        sensor_type,
        sensor_name,
        db_id,
        file_path,
        timestamp):

    rect_path = meter_rect_path(camera_id)
    wifc_path = meter_wifc_path(camera_id)

    temp, humd = reader.reader(file_path, rect_path, wifc_path)
    logger.debug(f"save sensordata temp {temp} humd {humd}")

    data = SensorData(
        sensor_type = sensor_type,
        sensor_name = sensor_name,
        data_t0 = sensor_name,
        data_i0 = db_id,
        data_f0 = temp,
        data_i1 = humd,
        timestamp = timestamp,
    )
    db.add(data)

    # overlay image

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font=settings.font_path, size=settings.font_size)
    draw.text(
        (img.width/2, img.height-80),
        f"{temp}℃ {humd}% " + timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        fill="#ffffff",
        font=font,
        anchor="ms",
        stroke_width=3,
        stroke_fill="#444444"
    )

    overlay_dir = os.path.join(
            settings.data_dir,
            "overlay-images",
            make_safe_path(sensor_name),
            timestamp.strftime('%Y%m%d'))
    if not os.path.exists(overlay_dir):
        os.makedirs(overlay_dir);

    overlay_path = os.path.join(overlay_dir, os.path.basename(file_path))
    logger.debug(f"save overlay-image {overlay_path}")
    img.save(overlay_path, quality=80)

