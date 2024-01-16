import logging
from sqlalchemy import select, delete, func

from .models import UploadCount

logger = logging.getLogger("gunicorn.error")

def add_upload_counts(db, count_data):
    for data in count_data.values():
        logger.debug(f"add_upload_count {data['sensor_name']} {data['count']}")

        st = select(UploadCount)\
                .where(
                    UploadCount.sensor_name == data["sensor_name"],
                    UploadCount.date == data["date"],
                    UploadCount.hour == data["hour"]
                )\
                .with_for_update()
        upload_count = db.scalar(st)

        if not upload_count:
            upload_count = UploadCount(
                sensor_name = data["sensor_name"],
                date = data["date"],
                hour = data["hour"],
                count = 0
            )
            db.add(upload_count)

        upload_count.count += data["count"]
        upload_count.timestamp = data["timestamp"]

