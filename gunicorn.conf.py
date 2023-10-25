import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2
worker_class = "uvicorn.workers.UvicornWorker"

pidfile = "/opt/iotuploader/run/iotuploader.pid"
accesslog = "/opt/iotuploader/log/access.log"
errorlog = "/opt/iotuploader/log/error.log"
loglevel = "info"


