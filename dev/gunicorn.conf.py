import multiprocessing
import os

bind = "0.0.0.0:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

accesslog = "/home/iotuploader/log/dev_access.log"
errorlog = "/home/iotuploader/log/dev_error.log"
loglevel = "debug"


