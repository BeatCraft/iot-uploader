import os
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from iotuploader.uploader import app
from iotuploader.models import Upload, SensorData, Image
from iotuploader.util import image_dir, image_path

client = TestClient(app)

def test_upload_sensordata(db):
    req_data = "EP01,ep1-test,11.1,,\nEP01,ep1-test,22.2,,"
    res = client.post("/upload/sensordata", content=req_data)
    assert res.status_code == 201
    upload_id = int(res.text)

    st = select(SensorData).where(SensorData.upload_id == upload_id)
    datas = db.scalars(st).all()
    assert len(datas) == 2
    assert datas[0].sensor_type == "EP01"
    assert datas[0].sensor_name == "ep1-test"


def test_upload_image(db, settings):
    camera_id = f"test-{uuid.uuid4()}"

    with open("tests/meter.jpg", "rb") as fp:
        img_data = fp.read()

    # post
    res = client.post(f"/upload/images/{camera_id}", content=img_data)
    assert res.status_code == 201
    upload_id = int(res.text)

    st = select(Image).where(Image.upload_id == upload_id)
    data = db.scalar(st)

    img_file = os.path.join(image_dir(camera_id, data.timestamp), data.name)
    with open(img_file, "rb") as fp:
        saved_img_data = fp.read()

    assert saved_img_data == img_data


def test_upload_digital_meter(db):
    with open("tests/meter.jpg", "rb") as fp:
        img_data = fp.read()

    res = client.post("/upload/images/testcamera02?t=TH02&n=testmeter02", content=img_data)
    assert res.status_code == 201
    upload_id = int(res.text)


