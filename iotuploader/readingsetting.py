import logging
import datetime
import os
import csv
import io
import math

from fastapi import Request, Depends, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func
import PIL

from .config import get_settings
from .database import get_db
from .models import Image, ReadingSetting, Sensor, SensorData
from .auth import auth
from .storage import get_storage
from . import th02
from . import gs01

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

    st = select(Sensor).where(Sensor.sensor_name == image.sensor_name)
    sensor = db.scalar(st)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    rs = db.scalar(st)
    if not rs:
        if sensor.sensor_type == "TH02":
            rs = th02.default_reading_setting(image)
        elif sensor.sensor_type == "GS01":
            rs = gs01.default_reading_setting(image)

    ctx_setting = {
        "rects": [],
        "not_read": rs.not_read,
        "labeled": rs.labeled,
        "labeled_values": [],
        "range_x": rs.range_x,
        "range_y": rs.range_y,
        "range_w": rs.range_w,
        "range_h": rs.range_h,
        "num_rects": rs.num_rects,
        "rotation_angle": rs.rotation_angle,
        "max_rects": 10,
    }

    for row in csv.reader(io.StringIO(rs.rect)):
        ctx_setting["rects"].append(row)

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

    elif sensor.sensor_type == "GS01":
        st = select(SensorData)\
                .where(SensorData.upload_id == image.upload_id)\
                .where(SensorData.sensor_type == "GS01")
        data_gas = db.scalar(st)

        gas = "0" * rs.num_rects
        if data_gas:
            data_bp = math.floor(data_gas.data)
            text_bp = str(data_bp).zfill(6)
            data_ap = data_gas.data - data_bp
            text_ap = "{:0=.2f}".format(data_ap)
            gas = (text_bp + text_ap[2:])[:rs.num_rects]
        for i in range(rs.num_rects):
            ctx_setting["labeled_values"].append(gas[i])

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

    storage = get_storage()
    req_data = await req.json()

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)

    st = select(Sensor).where(Sensor.sensor_name == image.sensor_name)
    sensor = db.scalar(st)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    reading_setting = db.scalar(st)
    if not reading_setting:
        if sensor.sensor_type == "TH02":
            reading_setting = th02.default_reading_setting(image)
        elif sensor.sensor_type == "GS01":
            reading_setting = gs01.default_reading_setting(image)

    # ReadingSetting
    new_setting = ReadingSetting(
        camera_id = reading_setting.camera_id,
        sensor_name = reading_setting.sensor_name,
        rect = req_data["rect"],
        wifc = req_data.get("wifc"),
        not_read = req_data["not_read"],
        labeled = req_data["labeled"],
        range_x = req_data["range_x"],
        range_y = req_data["range_y"],
        range_w = req_data["range_w"],
        range_h = req_data["range_h"],
        rotation_angle = float(req_data["rotation_angle"]),
        num_rects = req_data["num_rects"],
        max_brightness = 255,
        min_brightness = 0,
        max_contrast = 255,
        min_contrast = 0,
        timestamp = datetime.datetime.now()
    )

    if not new_setting.wifc:
        if sensor.sensor_type == "TH02":
            new_setting.wifc = th02.default_wifc()
        elif sensor.sensor_type == "GS01":
            new_setting.wifc = gs01.default_wifc()

    db.add(new_setting)
    db.commit()

    # labeled data
    if new_setting.labeled:
        image.reading_setting_id = new_setting.id

        if sensor.sensor_type == "TH02":
            img_data = storage.load_data(image.file)
            pil_img = PIL.Image.open(io.BytesIO(img_data))

            lvs = req_data["labeled_values"]
            temp = float(".".join(["".join(lvs[0:2]), lvs[2]]))
            humd = float("".join(lvs[3:5]))

            logger.info(f"image {image.id} labeled temp {temp} humd {humd}")
            th02.set_sensor_data(db, pil_img, image, temp, humd)

        elif sensor.sensor_type == "GS01":
            img_data = storage.load_data(image.file)
            pil_img = PIL.Image.open(io.BytesIO(img_data))

            lvs = req_data["labeled_values"]
            if len(lvs) > 6:
                lvs.insert(6, ".")
            vol = float(lvs)

            logger.info(f"image {image.id} labeled vol {vol}")
            gs01.set_sensor_data(db, pil_img, image, vol)

        db.commit()
        return

    # re-reading
    st = select(Image)\
            .where(Image.reading_setting_id == image.reading_setting_id)\
            .where(Image.camera_id == image.camera_id)\
            .where(Image.sensor_name == image.sensor_name)\
            .where(Image.id >= image.id)\
            .order_by(Image.id)\
            .limit(settings.re_reading_meter_limit)
    update_images = db.scalars(st)

    for update_image in update_images:
        update_image.reading_setting_id = new_setting.id

        if new_setting.not_read:
            logger.info("delete sensor_data")
            st = delete(SensorData).where(SensorData.upload_id == update_image.upload_id)
            db.execute(st)
            db.commit()
            continue

        img_data = storage.load_data(update_image.file)
        pil_img = PIL.Image.open(io.BytesIO(img_data))

        if sensor.sensor_type == "TH02":
            temp, humd = th02.read_numbers(db, pil_img, update_image, reading_setting=new_setting)
            logger.info(f"image {update_image.id} temp {temp} humd {humd}")

        elif sensor.sensor_type == "GS01":
            vol = gs01.read_numbers(db, pil_img, update_image, reading_setting=new_setting)
            logger.info(f"image {update_image.id} vol {vol}")

        db.commit()

    return ""


@router.get("/tools/readingsetting/test")
async def get_readingsetting_test(
        req: Request,
        image_id: int,
        username: str = Depends(auth),
        db: Session = Depends(get_db)):

    storage = get_storage()

    st = select(Image).where(Image.id == image_id)
    image = db.scalar(st)

    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    reading_setting = db.scalar(st)

    st = select(Sensor).where(Sensor.sensor_name == image.sensor_name)
    sensor = db.scalar(st)

    img_data = storage.load_data(image.file)
    pil_img = PIL.Image.open(io.BytesIO(img_data))

    if sensor.sensor_type == "TH02":
        temp, humd = th02.read_numbers(db, pil_img, image,
                                       reading_setting=reading_setting, save_data=False)
        return f"temp:{temp} humd:{humd}"

    elif sensor.sensor_type == "GS01":
        vol = gs01.read_numbers(db, pil_img, image,
                                reading_setting=reading_setting, save_data=False)
        return f"vol:{vol}"

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



