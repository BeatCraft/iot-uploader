from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Text, TIMESTAMP, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base, engine


class UploadSensorData(Base):
    __tablename__ = "upload_sensor_data"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True);
    remote_addr = Column(Text);
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "remote_addr": self.remote_addr,
            "timestamp": self.timestamp,
        }


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("upload_sensor_data.id"))
    sensor_type = Column(Text)
    sensor_name = Column(Text)
    data = Column(Float)
    note = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "upload_id": self.upload_id,
            "sensor_type": self.sensor_type,
            "sensor_name": self.sensor_name,
            "data": self.data,
            "note": self.note,
            "timestamp": str(self.timestamp),
        }


class UploadImage(Base):
    __tablename__ = "upload_images"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    camera_id = Column(Text)
    sensor_type = Column(Text)
    sensor_name = Column(Text)
    name = Column(Text)
    file = Column(Text)
    overlay_file = Column(Text)
    reading_setting_id = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "sensor_type": self.sensor_type,
            "sensor_name": self.sensor_name,
            "name": self.name,
            "file": self.file,
            "overlay_file": self.overlay_file,
            "reading_setting_id": self.reading_setting_id,
            "timestamp": str(self.timestamp),
        }


class ImageSensorData(Base):
    __tablename__ = "image_sensor_data"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    upload_image_id = Column(Integer, ForeignKey("upload_images.id"))
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "upload_image_id": self.upload_image_id,
            "sensor_data_id": self.sensor_data_id,
        }


class ReadingSetting(Base):
    __tablename__ = "reading_settings"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    camera_id = Column(Text)
    sensor_type = Column(Text)
    rect = Column(Text)
    wifc = Column(Text)
    not_read = Column(Boolean)
    labeled = Column(Boolean)
    center_x = Column(Integer)
    center_y = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "sensor_type": self.sensor_type,
            "rect": self.rect,
            "wifc": self.wifc,
            "not_read": self.not_read,
            "labeled": self.labeled,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "timestamp": str(self.timestamp),
        }


def create_tables():
    Base.metadata.create_all(bind=engine)

