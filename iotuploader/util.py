import re
import sys
import os


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


if __name__ == "__main__":
    print(sys.argv[1])
    print(make_safe_path(sys.argv[1]))

