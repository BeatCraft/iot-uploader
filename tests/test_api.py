import os
import uuid
import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from iotuploader.uploader import app
from iotuploader.models import Upload, SensorData, Image
from iotuploader.util import image_dir, image_path

client = TestClient(app)

def test_upload_sensordata(db):
    req_data = "EP01_TEST_01,11.1,,\nEP01_TEST_01,22.2,,2023-11-30T01:02:03"
    res = client.post("/upload/sensordata", content=req_data)
    assert res.status_code == 201
    upload_id = int(res.text)

    st = select(SensorData).where(SensorData.upload_id == upload_id)
    datas = db.scalars(st).all()
    assert len(datas) == 4

    assert datas[0].sensor_type == "EP01"
    assert datas[0].sensor_name == "EP01_TEST_01"
    assert datas[0].data == 11.1
    assert datas[0].timestamp != datetime.datetime.fromisoformat("2023-11-30T01:02:03")

    assert datas[1].sensor_type == "EP01C"
    assert datas[1].sensor_name == "EP01_TEST_01"
    assert datas[1].data == 11.1 * 2000 * 1000 * 0.8 * 1.0

    assert datas[2].sensor_type == "EP01"
    assert datas[2].sensor_name == "EP01_TEST_01"
    assert datas[2].data == 22.2
    assert datas[2].timestamp == datetime.datetime.fromisoformat("2023-11-30T01:02:03")

    assert datas[3].sensor_type == "EP01C"
    assert datas[3].sensor_name == "EP01_TEST_01"
    assert datas[3].data == 22.2 * 2000 * 1000 * 0.8 * 1.0


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
    camera_id = f"test-{uuid.uuid4()}"

    with open("tests/meter.jpg", "rb") as fp:
        img_data = fp.read()

    res = client.post(f"/upload/images/{camera_id}?n=TH02_TEST_21", content=img_data)
    assert res.status_code == 201
    upload_id = int(res.text)

    st = select(SensorData)\
            .where(SensorData.upload_id == upload_id)\
            .where(SensorData.sensor_type == "TH02T")
    data_temp = db.scalar(st)
    assert data_temp.sensor_name == "TH02_TEST_21"
    assert data_temp.sensor_type == "TH02T"

    st = select(SensorData)\
            .where(SensorData.upload_id == upload_id)\
            .where(SensorData.sensor_type == "TH02H")
    data_humd = db.scalar(st)
    assert data_humd.sensor_name == "TH02_TEST_21"
    assert data_humd.sensor_type == "TH02H"

