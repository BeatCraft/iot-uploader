import logging
import datetime

from sqlalchemy import select

from .models import SensorData, ElParameter, ElCalculation

logger = logging.getLogger("gunicorn.error")


def calculate(db, sensor_data):
    st = select(ElParameter)\
            .where(ElParameter.sensor_name == sensor_data.sensor_name)\
            .order_by(ElParameter.id.desc())\
            .limit(1)
    param = db.scalars(st).first()
    if not param:
        logger.error(f"not found ElParameter {sensor_data.sensor_name}")
        return None

    # ADC測定電圧
    ea = float(sensor_data.data)
    # リファレンス電圧
    eref = 3.4
    # ADC測定上限
    eamax = 0x7FFFFF
    # アンプ倍率
    amp = 5.0

    # RMS-DC出力電圧
    er = eref * ea / eamax / amp

    # シャント抵抗値
    rs = 3.0
    # シャント抵抗の電流
    ir = er / rs

    # 変流比
    n = param.current_ratio
    # 結合係数
    k = param.coefficient
    # 対象の電流
    i = ir * n / k

    # 力率
    f = param.power_factor
    # 対象の電圧
    e = param.voltage

    # 対象の有効消費電力
    p = i * e * f

    logger.debug(f"{sensor_data.sensor_type} {sensor_data.sensor_name} orig {sensor_data.data} calc {p} param {param.id}")

    calc_data = SensorData(
        upload_id = sensor_data.upload_id,
        sensor_name = sensor_data.sensor_name,
        sensor_type = sensor_data.sensor_type + "C",
        data = p,
        note = "",
        timestamp = sensor_data.timestamp
    )
    db.add(calc_data)
    db.flush()

    calc = ElCalculation(
        parameter_id = param.id,
        original_data = sensor_data.id,
        calculated_data = calc_data.id,
        timestamp = datetime.datetime.now()
    )
    db.add(calc)

    return calc_data

