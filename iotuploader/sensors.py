import csv
import datetime
import logging
import sys

from sqlalchemy import select

from .models import Sensor, ElParameter
from .database import SessionLocal

logger = logging.getLogger("gunicorn.error")


def save_el_parameter(db, sensor, row):
    phase = 0
    if row[8][:2] == "単相":
        phase = 1
    elif row[8][:2] == "3相":
        phase = 2

    current_ratio = 0
    if sensor.sensor_type == "EP01":
        current_ratio = 2000
    elif sensor.sensor_type == "EP02":
        current_ratio = 2000
    elif sensor.sensor_type == "EP03":
        current_ratio = 800

    param = ElParameter(
        sensor_name = sensor.sensor_name,
        phase = phase,
        current_ratio = current_ratio,
        voltage = row[7].split("(")[1][:-1],
        max_current = row[8][2:][:-1],
        power_factor = 0.8,
        coefficient = 1,
        timestamp = sensor.timestamp
    )
    db.add(param)
    db.flush()

    logger.info(f"insert el_parameter {param.id}")


def import_sensors_csv(db, csv_file):
    timestamp = datetime.datetime.now()
    reader = csv.reader(csv_file)

    next(reader)
    next(reader)
    next(reader)

    for row in reader:
        sensor = db.scalar(select(Sensor).where(Sensor.sensor_name == row[5]))

        if sensor:
            sensor.sensor_type = row[7].split("(")[0]
            sensor.factory = row[1],
            sensor.building = row[2],
            sensor.equipment = row[4],
            sensor.timestamp = timestamp
            logger.info(f"update sensor {sensor.sensor_name} {sensor.sensor_type}")
        else:
            sensor = Sensor(
                sensor_name = row[5],
                sensor_type = row[7].split("(")[0],
                factory = row[1],
                building = row[2],
                equipment = row[4],
                timestamp = timestamp
            )
            db.add(sensor)
            db.flush()
            logger.info(f"insert sensor {sensor.sensor_name} {sensor.sensor_type}")

        if sensor.sensor_type in ["EP01", "EP02", "EP03"]:
            save_el_parameter(db, sensor, row)

    db.commit()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(message)s')

    db = SessionLocal()
    with open(sys.argv[1]) as fp:
        import_sensors_csv(db, fp)

