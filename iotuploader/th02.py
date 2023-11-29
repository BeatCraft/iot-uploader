import os
import os.path
import csv
import shutil
import re
import logging
from PIL import ImageDraw, ImageFont

from digitalmeter import reader

from .config import get_settings
from .util import make_safe_path
from .models import SensorData

SENSOR_TYPE = "TH02"
ORIG_DIR = "digitalmeter"
RECT_CSV = "rect.csv"
RECT_CSV_TMP = "rect.csv.tmp"
WIFC_CSV = "wi-fc.csv"

logger = logging.getLogger("gunicorn.error")
settings = get_settings()


def setting_dir(camera_id):
    safe_id = make_safe_path(camera_id)
    _dir = os.path.join(settings.data_dir, "camera-settings", safe_id, SENSOR_TYPE)

    if not os.path.exists(_dir):
        os.makedirs(_dir)

        # copy rect.csv
        rect_path = os.path.join(_dir, RECT_CSV)
        rect_orig = os.path.join(ORIG_DIR, RECT_CSV)
        shutil.copyfile(rect_orig, rect_path)

        # copy wi-fc.csv
        wifc_path = os.path.join(_dir, WIFC_CSV)
        wifc_orig = os.path.join(ORIG_DIR, WIFC_CSV)
        shutil.copyfile(wifc_orig, wifc_path)

    return _dir


def rect_path(camera_id):
    return os.path.join(setting_dir(camera_id), RECT_CSV)


def wifc_path(camera_id):
    return os.path.join(setting_dir(camera_id), WIFC_CSV)


def load_rect(camera_id):
    rects = []

    path = rect_path(camera_id)
    with open(path) as fp:
        reader = csv.reader(fp)
        for row in reader:
            rects.append(list(row))

    return rects


def save_rect(camera_id, rects):
    tmp_path = os.path.join(setting_dir(camera_id), RECT_CSV_TMP)
    with open(tmp_path, "w") as fp:
        writer = csv.writer(fp)
        for rect in rects:
            writer.writerow(rect)

    out_path = rect_path(camera_id)
    shutil.copyfile(tmp_path, out_path)


def scan(db, pil_img, image):
    _rect_path = rect_path(image.camera_id)
    _wifc_path = wifc_path(image.camera_id)

    temp, humd = reader.reader(image.file, _rect_path, _wifc_path)
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

    overlay_dir = os.path.join(
            settings.data_dir,
            "overlay-images",
            make_safe_path(image.sensor_name),
            image.timestamp.strftime('%Y%m%d'))
    if not os.path.exists(overlay_dir):
        os.makedirs(overlay_dir);

    overlay_path = os.path.join(overlay_dir, image.name)
    logger.debug(f"save overlay-image {overlay_path}")
    pil_img.save(overlay_path)

    image.overlay_file = overlay_path
    return image


