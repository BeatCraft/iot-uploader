import logging
import os
import os.path
import datetime
import csv
import io

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import UploadSensorData, SensorData, UploadImage

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.post("/upload/sensordata", status_code=200)
async def post_upload_sensordata(req: Request, db: Session = Depends(get_db)):
    timestamp = datetime.datetime.now()

    upload = UploadSensorData(
        remote_addr = req.client.host,
        timestamp = timestamp,
    )

    db.add(upload)
    db.flush()

    logger.debug(f"upload sensordata {upload.id} {upload.remote_addr}")

    req_data = (await req.body()).decode()
    reader = csv.reader(io.StringIO(req_data))
    for row in reader:
        try:
            logger.debug(row)

            row_timestamp = row[3]
            if not row_timestamp:
                row_timestamp = timestamp

            data = SensorData(
                upload_id = upload.id,
                sensor_type = row[0],
                sensor_name = row[1],
                data = float(row[2]),
                note = row[3],
                timestamp = row_timestamp,
            )
            db.add(data)

        except:
            logger.exception(f"parse error: {row}")

    db.commit()

    return upload.id


images_dir = os.path.join(settings.data_dir, "images")
app.mount("/static/images", StaticFiles(directory=images_dir), name="images")

overlay_dir = os.path.join(settings.data_dir, "overlay-images")
app.mount("/static/overlay-images", StaticFiles(directory=overlay_dir), name="overlay-images")

