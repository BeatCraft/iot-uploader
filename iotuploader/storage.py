import logging
import re
import os

from .config import get_settings
from .models import Image

settings = get_settings()
logger = logging.getLogger("gunicorn.error")


def get_storage():
    if settings.enable_s3_storage:
        return S3Storage()
    else:
        return LocalStorage()


class Storage:
    def make_safe_path(self, orig):
        return re.sub(r'[^0-9,a-z,A-Z,-]', '_', orig)

    def make_image_filename(self, image: Image, suffix):
        return image.timestamp.strftime('%Y%m%d_%H%M%S%f_') + str(image.id) + suffix

    def make_image_path(self, image: Image):
        return os.path.join(
            "images",
            self.make_safe_path(image.camera_id),
            image.timestamp.strftime('%Y%m%d'),
            image.name
        )

    def make_overlay_image_path(self, image: Image):
        return os.path.join(
            "overlay-images",
            self.make_safe_path(image.sensor_name),
            image.timestamp.strftime('%Y%m%d'),
            image.name
        )

    def make_raw_data_path(self, data_type: str, timestamp):
        return os.path.join(
            "raw-data",
            timestamp.strftime('%Y%m%d_%H%M%S_') + data_type
        )

    def save_data(self, path, data):
        pass

    def load_data(self, path):
        pass

    def list_files(self, path):
        pass


class LocalStorage(Storage):
    def save_data(self, path, data):
        logger.debug(f"save local {path}")

        local_path = os.path.join(settings.data_dir, path)
        local_dir = os.path.dirname(local_path)

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        with open(local_path, "wb") as fp:
            fp.write(data)

    def load_data(self, path):
        logger.debug(f"load local {path}")

        local_path = os.path.join(settings.data_dir, path)
        with open(local_path, "rb") as fp:
            return fp.read()

    def list_files(self, path):
        logger.debug(f"list local {path}")

        data_dir = os.path.join(settings.data_dir, path)
        return sorted(os.listdir(data_dir), reverse=True)


if settings.enable_s3_storage:
    import boto3

class S3Storage(Storage):
    def save_data(self, path, data):
        logger.debug(f"save s3 {path}")
        bucket = boto3.resource("s3").Bucket("s11ah-uploads")
        bucket.Object(path).put(Body=data)

    def load_data(self, path):
        logger.debug(f"load s3 {path}")
        bucket = boto3.resource("s3").Bucket("s11ah-uploads")
        return bucket.Object(path).get()["Body"].read()

    def list_files(self, path):
        logger.debug(f"list s3 {path}")

        prefix = f"{path}/"

        bucket = boto3.resource("s3").Bucket("s11ah-uploads")
        objects = bucket.objects.filter(Prefix=prefix)

        keys = []
        for obj in objects:
            if obj.key == prefix:
                continue
            keys.append(obj.key.replace(prefix, ""))

        return sorted(keys, reverse=True)

