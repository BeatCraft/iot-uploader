import os
import uuid
import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from iotuploader.uploader import app as uploader_app
from iotuploader.tools import app as tools_app
from iotuploader.models import Upload, Image, ReadingSetting
from iotuploader.storage import Storage

uploader_client = TestClient(uploader_app)
tools_client = TestClient(tools_app)

def test_update_wifc(db, settings):
    camera_id = f"test-{uuid.uuid4()}"
    auth = (settings.tools_user, settings.tools_pass)

    with open("tests/gas.jpg", "rb") as fp:
        img_data = fp.read()

    res = uploader_client.post(f"/upload/images/{camera_id}?n=GS01_TEST_04", content=img_data)
    assert res.status_code == 201
    upload_id = int(res.text)

    st = select(Image).where(Image.upload_id == upload_id)
    image = db.scalar(st)

    # read reading_setting
    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    rs1 = db.scalar(st)
    # default setting
    assert rs1.num_rects == 8
    assert rs1.wifc[:8] != "0,0,0,0,"

    # update wifc
    rs2_dict = rs1.to_dict()
    rs2_dict["wifc"] = "0,0,0,0," + rs1.wifc[8:]
    rs2_dict["as_default"] = True
    res = tools_client.post(f"/tools/readingsetting?image_id={image.id}", json=rs2_dict, auth=auth)
    assert res.status_code == 200

    # read reading_setting
    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    rs2 = db.scalar(st)
    assert rs2.num_rects == 8
    assert rs2.wifc[:8] == "0,0,0,0,"

    # update except wifc
    rs3_dict = rs2.to_dict()
    rs3_dict["num_rects"] = 7
    del rs3_dict["wifc"]
    res = tools_client.post(f"/tools/readingsetting?image_id={image.id}", json=rs3_dict, auth=auth)
    assert res.status_code == 200

    # read reading_setting
    st = select(ReadingSetting).where(ReadingSetting.id == image.reading_setting_id)
    rs3 = db.scalar(st)
    assert rs3.num_rects == 7
    assert rs3.wifc[:8] == "0,0,0,0,"


