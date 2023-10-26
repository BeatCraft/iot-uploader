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


    def to_dict(self):
        result = {
            "id": self.id,
            "sensor_type": self.sensor_type,
            "sensor_name": self.sensor_name,
            "timestamp": str(self.timestamp),
        }

        if self.data_i0 is not None:
            result["data_i0"] = self.data_i0
        if self.data_i1 is not None:
            result["data_i1"] = self.data_i1
        if self.data_i2 is not None:
            result["data_i2"] = self.data_i2
        if self.data_i3 is not None:
            result["data_i3"] = self.data_i3
        if self.data_i4 is not None:
            result["data_i4"] = self.data_i4
        if self.data_i5 is not None:
            result["data_i5"] = self.data_i5
        if self.data_i6 is not None:
            result["data_i6"] = self.data_i6
        if self.data_i7 is not None:
            result["data_i7"] = self.data_i7
        if self.data_i8 is not None:
            result["data_i8"] = self.data_i8
        if self.data_i9 is not None:
            result["data_i9"] = self.data_i9

        if self.data_f0 is not None:
            result["data_f0"] = self.data_f0
        if self.data_f1 is not None:
            result["data_f1"] = self.data_f1
        if self.data_f2 is not None:
            result["data_f2"] = self.data_f2
        if self.data_f3 is not None:
            result["data_f3"] = self.data_f3
        if self.data_f4 is not None:
            result["data_f4"] = self.data_f4
        if self.data_f5 is not None:
            result["data_f5"] = self.data_f5
        if self.data_f6 is not None:
            result["data_f6"] = self.data_f6
        if self.data_f7 is not None:
            result["data_f7"] = self.data_f7
        if self.data_f8 is not None:
            result["data_f8"] = self.data_f8
        if self.data_f9 is not None:
            result["data_f9"] = self.data_f9

        if self.data_t0 is not None:
            result["data_t0"] = self.data_t0
        if self.data_t1 is not None:
            result["data_t1"] = self.data_t1
        if self.data_t2 is not None:
            result["data_t2"] = self.data_t2
        if self.data_t3 is not None:
            result["data_t3"] = self.data_t3
        if self.data_t4 is not None:
            result["data_t4"] = self.data_t4
        if self.data_t5 is not None:
            result["data_t5"] = self.data_t5
        if self.data_t6 is not None:
            result["data_t6"] = self.data_t6
        if self.data_t7 is not None:
            result["data_t7"] = self.data_t7
        if self.data_t8 is not None:
            result["data_t8"] = self.data_t8
        if self.data_t9 is not None:
            result["data_t9"] = self.data_t9

        return result


class UploadImage(Base):
    __tablename__ = "upload_images"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    device_id = Column(String(32), index=True)
    name = Column(Text)
    path = Column(Text)
    thumbnail_path = Column(Text)
    size = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now());

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "path": self.path,
            "thumbnail_path": self.thumbnail_path,
            "size": self.size,
            "timestamp": str(self.timestamp),
        }


def create_tables():
    Base.metadata.create_all(bind=engine)

