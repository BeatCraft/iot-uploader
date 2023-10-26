import os
import os.path
import csv
import shutil
import re

from .config import get_settings
from .util import make_safe_path


ORIG_DIR = "digitalmeter"
RECT_CSV = "rect.csv"
RECT_CSV_TMP = "rect.csv.tmp"
WIFC_CSV = "wi-fc.csv"

settings = get_settings()


def meter_setting_dir(device_id):
    safe_id = make_safe_path(device_id)
    setting_dir = os.path.join(settings.data_dir, "digitalmeter", safe_id)

    if not os.path.exists(setting_dir):
        os.makedirs(setting_dir)

        # copy rect.csv
        rect_path = os.path.join(setting_dir, RECT_CSV)
        rect_orig = os.path.join(ORIG_DIR, RECT_CSV)
        shutil.copyfile(rect_orig, rect_path)

        # copy wi-fc.csv
        wifc_path = os.path.join(setting_dir, WIFC_CSV)
        wifc_orig = os.path.join(ORIG_DIR, WIFC_CSV)
        shutil.copyfile(wifc_orig, wifc_path)

    return setting_dir


def meter_rect_path(device_id):
    return os.path.join(meter_setting_dir(device_id), RECT_CSV)


def meter_wifc_path(device_id):
    return os.path.join(meter_setting_dir(device_id), WIFC_CSV)


def load_meter_rect(device_id):
    rects = []

    path = meter_rect_path(device_id)
    with open(path) as fp:
        reader = csv.reader(fp)
        for row in reader:
            rects.append(list(row))

    return rects


def save_meter_rect(device_id, rects):
    tmp_path = os.path.join(meter_setting_dir(device_id), RECT_CSV_TMP)
    with open(tmp_path, "w") as fp:
        writer = csv.writer(fp)
        for rect in rects:
            writer.writerow(rect)

    out_path = meter_rect_path(device_id)
    shutil.copyfile(tmp_path, out_path)


