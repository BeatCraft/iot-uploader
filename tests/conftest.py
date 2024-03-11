import sys
sys.path.append("/opt/iotuploader/src/iot-uploader")

from dotenv import load_dotenv
load_dotenv("/opt/iotuploader/.iotenv")

import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from iotuploader.config import get_settings
from iotuploader.uploader import app as uploader_app
from iotuploader.tools import app as tools_app
from iotuploader.database import get_db


class TestSession(Session):
    def commit(self):
        self.flush()
        self.expire_all()


@pytest.fixture(scope="function")
def settings():
    return get_settings()


@pytest.fixture(scope="function")
def db(settings):
    engine = create_engine(settings.db_url, pool_pre_ping=True)
    TestSessionLocal = scoped_session(
        sessionmaker(
            class_=TestSession,
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )

    with TestSessionLocal() as session:
        def get_test_db():
            try:
                yield session
            except:
                session.rollback()

        uploader_app.dependency_overrides[get_db] = get_test_db
        tools_app.dependency_overrides[get_db] = get_test_db

        yield session

        session.rollback()

