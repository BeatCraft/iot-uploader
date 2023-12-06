import os
import os.path
import datetime
import io
import logging
from PIL import ImageDraw, ImageFont

from sqlalchemy import select

from digitalmeter import reader

from .config import get_settings
from .util import overlay_image_dir
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


def load_reading_setting(db, image):
    st = select(Image)\
            .where(Image.camera_id == image.camera_id)\
            .where(Image.sensor_name == image.sensor_name)\
            .order_by(Image.timestamp.desc())
    latest_image = db.scalars(st).first()

    if latest_image:
        st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
        reading_setting = db.scalar(st)

    if not reading_setting:
        reading_setting = ReadingSetting(
            camera_id = image.camera_id,
            sensor_name = image.sensor_name,
            rect = default_rect(),
            wifc = default_wifc(),
            not_read = False,
            labeled = False,
            range_x0 = 320,
            range_y0 = 240,
            range_x1 = 960,
            range_y1 = 720,
            timestamp = datetime.datetime.now()
        )
        db.add(reading_setting)
        db.flush()

    return reading_setting


def read_numbers(db, pil_img, image):
    reading_setting = load_reading_setting(db, image)
    image.reading_setting_id = reading_setting.id

    rect_file = io.StringIO(reading_setting.rect)
    wifc_file = io.StringIO(reading_setting.wifc)

    local_img_file = os.path.join(settings.data_dir, image.file)
    temp, humd = reader.reader(local_img_file, rect_file, wifc_file)
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

    # overlay image

    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype(font=settings.font_path, size=settings.font_size)
    draw.text(
        (pil_img.width/2, pil_img.height-80),
        f"{temp}℃ {humd}% " + image.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        fill="#ffffff",
        font=font,
        anchor="ms",
        stroke_width=3,
        stroke_fill="#444444"
    )

    overlay_dir = overlay_image_dir(image.sensor_name, image.timestamp)
    overlay_file = os.path.join(overlay_dir, image.name)

    local_overlay_dir = os.path.join(settings.data_dir, overlay_dir)
    if not os.path.exists(local_overlay_dir):
        os.makedirs(local_overlay_dir);

    local_overlay_file = os.path.join(local_overlay_dir, image.name)
    logger.debug(f"save overlay-image {overlay_file}")
    pil_img.save(local_overlay_file)

    image.overlay_file = overlay_file
    return image

