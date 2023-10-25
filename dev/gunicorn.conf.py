import multiprocessing
import os

bind = "0.0.0.0:8001"
workers =2
worker_class = "uvicorn.workers.UvicornWorker"

accesslog = "/opt/iotuploader/log/dev_access.log"
errorlog = "/opt/iotuploader/log/dev_error.log"
loglevel = "debug"


