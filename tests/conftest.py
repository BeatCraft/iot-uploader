import sys
sys.path.append("/opt/iotuploader/src/iot-uploader")

import pytest

from iotuploader.database import SessionLocal

@pytest.fixture()
def db():
    with SessionLocal() as session:
        yield session

