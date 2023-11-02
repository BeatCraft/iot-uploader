from fastapi.testclient import TestClient
from sqlalchemy import select

from iotuploader.main import app
from iotuploader.models import SensorData

client = TestClient(app)

def test_upload_sensordata(db):
    res = client.get("/sensordata/upload?t=TEST01&n=test01test&i3=33&f0=55.5&t0=ignore&t9=last")
    assert res.status_code == 200
    data_id = int(res.text)

    st = select(SensorData).where(SensorData.id == data_id)
    data = db.scalar(st)
    assert data.sensor_type == "TEST01"
    assert data.sensor_name == "test01test"
    assert data.data_i0 is None
    assert data.data_i1 is None
    assert data.data_i2 is None
    assert data.data_i3 == 33
    assert data.data_i4 is None
    assert data.data_i5 is None
    assert data.data_i6 is None
    assert data.data_i7 is None
    assert data.data_i8 is None
    assert data.data_i9 is None
    assert data.data_f0 == 55.5
    assert data.data_f1 is None
    assert data.data_f2 is None
    assert data.data_f3 is None
    assert data.data_f4 is None
    assert data.data_f5 is None
    assert data.data_f6 is None
    assert data.data_f7 is None
    assert data.data_f8 is None
    assert data.data_f9 is None
    assert data.data_t0 == "test01test"
    assert data.data_t1 is None
    assert data.data_t2 is None
    assert data.data_t3 is None
    assert data.data_t4 is None
    assert data.data_t5 is None
    assert data.data_t6 is None
    assert data.data_t7 is None
    assert data.data_t8 is None
    assert data.data_t9 == "last"


def test_upload_image(db):
    with open("tests/meter.jpg", "rb") as fp:
        img_data = fp.read()

    res = client.post("/images/upload/testcamera02", content=img_data)
    assert res.status_code == 200
    data_id = int(res.text)


def test_upload_digital_meter(db):
    with open("tests/meter.jpg", "rb") as fp:
        img_data = fp.read()

    res = client.post("/images/upload/testcamera02?t=TH02&n=testmeter02", content=img_data)
    assert res.status_code == 200
    data_id = int(res.text)


