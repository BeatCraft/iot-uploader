import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

accesslog = "/home/iotuploader/log/access.log"
errorlog = "/home/iotuploader/log/error.log"
loglevel = "info"


