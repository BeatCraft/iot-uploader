from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Text, TIMESTAMP, Float, Boolean, Date, Double
from sqlalchemy.types import BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import LONGTEXT

from .database import Base, engine


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True);
    remote_addr = Column(Text);
    data_type = Column(Integer);
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "remote_addr": self.remote_addr,
            "data_type": self.data_type,
            "timestamp": self.timestamp,
        }


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    sensor_name = Column(Text)
    sensor_type = Column(Text)
    factory = Column(Text)
    building = Column(Text)
    equipment = Column(Text)
    mac_address = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_name": self.sensor_name,
            "sensor_type": self.sensor_type,
            "factory": self.factory,
            "building": self.building,
            "equipment": self.equipment,
            "mac_address": self.mac_address,
            "timestamp": str(self.timestamp),
        }

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)
    upload_id = Column(BigInteger, ForeignKey("uploads.id"))
    sensor_name = Column(Text)
    sensor_type = Column(Text)
    data = Column(Double)
    note = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "upload_id": self.upload_id,
            "sensor_name": self.sensor_name,
            "sensor_type": self.sensor_type,
            "data": self.data,
            "note": self.note,
            "timestamp": str(self.timestamp),
        }


class Image(Base):
    __tablename__ = "images"

    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)
    upload_id = Column(BigInteger, ForeignKey("uploads.id"))
    camera_id = Column(Text)
    sensor_name = Column(Text)
    name = Column(Text)
    file = Column(Text)
    overlay_file = Column(Text)
    reading_setting_id = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "upload_id": self.upload_id,
            "camera_id": self.camera_id,
            "sensor_name": self.sensor_name,
            "name": self.name,
            "file": self.file,
            "overlay_file": self.overlay_file,
            "reading_setting_id": self.reading_setting_id,
            "timestamp": str(self.timestamp),
        }


class ReadingSetting(Base):
    __tablename__ = "reading_settings"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    camera_id = Column(Text)
    sensor_name = Column(Text)
    rect = Column(Text)
    wifc = Column(LONGTEXT)
    not_read = Column(Boolean)
    labeled = Column(Boolean)
    range_x = Column(Integer)
    range_y = Column(Integer)
    range_w = Column(Integer)
    range_h = Column(Integer)
    rotation_angle = Column(Float)
    num_rects = Column(Integer)
    max_brightness = Column(Float)
    min_brightness = Column(Float)
    max_contrast = Column(Float)
    min_contrast = Column(Float)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "sensor_name": self.sensor_name,
            "rect": self.rect,
            "wifc": self.wifc,
            "not_read": self.not_read,
            "labeled": self.labeled,
            "range_x": self.range_x,
            "range_y": self.range_y,
            "range_w": self.range_w,
            "range_h": self.range_h,
            "rotation_angle": self.rotation_angle,
            "num_rects": self.num_rects,
            "max_brightness": self.max_brightness,
            "min_brightness": self.min_brightness,
            "max_contrast": self.max_contrast,
            "min_contrast": self.min_contrast,
            "timestamp": str(self.timestamp),
        }


class ElParameter(Base):
    __tablename__ = "el_parameters"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    sensor_name = Column(Text)
    phase = Column(Integer)
    current_ratio = Column(Float)
    voltage = Column(Float)
    max_current = Column(Float)
    power_factor = Column(Float)
    coefficient = Column(Float)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_name": self.sensor_name,
            "phase": self.phase,
            "current_ratio": self.current_ratio,
            "voltage": self.voltage,
            "max_current": self.max_current,
            "power_factor": self.power_factor,
            "coefficient": self.coefficient,
            "timestamp": str(self.timestamp),
        }


class ElCalculation(Base):
    __tablename__ = "el_calculations"

    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)
    parameter_id = Column(Integer, ForeignKey("el_parameters.id"))
    original_data = Column(BigInteger, ForeignKey("sensor_data.id"))
    calculated_data = Column(BigInteger, ForeignKey("sensor_data.id"))
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "parameter_id": self.parameter_id,
            "original_data": self.original_data,
            "calculated_data": self.calculated_data,
            "timestamp": str(self.timestamp),
        }


class UploadCount(Base):
    __tablename__ = "upload_counts"

    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)
    sensor_name = Column(Text)
    date = Column(Date)
    hour = Column(Integer)
    count = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_name": self.sensor_name,
            "date": str(self.date),
            "hour": self.hour,
            "count": self.count,
            "timestamp": str(self.timestamp),
        }


class DefaultReadingSetting(Base):
    __tablename__ = "default_reading_settings"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    camera_id = Column(Text)
    sensor_name = Column(Text)
    reading_setting_id = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "sensor_name": self.sensor_name,
            "reading_setting_id": self.reading_setting_id,
            "timestamp": str(self.timestamp),
        }


def create_tables():
    Base.metadata.create_all(bind=engine)

