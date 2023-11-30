import logging

from sqlalchemy import select

from .models import SensorData, ElParameter

logger = logging.getLogger("gunicorn.error")


def calculate(db, sensor_data):
    st = select(ElParameter)\
            .where(ElParameter.sensor_name == sensor_data.sensor_name)\
            .order_by(ElParameter.id.desc())
    param = db.scalars(st).first()
    if not param:
        logger.error(f"not found ElParameter {sensor_data.sensor_name}")
        return None
    
    # dummy calc
    calc_data = sensor_data.data\
            * param.current_ratio * param.voltage\
            * param.power_factor * param.coefficient

    logger.debug(f"{sensor_data.sensor_type} {sensor_data.sensor_name} calc {calc_data} param {param.id}")

    new_data = SensorData(
        upload_id = sensor_data.upload_id,
        sensor_name = sensor_data.sensor_name,
        sensor_type = sensor_data.sensor_type + "C",
        data = calc_data,
        note = "",
        timestamp = sensor_data.timestamp
    )

    db.add(new_data)

    return new_data

