import sys
sys.path.append("/opt/iotuploader/src/iot-uploader")

from dotenv import load_dotenv
load_dotenv("/opt/iotuploader/.iotenv")

from iotuploader.models import create_tables


create_tables()

