from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = ""
    templates_dir: str = "/opt/iotuploader/src/iot-uploader/templates"
    static_dir: str = "/opt/iotuploader/src/iot-uploader/static"
    data_dir: str = "/opt/iotuploader/data"
    font_path: str = "/opt/iotuploader/src/iot-uploader/fonts/NotoSansJP-Regular.ttf"
    font_size: int = 28
    tools_user: str = ""
    tools_pass: str = ""
    enable_raw_data: bool = False


@lru_cache()
def get_settings():
    return Settings()

