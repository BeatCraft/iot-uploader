import logging
import datetime
import csv
import io

from fastapi import Request, Depends, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from .config import get_settings
from .database import get_db
from .models import Image, ReadingSetting, Sensor, SensorData
from .auth import auth

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

router = APIRouter()
templates = Jinja2Templates(directory=settings.templates_dir)


def js_version():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


@router.get("/tools/readingsetting", response_class=HTMLResponse)
async def get_readingsetting(
        req: Request,
        camera_id: str,
        sensor_name: str,
        image_id: int,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)
    image_url = f"/tools/static/{image.file}"

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    rs = db.scalar(st)

    ctx_setting = {
        "rects": [],
        "not_read": rs.not_read,
        "labeled": rs.labeled,
        "labeled_values": [],
        "range_x0": rs.range_x0,
        "range_y0": rs.range_y0,
        "range_x1": rs.range_x1,
        "range_y1": rs.range_y1,
    }

    for row in csv.reader(io.StringIO(rs.rect)):
        ctx_setting["rects"].append(row)

    st = select(Sensor).where(Sensor.sensor_name == image.sensor_name)
    sensor = db.scalar(st)

    if sensor.sensor_type == "TH02":
        st = select(SensorData)\
                .where(SensorData.upload_id == image.upload_id)\
                .where(SensorData.sensor_type == "TH02T")
        data_temp = db.scalar(st)
        temp = "{:0=4.1f}".format(data_temp.data)
        ctx_setting["labeled_values"].append(temp[0])
        ctx_setting["labeled_values"].append(temp[1])
        ctx_setting["labeled_values"].append(temp[3])

        st = select(SensorData)\
                .where(SensorData.upload_id == image.upload_id)\
                .where(SensorData.sensor_type == "TH02H")
        data_humd = db.scalar(st)
        humd = "{:0=2}".format(data_humd.data)
        ctx_setting["labeled_values"].append(humd[0])
        ctx_setting["labeled_values"].append(humd[1])

    ctx = {
        "request": req,
        "title": "ReadingSetting",
        "image_url": image_url,
        "setting": ctx_setting,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("readingsetting.html", ctx)


@router.post("/tools/readingsetting")
async def post_readingsetting(
        req: Request,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    req_data = await req.json()

    sensor_type = camera_meter_map[device_id]
    wifc = ""
    setting_id = None

    upload_image = db.query(UploadImage)\
            .filter(UploadImage.id == image_id)\
            .first()

    reading_image = db.query(ReadingImage)\
            .filter(ReadingImage.upload_image_id == image_id)\
            .first()

    if reading_image:
        setting = db.query(ReadingSetting)\
                .filter(ReadingSetting.id == reading_image.reading_setting_id)\
                .first()
        wifc = setting.wifc
        setting_id = setting.id

    else:
        reading_image = ReadingImage(
            upload_image_id = upload_image.id,
            sensor_type = sensor_type,
            reading_setting_id = None,
        )
        db.add(reading_image)
        db.flush()

    # ReadingSetting
    new_setting = ReadingSetting(
        camera_id = device_id,
        sensor_type = sensor_type,
        rect = req_data["rect"],
        wifc = req_data.get("wifc"),
    )

    if not new_setting.wifc:
        new_setting.wifc = default_wifc()

    db.add(new_setting)
    db.flush()

    # ReadingSetting2
    new_setting2 = ReadingSetting2(
        id = new_setting.id,
        not_read = req_data["not_read"],
        labeled = req_data["labeled"],
    )
    db.add(new_setting2)
    db.flush()

    # labeled data
    if new_setting2.labeled:
        reading_image.reading_setting_id = new_setting.id

        set_sensor_data(db, sensor_type, upload_image, req_data["temp"], req_data["humd"], reading_image)

        db.commit()
        return

    update_images = db.query(ReadingImage)\
            .filter(ReadingImage.reading_setting_id == setting_id)\
            .filter(ReadingImage.sensor_type == sensor_type)\
            .filter(ReadingImage.timestamp >= upload_image.timestamp)

    for update_image in update_images:
        update_image.reading_setting_id = new_setting.id

        if new_setting2.not_read:
            logger.info("DELETE")
            db.query(SensorData)\
                    .filter(SensorData.data_i0 == update_image.upload_image_id)\
                    .delete()
            continue

        target_image = db.query(UploadImage)\
                .filter(UploadImage.id == update_image.upload_image_id)\
                .first()

        img_path = os.path.join(UPLOAD_FOLDER, target_image.name)
        rect_file = io.StringIO(new_setting.rect)
        wifc_file = io.StringIO(new_setting.wifc)

        temp, humd = reader.reader(img_path, rect_file, wifc_file)
        logger.info(f"image {upload_image.id} temp {temp} humd {humd}")

        set_sensor_data(db, sensor_type, target_image, temp, humd, update_image)

    db.commit()





    return ""

