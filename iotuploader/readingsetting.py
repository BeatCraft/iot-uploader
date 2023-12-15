import logging
import datetime
import os
import csv
import io

from fastapi import Request, Depends, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func

from digitalmeter import reader

from .config import get_settings
from .database import get_db
from .models import Image, ReadingSetting, Sensor, SensorData
from .auth import auth
from . import th02

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

router = APIRouter()
templates = Jinja2Templates(directory=settings.templates_dir)


def js_version():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


@router.get("/tools/readingsetting", response_class=HTMLResponse)
async def get_readingsetting(
        req: Request,
        image_id: int,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)
    image_url = f"/tools/images/{image.id}"

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

        temp = "00.0"
        if data_temp:
            temp = "{:0=4.1f}".format(data_temp.data)
        ctx_setting["labeled_values"].append(temp[0])
        ctx_setting["labeled_values"].append(temp[1])
        ctx_setting["labeled_values"].append(temp[3])

        st = select(SensorData)\
                .where(SensorData.upload_id == image.upload_id)\
                .where(SensorData.sensor_type == "TH02H")
        data_humd = db.scalar(st)

        humd = "00"
        if data_humd:
            humd = "{:0=2}".format(data_humd.data)
        ctx_setting["labeled_values"].append(humd[0])
        ctx_setting["labeled_values"].append(humd[1])

    ctx = {
        "request": req,
        "title": "ReadingSetting",
        "image_id": image.id,
        "image_url": image_url,
        "setting": ctx_setting,
        "js_version": js_version(),
    }
    return templates.TemplateResponse("readingsetting.html", ctx)


@router.post("/tools/readingsetting")
async def post_readingsetting(
        req: Request,
        image_id: int,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    req_data = await req.json()

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    reading_setting = db.scalar(st)

    st = select(Sensor).where(Sensor.sensor_name == image.sensor_name)
    sensor = db.scalar(st)

    # ReadingSetting
    new_setting = ReadingSetting(
        camera_id = reading_setting.camera_id,
        sensor_name = reading_setting.sensor_name,
        rect = req_data["rect"],
        wifc = req_data.get("wifc"),
        not_read = req_data["not_read"],
        labeled = req_data["labeled"],
        range_x0 = req_data["range_x0"],
        range_y0 = req_data["range_y0"],
        range_x1 = req_data["range_x1"],
        range_y1 = req_data["range_y1"],
    )

    if not new_setting.wifc:
        if sensor.sensor_type == "TH02":
            new_setting.wifc = th02.default_wifc()

    db.add(new_setting)
    db.flush()

    # labeled data
    if new_setting.labeled:
        image.reading_setting_id = new_setting.id

        if sensor.sensor_type == "TH02":
            lvs = req_data["labeled_values"]
            temp = float(".".join(["".join(lvs[0:2]), lvs[2]]))
            humd = float("".join(lvs[3:5]))

            logger.info(f"image {image.id} labeled temp {temp} humd {humd}")
            th02.set_sensor_data(db, image, temp, humd)

        db.commit()
        return

    # re-reading
    st = select(Image)\
            .where(Image.reading_setting_id == image.reading_setting_id)\
            .where(Image.camera_id == image.camera_id)\
            .where(Image.sensor_name == image.sensor_name)\
            .where(Image.id >= image.id)
    update_images = db.scalars(st).all()

    for update_image in update_images:
        update_image.reading_setting_id = new_setting.id

        if new_setting.not_read:
            logger.info("delete sensor_data")
            st = delete(SensorData).where(SensorData.upload_id == update_image.upload_id)
            db.execute(st)
            continue

        img_path = os.path.join(settings.data_dir, update_image.file)
        rect_file = io.StringIO(new_setting.rect)
        wifc_file = io.StringIO(new_setting.wifc)

        if sensor.sensor_type == "TH02":
            temp, humd = reader.reader(img_path, rect_file, wifc_file)
            logger.info(f"image {update_image.id} temp {temp} humd {humd}")

            th02.set_sensor_data(db, update_image, temp, humd)

    db.commit()
    return ""


@router.get("/tools/readingsetting/test")
async def get_readingsetting_test(
    req: Request,
    image_id: int,
    username: str = Depends(auth),
    db: Session = Depends(get_db)):

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)

    file_path = os.path.join(settings.data_dir, image.file)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    reading_setting = db.scalar(st)

    st = select(Sensor).where(Sensor.sensor_name == image.sensor_name)
    sensor = db.scalar(st)

    if sensor.sensor_type == "TH02":
        rect_file = io.StringIO(reading_setting.rect)
        wifc_file = io.StringIO(reading_setting.wifc)

        temp, humd = reader.reader(file_path, rect_file, wifc_file)
        return f"temp:{temp} humd:{humd}"

    elif sensor.sensor_type == "GS01":
        return "not implemented"

    else:
        return f"Unknown sensor {sensor.sensor_type}"


@router.get("/tools/readingsetting/rect.csv")
async def get_readingsetting_rect_csv(
        req: Request,
        image_id: int,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    reading_setting = db.scalar(st)

    return StreamingResponse(
        content = io.StringIO(reading_setting.rect),
        headers={"Content-Disposition": f'attachment; filename="rect.csv"'},
        media_type="text/csv",
    )


@router.get("/tools/readingsetting/wi-fc.csv")
async def get_readingsetting_wifc_csv(
        req: Request,
        image_id: int,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    reading_setting = db.scalar(st)

    return StreamingResponse(
        content = io.StringIO(reading_setting.wifc),
        headers={"Content-Disposition": f'attachment; filename="wi-fc.csv"'},
        media_type="text/csv",
    )



