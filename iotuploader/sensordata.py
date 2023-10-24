import datetime
import os
import sys

from fastapi import Request, Depends, APIRouter, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import get_settings
from .models import SensorData
from .database import get_db

settings = get_settings()

router = APIRouter()
templates = Jinja2Templates(directory=settings.templates_dir)


@router.get("/sensordata/upload", status_code=200)
def sensordata_upload(
        req: Request,
        t: str = None, n: str = None,
        i0: int = None, i1: int = None, i2: int = None, i3: int = None,
        i4: int = None, i5: int = None, i6: int = None, i7: int = None,
        i8: int = None, i9: int = None,
        f0: float = None, f1: float = None, f2: float = None, f3: float = None,
        f4: float = None, f5: float = None, f6: float = None, f7: float = None,
        f8: float = None, f9: float = None,
        t0: str = None, t1: str = None, t2: str = None, t3: str = None,
        t4: str = None, t5: str = None, t6: str = None, t7: str = None,
        t8: str = None, t9: str = None,
        db: Session = Depends(get_db)):

    data = SensorData(
        sensor_type = t, sensor_name = n,
        data_i0 = i0, data_i1 = i1, data_i2 = i2, data_i3 = i3, data_i4 = i4,
        data_i5 = i5, data_i6 = i6, data_i7 = i7, data_i8 = i8, data_i9 = i9,
        data_f0 = f0, data_f1 = f1, data_f2 = f2, data_f3 = f3, data_f4 = f4,
        data_f5 = f5, data_f6 = f6, data_f7 = f7, data_f8 = f8, data_f9 = f9,
        data_t0 = n,  data_t1 = t1, data_t2 = t2, data_t3 = t3, data_t4 = t4,
        data_t5 = t5, data_t6 = t6, data_t7 = t7, data_t8 = t8, data_t9 = t9,
        timestamp = datetime.datetime.now()
    )

    db.add(data)
    db.commit()

    return data.id

