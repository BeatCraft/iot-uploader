import os
import os.path
import datetime
import io
import logging
import datetime

from sqlalchemy import select
import PIL
from PIL import ImageFont

from digitalmeter import reader

from .config import get_settings
from .storage import get_storage
from .models import SensorData, ReadingSetting, Image

RECT_PATH = "/opt/iotuploader/src/iot-uploader/digitalmeter/rect.csv"
WIFC_PATH = "/opt/iotuploader/src/iot-uploader/digitalmeter/wi-fc.csv"

logger = logging.getLogger("gunicorn.error")
settings = get_settings()


def default_rect():
    with open(RECT_PATH) as fp:
        rect = fp.read()
    return rect


def default_wifc():
    with open(WIFC_PATH) as fp:
        wifc = fp.read()
    return wifc


def default_reading_setting(image):
    return ReadingSetting(
        camera_id = image.camera_id,
        sensor_name = image.sensor_name,
        rect = default_rect(),
        wifc = default_wifc(),
        not_read = False,
        labeled = False,
        range_x = 320,
        range_y = 240,
        range_w = 640,
        range_h = 480,
        rotation_angle = 0,
        num_rects = 5,
        max_brightness = 255,
        min_brightness = 0,
        max_contrast = 255,
        min_contrast = 0,
        timestamp = datetime.datetime.now()
    )


def load_reading_setting(db, image):
    st = select(Image)\
            .where(Image.id != image.id)\
            .where(Image.camera_id == image.camera_id)\
            .where(Image.sensor_name == image.sensor_name)\
            .order_by(Image.id.desc())
    latest_image = db.scalars(st).first()

    reading_setting = None

    if latest_image:
        logger.debug(f"latest_image {latest_image.id}")
        st = select(ReadingSetting).where(ReadingSetting.id == latest_image.reading_setting_id)
        reading_setting = db.scalar(st)

    if reading_setting and reading_setting.labeled:
        new_setting = ReadingSetting(
            camera_id = reading_setting.camera_id,
            sensor_name = reading_setting.sensor_name,
            rect = reading_setting.rect,
            wifc = reading_setting.wifc,
            not_read = reading_setting.not_read,
            labeled = False,
            range_x = reading_setting.range_x,
            range_y = reading_setting.range_y,
            range_w = reading_setting.range_w,
            range_h = reading_setting.range_h,
            rotation_angle = reading_setting.rotation_angle,
            num_rects = reading_setting.num_rects,
            max_brightness = reading_setting.max_brightness,
            min_brightness = reading_setting.min_brightness,
            max_contrast = reading_setting.max_contrast,
            min_contrast = reading_setting.min_contrast,
            timestamp = datetime.datetime.now()
        )
        db.add(new_setting)
        db.flush()

        reading_setting = new_setting

    if not reading_setting:
        reading_setting = default_reading_setting(image)
        db.add(reading_setting)
        db.flush()

    logger.debug(f"reading_setting {reading_setting.id}")
    return reading_setting


def save_overlay_image(db, pil_img, image, temp, humd):
    draw = PIL.ImageDraw.Draw(pil_img)
    font = PIL.ImageFont.truetype(font=settings.font_path, size=settings.font_size)
    draw.text(
        (pil_img.width/2, pil_img.height-80),
        f"{temp}℃ {humd}% " + image.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        fill="#ffffff",
        font=font,
        anchor="ms",
        stroke_width=3,
        stroke_fill="#444444"
    )

    storage = get_storage()
    image.overlay_file = storage.make_overlay_image_path(image)
    logger.debug(f"save overlay-image {image.overlay_file}")

    img_data = io.BytesIO()
    pil_img.save(img_data, format=pil_img.format)

    storage.save_data(image.overlay_file, img_data.getvalue())

    return image

def read_numbers(db, pil_img, image):
    reading_setting = load_reading_setting(db, image)
    image.reading_setting_id = reading_setting.id

    if reading_setting.not_read:
        logger.info(f"image {image.id} not_read")
        return

    rect_file = io.StringIO(reading_setting.rect)
    wifc_file = io.StringIO(reading_setting.wifc)

    temp, humd = reader.reader(pil_img, rect_file, wifc_file)
    logger.debug(f"save sensordata temp {temp} humd {humd}")

    data_temp = SensorData(
        upload_id = image.upload_id,
        sensor_type = "TH02T",
        sensor_name = image.sensor_name,
        data = temp,
        timestamp = image.timestamp,
    )
    db.add(data_temp)

    data_humd = SensorData(
        upload_id = image.upload_id,
        sensor_type = "TH02H",
        sensor_name = image.sensor_name,
        data = humd,
        timestamp = image.timestamp,
    )
    db.add(data_humd)

    save_overlay_image(db, pil_img, image, temp, humd)

    return image


def set_sensor_data(db, image, temp, humd):
    timestamp = datetime.datetime.now()

    # temp
    st = select(SensorData)\
            .where(SensorData.upload_id == image.upload_id)\
            .where(SensorData.sensor_type == "TH02T")
    data_temp = db.scalar(st)

    if data_temp:
        data_temp.data = temp
        data_temp.timestamp = timestamp
    else:
        data_temp = SensorData(
            upload_id = image.upload_id,
            sensor_name = image.sensor_name,
            sensor_type = "TH02T",
            data = temp,
            timestamp = timestamp,
        )
        db.add(data_temp)

    # humd
    st = select(SensorData)\
            .where(SensorData.upload_id == image.upload_id)\
            .where(SensorData.sensor_type == "TH02H")
    data_humd = db.scalar(st)

    if data_humd:
        data_humd.data = humd
        data_humd.timestamp = timestamp
    else:
        data_humd = SensorData(
            upload_id = image.upload_id,
            sensor_name = image.sensor_name,
            sensor_type = "TH02H",
            data = humd,
            timestamp = timestamp,
        )
        db.add(data_humd)

    db.flush()

    # overlay image
    image_path = os.path.join(settings.data_dir, image.file)
    with open(image_path, "rb") as fp:
        pil_img = PIL.Image.open(fp)
        save_overlay_image(db, pil_img, image, temp, humd)

    return data_temp, data_humd

