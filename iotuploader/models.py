from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base, engine


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True);
    sensor_type = Column(Text);
    sensor_name = Column(Text);
    
    data_i0 = Column(Integer);
    data_i1 = Column(Integer);
    data_i2 = Column(Integer);
    data_i3 = Column(Integer);
    data_i4 = Column(Integer);
    data_i5 = Column(Integer);
    data_i6 = Column(Integer);
    data_i7 = Column(Integer);
    data_i8 = Column(Integer);
    data_i9 = Column(Integer);

    data_f0 = Column(Float);
    data_f1 = Column(Float);
    data_f2 = Column(Float);
    data_f3 = Column(Float);
    data_f4 = Column(Float);
    data_f5 = Column(Float);
    data_f6 = Column(Float);
    data_f7 = Column(Float);
    data_f8 = Column(Float);
    data_f9 = Column(Float);

    data_t0 = Column(Text);
    data_t1 = Column(Text);
    data_t2 = Column(Text);
    data_t3 = Column(Text);
    data_t4 = Column(Text);
    data_t5 = Column(Text);
    data_t6 = Column(Text);
    data_t7 = Column(Text);
    data_t8 = Column(Text);
    data_t9 = Column(Text);
    
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now());


class UploadImage(Base):
    __tablename__ = "upload_images"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    device_id = Column(String(32), index=True)
    name = Column(Text)
    path = Column(Text)
    thumbnail_path = Column(Text)
    size = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now());


def create_tables():
    Base.metadata.create_all(bind=engine)

