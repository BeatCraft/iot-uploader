import re
import sys
import os

from .config import get_settings

settings = get_settings()


def make_safe_path(orig):
    return re.sub(r'[^0-9,a-z,A-Z,-]', '_', orig)


def image_dir(camera_id, timestamp):
    return os.path.join(
            settings.data_dir,
            "images",
            make_safe_path(camera_id),
            timestamp.strftime('%Y%m%d')
    )


"""
def image_path(camera_id, timestamp, image_id, suffix):
    img_dir = image_dir(camera_id, timestamp)
    file_name = timestamp.strftime('%Y%m%d_%H%M%S%f_') + str(image_id) + suffix
    return os.path.join(img_dir, file_name)
"""


if __name__ == "__main__":
    print(sys.argv[1])
    print(make_safe_path(sys.argv[1]))

