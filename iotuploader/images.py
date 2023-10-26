import datetime
import os
import sys
import logging

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

    now = datetime.datetime.now()

    db_file = UploadImage(
        device_id = device_id,
        name = "",
        path = "",
        thumbnail_path = "",
        size = 0,
        timestamp = now,
    )
    db.add(db_file)
    db.flush()

    safe_id = make_safe_path(device_id)
    img_dir = os.path.join(settings.data_dir, "images", safe_id,  now.strftime('%Y%m%d'))
    if not os.path.exists(img_dir):
        os.makedirs(img_dir);

    file_name = now.strftime('%Y%m%d_%H%M%S%f_') + str(db_file.id)
    file_path = os.path.join(img_dir, file_name)
    
    with open(file_path, 'wb') as out_file:
        data = await req.body()
        data_len = len(data)
        out_file.write(data)

    logger.debug(f"save image {file_path} {data_len} bytes")

    os.utime(file_path);

    db_file.name = file_name
    db_file.path = f"/upload/{file_name}"
    db_file.size = data_len

    try:
        if t and n and t == "TH02":
            rect_path = meter_rect_path(device_id)
            wifc_path = meter_wifc_path(device_id)

            temp, humd = reader.reader(file_path, rect_path, wifc_path)
            logger.debug(f"save sensordata temp {temp} humd {humd}")

            data = SensorData(
                sensor_type = t,
                sensor_name = n,
                data_t0 = n,
                data_i0 = db_file.id,
                data_f0 = temp,
                data_i1 = humd,
                timestamp = now,
            )
            db.add(data)
    except:
        logger.exception("images/upload digital_meter error")

    db.commit()

    return db_file.id

