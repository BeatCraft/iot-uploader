import logging
import re
import sys
import os

from .config import get_settings

settings = get_settings()
logger = logging.getLogger("gunicorn.error")


def make_safe_path(orig):
    return re.sub(r'[^0-9,a-z,A-Z,-]', '_', orig)


def image_dir(camera_id, timestamp):
    return os.path.join(
            "images",
            make_safe_path(camera_id),
            timestamp.strftime('%Y%m%d')
    )


def overlay_image_dir(sensor_name, timestamp):
    return os.path.join(
            "overlay-images",
            make_safe_path(sensor_name),
            timestamp.strftime('%Y%m%d')
    )


def image_filename(timestamp, image_id, suffix):
    return timestamp.strftime('%Y%m%d_%H%M%S%f_') + str(image_id) + suffix


def save_raw_data(data_type, timestamp, raw_data):
    try:
        raw_name = data_type + timestamp.strftime('_%Y%m%d_%H%M%S')
        logger.info(f"save_raw_data {raw_name}")

        raw_file = os.path.join(settings.data_dir, "raw-data", raw_name)
        with open(raw_file, "wb") as fp:
            fp.write(raw_data)
    except:
        logger.exception("save_raw_data error")


if __name__ == "__main__":
    print(sys.argv[1])
    print(make_safe_path(sys.argv[1]))

